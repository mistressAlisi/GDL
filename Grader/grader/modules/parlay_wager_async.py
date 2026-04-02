from decimal import Decimal
from types import SimpleNamespace

from asgiref.sync import sync_to_async
from celery.worker.state import total_count
from django.db import transaction, connections
from django.forms import model_to_dict
from django.utils.timezone import now

import wager
from account.models import Account
from grader.daemon.const import GRADER_MATCH_FINISHED_STATUS_SHORT
from grader.modules.abcasync import GraderModuleABCAsync
from grader.modules.straight_wager_async import StraightWagerGraderAsync
from grader.toolkit.parlays import parlay_decimal_odds, american_juicer, american_juicer_v2
from cashier.models import ParlayPayoutRulesetEntry, AccountLevels, ParlayPayoutRuleset
from matches.models import Match
from matches.toolkit.scorer import get_final_match_scores
from odds.models import MatchOddsSummary
from grader.modules.abc import GraderModuleABC

from grader.modules.straight_wager import StraightWagerGrader
class ParlayWagerGraderAsync(GraderModuleABCAsync):

    def __init__(self, vhost,**kwargs):
        GraderModuleABCAsync.__init__(self, vhost, **kwargs)
        self.vhost = vhost
        if "logger" in kwargs:
            self.logger = kwargs["logger"]
        self.straight_grader = StraightWagerGraderAsync(self.vhost,logger=self.logger)
        self.straight_grader_sync = StraightWagerGrader(self.vhost,logger=self.logger)

    async def _close_wager_func(self, wagerObj, **kwargs):
        """
        Close and grade a parlay wager inside a single DB transaction / connection.
        """

        @sync_to_async(thread_sensitive=True)
        def _orm_block():
            with transaction.atomic(using="default"):
                wager = SimpleNamespace(**model_to_dict(wagerObj))
                self.logger.info(f"Qualifying Parlay Wager: {wager.uuid}...")

                nodes = self._find_parlay_nodes_sync(wagerObj)

                # --- Counters ---
                original_matches = len(nodes)
                total_wins = total_losses = total_draws = 0
                finished_nodes = 0
                recompute_nodes = []
                void_nodes = []

                root_wager = nodes[0]
                root_wager_data = SimpleNamespace(**model_to_dict(root_wager))

                # --- Resolve ruleset ---
                account = Account.objects.using("default").get(uuid=root_wager_data.account)
                if account.parlay_rules:
                    ruleset = account.parlay_rules
                elif account.account_level:
                    ruleset = account.account_level.parlay_ruleset
                else:
                    ruleset = None

                if not ruleset:
                    self.logger.warning(
                        f"For wager {root_wager_data.uuid} - no ruleset found. Can't qualify."
                    )
                    return None

                # --- Tally legs ---
                for node in nodes:
                    match = Match.objects.using("default").get(uuid=node.match.uuid)
                    match_data = SimpleNamespace(**model_to_dict(match))

                    if not match_data.finished:
                        self.logger.info(
                            f"Node {node.uuid} not finished (Match {match.uuid})."
                        )
                        continue

                    if match_data.status_short in [
                        "PP", "SUSP", "RDELAY", "DELAY", "CANC",
                        "Cancelled", "NS", "Walk Over", "PPD", "Postponed"
                    ]:
                        recompute_nodes.append(node)
                        if match_data.status_short in ["PPD", "CANC"]:
                            void_nodes.append(node)
                        continue

                    # Ensure grading
                    if node.status not in ["W", "L", "D"]:
                        self.straight_grader_sync._grade_wager_func(node, match, **kwargs)

                    if node.status == "W":
                        total_wins += 1
                    elif node.status == "L":
                        total_losses += 1
                    elif node.status == "D":
                        total_draws += 1

                    finished_nodes += 1

                # --- Effective matches (after voids) ---
                total_matches = original_matches - len(void_nodes)

                # --- Qualification ---
                active_rules = ParlayPayoutRulesetEntry.objects.using("default").filter(
                    ruleset=ruleset,
                    parlay_legs=total_matches,
                )

                if not active_rules.exists():
                    self.logger.warning(
                        f"No active rules for {wager.uuid}, Matches: {total_matches}"
                    )
                    return None

                if finished_nodes < total_matches:
                    self.logger.info(
                        f"{root_wager_data.uuid}: Not yet ready to close - "
                        f"Total Matches: {total_matches} | "
                        f"Finished: {finished_nodes} | "
                        f"Wins: {total_wins} | "
                        f"Losses: {total_losses} | "
                        f"Recompute: {len(recompute_nodes)}"
                    )
                    return None

                # --- Full win ---
                if total_wins == total_matches and total_losses == 0 and not recompute_nodes:
                    root_wager.grade_outcome = "W"
                    root_wager.graded = True
                    root_wager.graded_at = now()
                    root_wager.grader_history.update({"node_wagers_won": True})
                    root_wager.save(using="default")

                    for node in nodes:
                        node.parlay_closed = True
                        node.grade_outcome = "W"
                        node.graded = True
                        node.graded_at = now()
                        node.save(using="default")

                    from wager.signals import signal_wager_qualified
                    signal_wager_qualified.send(
                        sender=self.__class__,
                        wagerObj=root_wager,
                        account=root_wager.account,
                        vhost=root_wager.vhost,
                    )
                    return True

                # --- Loss / partial ---
                try:
                    rule = ParlayPayoutRulesetEntry.objects.using("default").get(
                        max_losses=total_losses,
                        ruleset=ruleset,
                        parlay_legs=total_matches,
                    )
                except ParlayPayoutRulesetEntry.DoesNotExist:
                    root_wager.grade_outcome = "L"
                    root_wager.graded = True
                    root_wager.grader_history.update({"node_wagers_lost": True})
                    root_wager.save(using="default")

                    for node in nodes:
                        node.grade_outcome = "L"
                        node.parlay_closed = True
                        node.graded = True
                        node.graded_at = now()
                        node.save(using="default")

                    from wager.signals import signal_wager_qualified
                    signal_wager_qualified.send(
                        sender=self.__class__,
                        wagerObj=root_wager,
                        account=root_wager.account,
                        vhost=root_wager.vhost,
                    )
                    return False

                # --- Dynamic payout ---
                final_odds = []
                if not "outcome_meta" in root_wager.bet_data:
                    self.logger.warning(f"Wager {root_wager.uuid} does not have bet outcome metadata. Closing and marking as cancelled.")
                    for node in nodes:
                        node.status = "C"
                        node.graded = True
                        node.save(using="default")
                    return False
                outcomes = root_wager.bet_data["outcome_meta"]

                for node in nodes:
                    if node.status == "W":
                        final_odds.append(
                            float(outcomes[str(node.match.uuid)]["odds"])
                        )

                final_parlay_odds = 1
                for odd in final_odds:
                    final_parlay_odds *= odd

                final_payout = round(
                    Decimal(root_wager.risk)
                    * Decimal(final_parlay_odds)
                    * Decimal(rule.players_percentage / 100),
                    2,
                )

                root_wager.win = final_payout
                root_wager.partial_payout = True
                root_wager.grade_outcome = "W"
                root_wager.status = "W"
                root_wager.graded = True
                root_wager.graded_at = now()
                root_wager.grader_history.update({
                    "recalculated": True,
                    "final_parlay_odds": float(final_parlay_odds),
                    "total_matches": total_matches,
                    "total_losses": total_losses,
                    "total_wins": total_wins,
                    "ju_pct": rule.juice_percentage,
                    "eap_pct": rule.players_percentage,
                    "original_win": float(wager.win),
                    "outcomes": outcomes,
                })
                root_wager.save(using="default")

                for node in nodes:
                    node.parlay_closed = True
                    node.grade_outcome = "W"
                    node.graded = True
                    node.save(using="default")

                from wager.signals import signal_wager_qualified
                signal_wager_qualified.send(
                    sender=self.__class__,
                    wagerObj=root_wager,
                )

                return True

        return await _orm_block()

    async def _grade_wager_func(self, wagerObj, **kwargs):
        # if not self._check_wager_stat(wagerObj):
        #     return False
        wager_data = await sync_to_async(lambda:SimpleNamespace(**model_to_dict(wagerObj)),thread_sensitive=False)()
        self.logger.info(f"Qualifying Parlay Wager: {wager_data.uuid}...")
        nodes = await self._find_parlay_nodes(wagerObj)
        total_matches = len(nodes)
        total_losses = 0
        total_wins = 0
        total_draws = 0
        total_complete = 0
        not_complete = 0
        root_wager = nodes[0]
        recompute = []
        ruleset = False
        root_wager_data = await sync_to_async(lambda:SimpleNamespace(**model_to_dict(root_wager)),thread_sensitive=False)()
        if not root_wager_data.parlay_ruleset:
            # print("a")
            account_data = await sync_to_async(lambda:SimpleNamespace(**model_to_dict(Account.objects.get(uuid=root_wager_data.account))),thread_sensitive=False)()
            if account_data.parlay_rules:
                # print("b")
                pruuid = await sync_to_async(lambda:account_data.parlay_rules.uuid,thread_sensitive=False)()
                ruleset = await sync_to_async(lambda:ParlayPayoutRuleset.objects.get(uuid=pruuid),thread_sensitive=False)()
            elif account_data.account_level:
                # print("c")
                accountLevel = await sync_to_async(lambda:AccountLevels.objects.get(uuid=account_data.account_level),thread_sensitive=False)()
                ruuid = await sync_to_async(lambda:accountLevel.parlay_ruleset.uuid,thread_sensitive=False)()
                # print(f"d {ruuid}")
                ruleset = await sync_to_async(lambda:ParlayPayoutRuleset.objects.get(uuid=ruuid),thread_sensitive=False)()
                # print(f"Ruuid: {ruuid}")
        else:

            ruleset = await sync_to_async(lambda:ParlayPayoutRuleset.objects.get(uuid=root_wager.parlay_ruleset),thread_sensitive=False)()
        # print("rwd")
        if not ruleset:

            self.logger.warning(f"For wager {root_wager_data.uuid} - no ruleset found. Can't qualify.")
            return None
        # print(ruleset)
        # print("rwa")
        for node in nodes:
            # if not self._check_wager_stat(node):
            #     return False
            # Match must be finished...
            status_short = await sync_to_async(lambda:node.match.status_short,thread_sensitive=False)()
            node_status = await sync_to_async(lambda:node.status,thread_sensitive=False)()
            if status_short in ["PP","SUSP","RDELAY","DELAY","CANC","PPD"]:
                # ... and not in a special delayed state, which would involve recomputation:
                recompute.append(node)

            if not status_short in GRADER_MATCH_FINISHED_STATUS_SHORT:
                nuuid = await sync_to_async(lambda:node.uuid,thread_sensitive=False)()
                muuid = await sync_to_async(lambda:node.match.uuid,thread_sensitive=False)()
                self.logger.info(f"For Parlay Node {nuuid}; Match is not yet finished. Not qualifying [Match: {muuid}]. Status is: {status_short}")
                if status_short in ["PP","SUSP","RDELAY","DELAY","CANC","PPD"]:
                    not_complete += 1


            else:

                if node_status not in ["W", "L", "D"]:
                    await self.straight_grader._grade_wager_func(node, **kwargs)
                if node_status == "W":
                    total_wins += 1
                    total_complete += 1
                elif node_status == "L":
                    total_losses += 1
                    total_complete += 1
                elif node_status == "D":
                    total_draws += 1
                    total_complete += 1
        self.logger.info(f"{root_wager_data.uuid}: Total matches: {total_matches}. Total Complete: {total_complete}. Total Wins: {total_wins}. Total Draws: {total_draws}. Total Losses: {total_losses}. Total Not Complete: {not_complete}")
        # print("Here we are")
        return True












GRADER_MODULE=ParlayWagerGraderAsync