import asyncio
import itertools
from dataclasses import dataclass

from asgiref.sync import sync_to_async
from django.db import transaction
from django.http import JsonResponse
from uuid import UUID

from game.gdlfront.models import GDLTicketCartCache
from cashier.engine import Cashier
from licensemanager.models import AvailableApplication
from matches.models import Match, MatchScore
from odds.models import MatchOddsSummary
from outcomes.engine import OutcomesEngine
from outcomes.models import OutcomeTeams
from toolkit.wagers.application_tools import create_application_wager

from wager.models import Wager, MatchWagers
from matches.toolkit.scorer import get_final_match_scores, get_live_match_scores, get_live_match_scores_v2, \
    get_match_consensus_score
from django.core.cache import cache



@dataclass
class TicketPrecheckResult:
    ok: bool
    error: str | None = None

async def   prevalidate_ticket(ticket_data):
    """
    Async-safe ticket validation.
    NO SAVES. NO BALANCE MUTATION.
    """

    try:
        # Structural checks
        if not ticket_data["matches"]:
            return TicketPrecheckResult(False, "Ticket has no matches")

        if not (
            len(ticket_data["matches"])
            == len(ticket_data["lines"])
            == len(ticket_data["types"])
        ):
            return TicketPrecheckResult(False, "Malformed ticket legs")

        if ticket_data["stake"] <= 0:
            return TicketPrecheckResult(False, "Invalid stake")

        # ORM read-only checks
        matches = await sync_to_async(
            lambda: set(
                Match.objects.filter(uuid__in=ticket_data["matches"])
                .values_list("uuid", flat=True)
            ),
            thread_sensitive=True,
        )()

        if len(matches) != len(ticket_data["matches"]):
            return TicketPrecheckResult(False, "One or more matches not found")

        lines = await sync_to_async(
            lambda: set(
                MatchOddsSummary.objects.filter(uuid__in=ticket_data["lines"])
                .values_list("uuid", flat=True)
            ),
            thread_sensitive=True,
        )()

        if len(lines) != len(ticket_data["lines"]):
            return TicketPrecheckResult(False, "One or more odds lines not found")

        # Type validation
        valid_types = {"home", "away", "draw", "home_price", "away_price", "draw_price"}
        for t in ticket_data["types"]:
            if t not in valid_types:
                return TicketPrecheckResult(False, f"Invalid bet type: {t}")

        # Duplicate legs
        if len(set(zip(ticket_data["matches"], ticket_data["lines"]))) != len(ticket_data["matches"]):
            return TicketPrecheckResult(False, "Duplicate match/line detected")

        return TicketPrecheckResult(True)

    except Exception as e:
        return TicketPrecheckResult(False, str(e))

async def prevalidate_all_tickets(ticket_objs):
    tasks = [
        prevalidate_ticket(t.ticket_data)
        for t in ticket_objs
    ]
    return await asyncio.gather(*tasks)

def get_gdl_application():
    app = cache.get("gdl_application")
    if not app:
        app = AvailableApplication.objects.select_related("studio").get(
            slug="gamedaylotto",
            studio__slug="solstic"
        )
        cache.set("gdl_application", app, 3600)
    return app

def _gdl_ticket_leg_factory(vhost, account, current_ip, match, line, bet_type, **kwargs):
    gdl_app = get_gdl_application()

    wager_data = {
        "type": "PA",
        "current_ip": current_ip,
        "gdl_ticket": True,
        "match": match,
        "bet_data": {
            "type": "straight",
            "mode": "parlay",
            "dynamic": True,
            "hierarchy": [str(line.uuid)],
        }
    }

    if account.parlay_rules:
        wager_data["parlay_ruleset"] = account.parlay_rules

    if bet_type in ("home", "home_price"):
        wager_data["team_1"] = match.home_team
    elif bet_type in ("away", "away_price"):
        wager_data["team_1"] = match.away_team
    elif bet_type in ("draw", "draw_price"):
        wager_data["for_draw"] = True
    wager_data["no_metrics"] = True
    wager_data.update(kwargs)

    return create_application_wager(account, gdl_app, vhost, **wager_data)


def create_gdl_ticket(vhost, account, current_ip, ticket_data,use_bonus=False):
    """
    Create a GameDayLotto Ticket.

    Returns:
        (root_wager, nodes, node_uuid_list)
        or (False, None, None) on failure
    """

    cashier = Cashier(account=account, vhost=vhost)

    # -------------------------
    # 1. Basic validation
    # -------------------------
    try:
        stake = ticket_data["stake"]
        returns = ticket_data["returns"]
        match_ids = [str(UUID(u)) for u in ticket_data["matches"]]
        line_ids = [str(UUID(u)) for u in ticket_data["lines"]]
        bet_types = ticket_data["types"]
        outcome_meta = ticket_data.get("outcome_meta")
    except (KeyError, ValueError, TypeError):
        return False, None, None

    if stake > cashier.get_available_balance(use_bonus=use_bonus):
        return False, None, None

    if not (len(match_ids) == len(line_ids) == len(bet_types)):
        return False, None, None

    # -------------------------
    # 2. Bulk load dependencies
    # -------------------------
    matches = {
        str(k): v
        for k, v in Match.objects.in_bulk(match_ids).items()
    }
    lines = {
        str(k): v
        for k, v in MatchOddsSummary.objects.in_bulk(line_ids).items()
    }

    if len(matches) != len(match_ids) or len(lines) != len(line_ids):
        return False, None, None

    # -------------------------
    # 3. Create wager legs
    # -------------------------
    nodes = []
    root_wager = None

    for idx, (mid, lid, bet_type) in enumerate(
        zip(match_ids, line_ids, bet_types)
    ):
        match = matches[mid]
        line = lines[lid]

        if idx == 0:
            root_wager = _gdl_ticket_leg_factory(
                vhost=vhost,
                account=account,
                current_ip=current_ip,
                match=match,
                line=line,
                bet_type=bet_type,
                risk=stake,
                win=returns,
                outcome_meta=outcome_meta,
            )
        else:
            nodes.append(
                _gdl_ticket_leg_factory(
                    vhost=vhost,
                    account=account,
                    current_ip=current_ip,
                    match=match,
                    line=line,
                    bet_type=bet_type,
                    no_metrics=True,
                )
            )

    if root_wager is None:
        return False, None, None

    # -------------------------
    # 4. Root wager metadata
    # -------------------------
    root_wager.bet_data["root_wager"] = True
    root_wager.bet_data["nodes"] = []
    root_wager.risk = stake
    root_wager.win = returns
    root_wager.use_bonus = use_bonus
    root_wager.ruleset = (
        account.parlay_rules
        or account.account_level.parlay_ruleset
        or False
    )

    root_wager.save()
    MatchWagers.objects.get_or_create(
        wager=root_wager,
        match=root_wager.match,
    )

    # -------------------------
    # 5. Attach nodes
    # -------------------------
    node_uuids = []

    for node in nodes:
        node.bet_data["parent"] = str(root_wager.uuid)
        node.hide_in_reports = True
        node.save()

        MatchWagers.objects.get_or_create(
            wager=node,
            match=node.match,
        )

        node_uuids.append(str(node.uuid))

    root_wager.bet_data["nodes"] = node_uuids
    root_wager.save(update_fields=["bet_data"])

    return root_wager, nodes, node_uuids

def get_gdl_ticket(root_wager, serialise=True, add_scores=False):
    wager_ids = [root_wager.uuid]
    for suuid in root_wager.bet_data["nodes"]:
        wager_ids.append(UUID(suuid))
    wagers = (
        Wager.objects
        .select_related("match__sport__group")
        .in_bulk(wager_ids)
    )

    ticket = {
        "uuid": str(root_wager.uuid),
        "matches": [],
        "wagers": [],
        "sports": [],
        "status": root_wager.status,
        "mlen": 0,
        "returns": float(root_wager.win),
        "stake": int(root_wager.risk),
        "payload": str(root_wager.uuid),
        "grade_outcome": root_wager.get_grade_outcome_display(),
    }
    # print(wager_ids)
    # print(wagers)
    for wid in wager_ids:
        wager = wagers[wid]
        match = wager.match

        if add_scores:
            scores = get_live_match_scores_v2(match, False)

        ticket["matches"].append(str(match.uuid) if serialise else match)
        ticket["wagers"].append(
            str(wager.uuid) if serialise else (wager if not add_scores else [wager, *scores])
        )

        ticket["sports"].append(
            [str(match.sport.uuid), match.sport.title, match.sport.group.name, match.sport.group.icon]
            if serialise else match.sport
        )

        ticket["mlen"] += 1

    return ticket


def get_gdl_ticket_matches(root_wager, ncol=5):
    wager_ids = [root_wager.uuid] + root_wager.bet_data["nodes"]

    wagers = (
        Wager.objects
        .select_related("match")
        .in_bulk(wager_ids)
    )

    rows = []
    for wager in wagers.values():
        match = wager.match
        scores = (
            get_match_consensus_score(match)
            if match.final_score_consensus
            else get_live_match_scores_v2(match)
        )
        rows.append([wager, match, scores])

    return list(itertools.batched(rows, ncol))

def _play_app_confirm_tickets_tx(request):
    """
    Synchronous, transactional ticket commit.
    MUST be called via sync_to_async(thread_sensitive=True)
    """

    with transaction.atomic():
        # --- IP ---
        current_ip = request.META.get(
            "HTTP_X_REAL_IP",
            request.META.get("REMOTE_ADDR")
        )


        # --- Check if using bonus ---
        use_bonus = request.POST.get('use_bonus', 'false') == 'true'

        # Lock selected tickets
        ticket_objs = list(
            GDLTicketCartCache.objects
            .select_for_update()
            .filter(
                vhost=request.vhost,
                domain=request.vdomain,
                account=request.account,
                selected=True
            )
        )

        if not ticket_objs:
            return JsonResponse(
                {"res": "err", "err": "No tickets selected"},
                safe=False
            )

        total_stake = sum(t.risk for t in ticket_objs)

        cashier = Cashier(account=request.account, vhost=request.vhost)

        # --- Balance check (authoritative) ---
        avl = cashier.get_available_balance()
        bonus_available = cashier.get_bonus_balance() if use_bonus else 0
        combined_balance = avl + bonus_available

        if total_stake > combined_balance:
            return JsonResponse(
                {
                    "res": "err",
                    "err": f"${total_stake:.2f} exceeds available balance: ${combined_balance:.2f}.",
                    "cashier": True,
                },
                safe=False
            )

        ticket_uuids = []
        remaining_bonus = bonus_available  # Track remaining bonus for this transaction

        # --- Ticket creation ---
        for ticket in ticket_objs:
            max_wager = cashier.get_max_possible_wager(use_bonus=use_bonus)
            if ticket.risk > max_wager:
                return JsonResponse(
                    {
                        "res": "err",
                        "err": f"${ticket.risk:.2f} exceeds max possible wager: ${max_wager:.2f}.",
                    },
                    safe=False
                )

            root, nodes, nuuids = create_gdl_ticket(
                request.vhost,
                request.account,
                current_ip,
                ticket.ticket_data,
                use_bonus=use_bonus,
            )

            if root is False:
                return JsonResponse(
                    {
                        "res": "err",
                        "err": f"${total_stake:.2f} exceeds available balance.",
                        "cashier": True,
                    },
                    safe=False
                )

            # --- Risk reservation (authoritative) ---
            ticket_risk = ticket.risk

            if use_bonus and remaining_bonus > 0:
                # Use bonus first, then available balance
                bonus_portion = min(ticket_risk, remaining_bonus)
                avail_portion = ticket_risk - bonus_portion

                if bonus_portion > 0:
                    success, _ = cashier.use_bonus_for_wager(root, bonus_portion, relations=nuuids)
                    if not success:
                        return JsonResponse(
                            {
                                "res": "err",
                                "err": f"Failed to use bonus balance.",
                                "cashier": True,
                            },
                            safe=False
                        )
                    remaining_bonus -= bonus_portion

                if avail_portion > 0:
                    success, _, _ = cashier.risk_balance(root, amount=avail_portion, relations=nuuids)
                    if not success:
                        return JsonResponse(
                            {
                                "res": "err",
                                "err": f"${total_stake:.2f} exceeds available balance.",
                                "cashier": True,
                            },
                            safe=False
                        )
            else:
                # Standard flow - use available balance only
                success, _, _ = cashier.risk_balance(root, relations=nuuids)
                if not success:
                    return JsonResponse(
                        {
                            "res": "err",
                            "err": f"${total_stake:.2f} exceeds available balance.",
                            "cashier": True,
                        },
                        safe=False
                    )

            ticket_uuids.append(nuuids)

            # Remove from cart
            ticket.delete()

        # --- Final balances ---
        latest_balance = cashier.get_balance()
        latest_bonus = cashier.get_available_bonus()
        pending = cashier.get_at_risk_balance()
        balance = cashier.get_available_balance()+latest_bonus

        # --- Signal ---
        from cashier.signals import signal_balance_wager_created
        signal_balance_wager_created.send(
            sender="GDLPlayApp",
            account=request.account,
            tickets=ticket_uuids
        )

    # Transaction committed here
    return JsonResponse(
        {
            "res": "ok",
            "silent": "true",
            "total_stake": f"{total_stake:.2f}",
            "available": f"{balance:.2f}",
            "bonus": f"{latest_bonus:.2f}",
            "pending": f"{pending:.2f}",
            "balance": f"{latest_balance:.2f}",
        },
        safe=False
    )