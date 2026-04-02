import asyncio, json
from decimal import DivisionByZero, InvalidOperation
from uuid import UUID

from asgiref.sync import sync_to_async
from websockets.exceptions import ConnectionClosed, ConnectionClosedOK

from account.models import Account
from cashier.models import ParlayPayoutRulesetEntry
from grader.toolkit.parlays import american_juicer_v2, american_to_fraction_str
from parameters.models import VHost, VHostDomain
from .protocol import JSONProtocol
from game.gdlcore.algos.gdlgpucore_async import GDLGPUCoreAsync
from django.utils.timezone import now
from odds.models import MatchOddsSummary
from uuid import UUID
from django.utils.timezone import now
import asyncio
import random
from ..models import GDLCoreSportGroupFilters

core = GDLGPUCoreAsync()


class CommandHandler:
    SEM = asyncio.Semaphore(20)

    def __init__(self, websocket):
        self.websocket = websocket
        self.closed = False

    # -------------------------------------------------
    # Safe websocket send
    # -------------------------------------------------
    async def safe_send(self, payload):
        if self.closed:
            return

        try:
            await self.websocket.send(payload)
        except ConnectionClosedOK:
            self.closed = True
        except ConnectionClosed:
            self.closed = True
        except Exception:
            self.closed = True
            raise

    # -------------------------------------------------
    # Odds processing
    # -------------------------------------------------
    async def process_zm(self, zmObj, juice):
        if self.closed:
            return None

        async with self.SEM:
            try:
                hp, ap = american_juicer_v2(
                    zmObj.home_price,
                    zmObj.away_price,
                    juice
                )
                hpf = american_to_fraction_str(hp)
                apf = american_to_fraction_str(ap)
            except (DivisionByZero, InvalidOperation):
                return None

            def _create_and_save():
                obj = MatchOddsSummary(
                    vhost=zmObj.match.vhost,
                    match=zmObj.match,
                    bookmaker=zmObj.bookmaker,
                    driver=zmObj.driver,
                    juice_pct=juice,
                    home_team=zmObj.home_team,
                    away_team=zmObj.away_team,
                    home_price=hp,
                    home_price_fraction=hpf,
                    away_price=ap,
                    away_price_fraction=apf,
                )
                obj.save()
                return obj

            return await sync_to_async(_create_and_save, thread_sensitive=False)()

    # -------------------------------------------------
    # Command router
    # -------------------------------------------------
    async def handle(self, message: dict):
        if self.closed:
            return

        action = message.get("action")
        req_id = message.get("request_id")

        if action == "ping":
            await self.safe_send(
                JSONProtocol.make_response(
                    "pong", req_id, {"time": str(now())}
                )
            )
            return

        if action == "generate":
            await self._handle_generate(
                req_id,
                message.get("filters", {}),
                message.get("settings", {})
            )
            return

        await self.safe_send(
            JSONProtocol.make_response(
                "error", req_id, {"error": f"Unknown action {action}"}
            )
        )

    # -------------------------------------------------
    # Generator handler
    # -------------------------------------------------
    async def _handle_generate(self, req_id, filters, settings):
        if self.closed:
            return



        qstr = {}
        chosen_sports = []
        chosen_groups = []
        groups = []
        sports = []

        # ------------------------------------------------------------
        # Parse dynamic settings
        # ------------------------------------------------------------
        for entry in settings.keys():
            if entry.startswith("sport_"):
                chosen_sports.append(UUID(settings[entry]))
            elif entry.startswith("group_"):
                chosen_groups.append(UUID(settings[entry]))
            elif entry == "sports":
                chosen_groups = settings[entry].split(",")


        # ------------------------------------------------------------
        # Load account + parlay rules
        # ------------------------------------------------------------
        # print("Loading Account")

        accountObj = await sync_to_async(
            lambda: Account.objects.get(
                uuid=settings["account"],
                vhost__uuid=settings["vhost"]
            ),
            thread_sensitive=False
        )()
        await sync_to_async(lambda:print(accountObj),thread_sensitive=False)()
        account_level_parlay_rules = await sync_to_async(
            lambda: accountObj.account_level.parlay_ruleset,
            thread_sensitive=False
        )()

        account_parlay_rules = await sync_to_async(
            lambda: accountObj.parlay_rules,
            thread_sensitive=False
        )()

        if account_level_parlay_rules:
            parlayRuleset = await sync_to_async(
                lambda: ParlayPayoutRulesetEntry.objects
                .filter(
                    ruleset=account_level_parlay_rules,
                    parlay_legs=settings["depth"]
                )
                .order_by("parlay_legs")
                .first(),
                thread_sensitive=False
            )()
        elif account_parlay_rules:
            parlayRuleset = await sync_to_async(
                lambda: ParlayPayoutRulesetEntry.objects
                .filter(
                    ruleset=account_parlay_rules,
                    parlay_legs=settings["depth"]
                )
                .order_by("parlay_legs")
                .first(),
                thread_sensitive=False
            )()
        else:
            raise ValueError("Account does not have a Parlay ruleset set!")

        juice = parlayRuleset.juice_percentage / 100

        # ------------------------------------------------------------
        # Domain / vhost sport + group filters
        # ------------------------------------------------------------
        if "vhost" in settings and "vdomain" in settings:
            vhost = await VHost.objects.aget(uuid=settings["vhost"])
            vdomain = await VHostDomain.objects.aget(
                uuid=settings["vdomain"],
                vhost=vhost
            )
            try:
                filter_chain = await GDLCoreSportGroupFilters.objects.aget(
                    vhost=vhost,
                    domain=vdomain
                )
                groups += await sync_to_async(list)(filter_chain.group_filter.all())
                sports += await sync_to_async(list)(filter_chain.sport_filter.all())
            except GDLCoreSportGroupFilters.DoesNotExist:
                pass

        # ------------------------------------------------------------
        # Build queryset filters
        # ------------------------------------------------------------
        if chosen_sports:
            qstr["match__sport__uuid__in"] = chosen_sports
        elif chosen_groups:
            qstr["match__sport__group__uuid__in"] = chosen_groups
        elif groups:
            qstr["match__sport__group__in"] = groups

        if settings.get("events_within"):
            from django.utils.timezone import now as tznow, timedelta
            cutoff = tznow() + timedelta(seconds=int(settings["events_within"]))
            qstr["match__commence_time__lte"] = cutoff

        qstr["juice_pct"] = juice

        base_filter = dict(
            match__active=True,
            match__open=True,
            match__finished=False,
            match__commence_time__gte=now(),
            home_price__range=(-9499, 2000),
            away_price__range=(-9499, 2000),
            draw_price__range=(-9499, 2000),
        )

        qs = MatchOddsSummary.objects.filter(**base_filter).filter(**qstr)

        aqs = await qs.acount()

        # ------------------------------------------------------------
        # Fallback to zero-juice if needed
        # ------------------------------------------------------------
        if aqs < settings["depth"]:
            qstr["juice_pct"] = 0
            base_qs = MatchOddsSummary.objects.filter(**base_filter).filter(**qstr)

            zaqs = await base_qs.acount()
            if zaqs < settings["depth"]:
                await self.safe_send(
                    JSONProtocol.make_response(
                        "empty",
                        req_id,
                        {"error": "Not enough Odds", "incomplete": True}
                    )
                )
                return

        else:
            base_qs = qs

        # ------------------------------------------------------------
        # ✅ BOUNDED RANDOM SAMPLING (ORDER ONLY)
        # ------------------------------------------------------------
        depth = int(settings["depth"])
        BOUND = max(depth * 10, 500)

        ids = await sync_to_async(
            list,
            thread_sensitive=False
        )(base_qs.values_list("uuid", flat=True)[:BOUND])

        random.shuffle(ids)

        lines_list = await sync_to_async(
            list,
            thread_sensitive=False
        )(MatchOddsSummary.objects.filter(uuid__in=ids))

        # ------------------------------------------------------------
        # Engine settings (strip dynamic keys)
        # ------------------------------------------------------------
        engine_settings = {
            k: v for k, v in settings.items()
            if not k.startswith("sport_") and not k.startswith("group_") and not k.startswith("sports")
        }

        # ------------------------------------------------------------
        # Stream generation (BACKEND CONTROLS COMPLETION)
        # ------------------------------------------------------------
        sent = 0
        print(engine_settings)
        print(len(lines_list))
        try:
            async for item in core.stream_generate(
                    lines_list=lines_list,
                    **engine_settings
            ):
                if self.closed:
                    break

                payload = item.copy()
                frame_type = payload.get("type", "ticket")

                if frame_type == "ticket":
                    sent += 1

                await self.safe_send(
                    JSONProtocol.make_response(
                        frame_type,
                        req_id,
                        payload
                    )
                )

        except ConnectionClosedOK:
            self.closed = True

        except Exception as e:
            if not self.closed:
                await self.safe_send(
                    JSONProtocol.make_response(
                        "error",
                        req_id,
                        {"error": str(e)}
                    )
                )
                return

        # ------------------------------------------------------------
        # FINAL COMPLETE — ONLY AFTER GENERATOR EXHAUSTS
        # ------------------------------------------------------------
        if not self.closed:
            await self.safe_send(
                JSONProtocol.make_response(
                    "complete",
                    req_id,
                    {
                        "sent": sent,
                    }
                )
            )

        # hard EOF so proxy drains cleanly
        if not self.closed:
            try:
                await self.websocket.close()
            except Exception:
                pass