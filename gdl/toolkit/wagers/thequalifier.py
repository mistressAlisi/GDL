import importlib
from decimal import Decimal

import odds.toolkit.markets
from cashier.models import ParlayPayoutRulesetEntry
from grader.toolkit.parlays import  american_juicer, american_to_decimal, parlay_decimal_odds
from matches.models import MatchScore
from odds.models import MatchOddsSummary

from toolkit.logger import getLogger
from toolkit.matches import get_match_2way_scoredelta, get_match_2way_scoretotal
from wager.models import Wager

logger =  getLogger("toolkit.wagers","qualifier.log","wagers")
marketMap = odds.toolkit.markets.OddsMarketMapping()
class TheQualifier:
    parlay_ruleset = None
    account = None
    vhost = None
    def __init__(self):
        logger.info('TheQualifier(tm): Ready!')

    def calculate_payout(self,risk,odds):
        if odds > 0:  # Positive odds
            profit = risk * (odds / 100)
            payout = risk + profit
        else:  # Negative odds
            profit = risk * (100 / abs(odds))
            payout = risk + profit
        return payout

    def _qual_straight_bet(self,wagerObj,update_bet=True):
        logger.info(f"Qualifying Straight Bet: {wagerObj.uuid}")
        print(f"Qualifying Straight Bet: {wagerObj.uuid}")
        scoredelta, hi_score, lo_score = get_match_2way_scoredelta(wagerObj.match)
        if scoredelta == 0:
            if wagerObj.for_draw:
                logger.info(f"Player bet on Draw; match is a draw, player WINS!")
                if not update_bet: return True
                wagerObj.status = "W"
                wagerObj.qualifier_history = {"auto": True,"draw_won":True,"type":"parlay_leg_straight"}
                wagerObj.save()
                return True
            logger.info(f"Match is a Draw! Scoredelta 0!")
            if not update_bet: return None
            wagerObj.status = "D"
            wagerObj.qualifier_history = {"auto": True,"type":"parlay_leg_straight"}
            wagerObj.save()
            return None
        if wagerObj.match.winner == wagerObj.team_1:
            logger.info(f"Player bet on winning team: {wagerObj.team_1.name}: Score: {hi_score}!")
            if not update_bet: return True
            wagerObj.status = "W"
            wagerObj.qualifier_history = {"auto":True,"type":"parlay_leg_straight"}
            wagerObj.save()
            return True
        else:
            logger.info(f"Wager is a looser!")
            if not update_bet: return False
            wagerObj.status = "L"
            wagerObj.qualifier_history = {"auto":True,"type":"parlay_leg_straight"}
            wagerObj.save()
            return False

    def _score_period_calc(self,home_score_obj,away_score_obj,period_name):
        if period_name == "Q1":
            if "quarter_1" in home_score_obj.score_data and "quarter_1" in away_score_obj.score_data:
                home_score = home_score_obj.score_data["quarter_1"]
                away_score = away_score_obj.score_data["quarter_1"]
            else:
                logger.warning(f"For Given Score Objects, {period_name} were not found.")
                return False, False
        elif period_name == "Q2":
            if "quarter_2" in home_score_obj.score_data and "quarter_2" in away_score_obj.score_data:
                home_score = home_score_obj.score_data["quarter_2"]
                away_score = away_score_obj.score_data["quarter_2"]
            else:
                logger.warning(f"For Given Score Objects, {period_name} were not found.")
                return False, False
        elif period_name == "Q3":
            if "quarter_3" in home_score_obj.score_data and "quarter_3" in away_score_obj.score_data:
                home_score = home_score_obj.score_data["quarter_3"]
                away_score = away_score_obj.score_data["quarter_3"]
            else:
                logger.warning(f"For Given Score Objects, {period_name} were not found.")
                return False, False
        elif period_name == "Q4":
            if "quarter_4" in home_score_obj.score_data and "quarter_4" in away_score_obj.score_data:
                home_score = home_score_obj.score_data["quarter_4"]
                away_score = away_score_obj.score_data["quarter_4"]
            else:
                logger.warning(f"For Given Score Objects, {period_name} were not found.")
                return False, False
        elif period_name == "H1":
            if "quarter_1" in home_score_obj.score_data and "quarter_1" in away_score_obj.score_data and "quarter_2" in home_score_obj.score_data and "quarter_2" in away_score_obj.score_data:
                home_score = home_score_obj.score_data["quarter_1"]+home_score_obj.score_data["quarter_2"]
                away_score = away_score_obj.score_data["quarter_1"]+away_score_obj.score_data["quarter_2"]
            else:
                logger.warning(f"For Given Score Objects, {period_name} were not found.")
                return False, False
        elif period_name == "H2":
            if "quarter_3" in home_score_obj.score_data and "quarter_3" in away_score_obj.score_data and "quarter_4" in home_score_obj.score_data and "quarter_4" in away_score_obj.score_data:
                home_score = home_score_obj.score_data["quarter_3"]+home_score_obj.score_data["quarter_4"]
                away_score = away_score_obj.score_data["quarter_3"]+away_score_obj.score_data["quarter_4"]
            else:
                logger.warning(f"For Given Score Objects, {period_name} were not found.")
                return False, False
        return home_score, away_score





    def _qual_dyn_spread_bet(self,wagerObj):
        logger.info(f"Qualifying Dynamic Spread for Bet: {wagerObj.uuid}, Period: {wagerObj.bet_data['period']}")
        home_score_obj = MatchScore.objects.get(match=wagerObj.match, team=wagerObj.match.home_team)
        away_score_obj = MatchScore.objects.get(match=wagerObj.match, team=wagerObj.match.away_team)
        home_score,away_score = self._score_period_calc(home_score_obj,away_score_obj,wagerObj.bet_data['period'])
        if home_score and away_score == False:
            logger.warning("_score_period_calc refused to resolve. This wager requires ** MANUAL INTERVENTION **")
            logger.warning(f"**[Wager {wagerObj.uuid}] **")
            wagerObj.qualifier_history = {"auto":True,"fail":True,"retry":True,"msg":"_score_period_calc refused to resolve. Check Syslog / Resolve Manually."}
            wagerObj.save()
            return -1

        if home_score == away_score:
            logger.info(f"Match is a Draw! Scoredelta 0!")
            wagerObj.status = "D"
            wagerObj.qualifier_history = {"auto": True}
            wagerObj.save()
            return None
        if wagerObj.team_1 == wagerObj.match.home_team:
            adjusted_score = home_score - Decimal(wagerObj.bet_data["points"])
            scoredelta = home_score - away_score
            if adjusted_score > away_score:
                logger.info(f"Wager is a Winner!: Spread: {wagerObj.bet_data['points']}, Actual Delta: {scoredelta}, Score: {home_score}")
                wagerObj.status = "W"
                wagerObj.qualifier_history = {"auto": True}
                wagerObj.save()
                return True
            else:
                logger.info(f"Wager is a Looser!: Spread: {wagerObj.bet_data['points']}, Actual Delta: {scoredelta}, Score: {home_score}")
                wagerObj.status = "L"
                wagerObj.qualifier_history = {"auto": True}
                wagerObj.save()
                return False
        else:
            adjusted_score = away_score + Decimal(wagerObj.bet_data["points"])
            scoredelta = home_score - away_score
            if adjusted_score > home_score:
                logger.info(f"Wager is a Winner!: Spread: {wagerObj.bet_data['points']}, Actual Delta: {scoredelta}, Score: {away_score}")
                wagerObj.status = "W"
                wagerObj.qualifier_history = {"auto": True}
                wagerObj.save()
                return True
            else:
                logger.info(f"Wager is a Looser!: Spread: {wagerObj.bet_data['points']}, Actual Delta: {scoredelta}, Score: {away_score}")
                wagerObj.status = "L"
                wagerObj.qualifier_history = {"auto": True}
                wagerObj.save()
                return False


    def _qual_spread_bet(self,wagerObj,delta_check=True,update_bet=True):
        logger.info(f"Qualifying Spread for Bet: {wagerObj.uuid}")
        scoredelta, hi_score, lo_score = get_match_2way_scoredelta(wagerObj.match)
        if delta_check:
            if scoredelta == 0:
                logger.info(f"Match is a Draw! Scoredelta 0!")
                if not update_bet: return None
                wagerObj.status = "D"
                wagerObj.qualifier_history = {"auto": True}
                wagerObj.save()
                return None
        home_score = MatchScore.objects.get(match=wagerObj.match, team=wagerObj.match.home_team)
        away_score = MatchScore.objects.get(match=wagerObj.match, team=wagerObj.match.away_team)
        if wagerObj.team_1 == wagerObj.match.home_team:
            adjusted_score = home_score.score - Decimal(wagerObj.bet_data["points"])
            logger.info(f"Player bet on Home Team: AS: {adjusted_score}, based on: {home_score.score} - {wagerObj.bet_data['points']}")
            if adjusted_score > away_score.score2int():
                if not update_bet: return True
                logger.info(f"Wager is a Winner!: Spread: {wagerObj.bet_data['points']}, Actual Delta: {scoredelta}, Score: {hi_score}")
                wagerObj.status = "W"
                wagerObj.qualifier_history = {"auto": True}
                wagerObj.save()
                return True
            else:
                logger.info(f"Wager is a Looser!: Spread: {wagerObj.bet_data['points']}, Actual Delta: {scoredelta}, Score: {lo_score}")
                if not update_bet: return False
                wagerObj.status = "L"
                wagerObj.qualifier_history = {"auto": True}
                wagerObj.save()
                return False
        else:
            adjusted_score = away_score.score + Decimal(wagerObj.bet_data["points"])
            logger.info(f"Player bet on Away Team: AS: {adjusted_score}, based on: {away_score.score} + {wagerObj.bet_data['points']}")
            if adjusted_score > home_score.score2int():
                logger.info(f"Wager is a Winner!: Spread: {wagerObj.bet_data['points']}, Actual Delta: {scoredelta}, Score: {hi_score}")
                if not update_bet: return True
                wagerObj.status = "W"
                wagerObj.qualifier_history = {"auto": True}
                wagerObj.save()
                return True
            else:
                logger.info(f"Wager is a Looser!: Spread: {wagerObj.bet_data['points']}, Actual Delta: {scoredelta}, Score: {lo_score}")
                if not update_bet: return False
                wagerObj.status = "L"
                wagerObj.qualifier_history = {"auto": True}
                wagerObj.save()
                return False

    def _qual_dyn_totals_bet(self,wagerObj,update_bet=True):
        logger.info(f"Qualifying Dynamic Spread for Bet: {wagerObj.uuid}, Period: {wagerObj.bet_data['period']}")

        home_score_obj = MatchScore.objects.get(match=wagerObj.match, team=wagerObj.match.home_team)
        away_score_obj = MatchScore.objects.get(match=wagerObj.match, team=wagerObj.match.away_team)
        home_score, away_score = self._score_period_calc(home_score_obj, away_score_obj, wagerObj.bet_data['period'])
        if home_score and away_score == False:
            logger.warning("_score_period_calc refused to resolve. This wager requires ** MANUAL INTERVENTION **")
            logger.warning(f"**[Wager {wagerObj.uuid}] **")

            wagerObj.qualifier_history = {"auto": True, "fail": True, "retry": True, "msg": "_score_period_calc refused to resolve. Check Syslog / Resolve Manually."}
            wagerObj.save()
            return -1
        # print(home_score, away_score)
        score_total = home_score + away_score
        if wagerObj.bet_data["totals"] == "over":
            if score_total > Decimal(wagerObj.bet_data["points"]):
                logger.info(f"Wager is a Winner!: Final Score for match: {score_total}! ")
                if not update_bet: return True
                wagerObj.status = "W"
                wagerObj.qualifier_history = {"auto": True}
                wagerObj.save()
                return True
            else:
                logger.info(f"Wager is a Looser!: Final Score for match: {score_total}! ")
                if not update_bet: return False
                wagerObj.status = "L"
                wagerObj.qualifier_history = {"auto": True}
                wagerObj.save()
                return False
        elif wagerObj.bet_data["totals"] == "under":
            if score_total < Decimal(wagerObj.bet_data["points"]):
                logger.info(f"Wager is a Winner!: Final Score for match: {score_total}! ")
                if not update_bet: return True
                wagerObj.status = "W"
                wagerObj.qualifier_history = {"auto": True}
                wagerObj.save()
                return True
            else:
                logger.info(f"Wager is a Looser!: Final Score for match: {score_total}! ")
                if not update_bet: return False
                wagerObj.status = "L"
                wagerObj.qualifier_history = {"auto": True}
                wagerObj.save()
                return False
        else:
            logger.warning(f"Wager {wagerObj.uuid} has an unknown totals value, {wagerObj.bet_data['totals']}. Not qualifying.")
            return None


    def _qual_totals_bet(self,wagerObj,update_bet=True):
        logger.info(f'Qualifying Totals Bet: {wagerObj.uuid}: {wagerObj.bet_data["type"]}')
        scoretotal, hi_score, lo_score = get_match_2way_scoretotal(wagerObj.match)
        if "totals" in wagerObj.bet_data:
            bet_type = f"totals-{wagerObj.bet_data['totals']}"
        else:
            bet_type = wagerObj.bet_data["type"]

        if bet_type == "totals-over":
            if scoretotal > Decimal(wagerObj.bet_data["points"]):
                logger.info(f"Wager is a Winner!: Final Score for match: {scoretotal}! ")
                if not update_bet: return True
                wagerObj.status = "W"
                wagerObj.qualifier_history = {"auto": True}
                wagerObj.save()
                return True
            else:
                logger.info(f"Wager is a Looser!: Final Score for match: {scoretotal}! ")
                if not update_bet: return False
                wagerObj.status = "L"
                wagerObj.qualifier_history = {"auto": True}
                wagerObj.save()
                return False
        elif bet_type == "totals-under":
            if scoretotal < Decimal(wagerObj.bet_data["points"]):
                if not update_bet: return True
                wagerObj.status = "W"
                wagerObj.qualifier_history = {"auto": True}
                wagerObj.save()
                return True
            else:
                logger.info(f"Wager is a Looser!: Final Score for match: {scoretotal}! ")
                if not update_bet: return False
                wagerObj.status = "L"
                wagerObj.qualifier_history = {"auto": True}
                wagerObj.save()
                return False




    def _parlay_node_qualify(self,wagerObj,update_bet=True):
        if wagerObj.status in ['P','M'] and wagerObj.match.finished:
            if wagerObj.bet_data["type"].startswith("totals"):
                return self._qual_totals_bet(wagerObj,update_bet)
            elif wagerObj.bet_data["type"].startswith("spread"):
                return self._qual_spread_bet(wagerObj,True,update_bet)
            elif wagerObj.bet_data["type"].startswith("straight"):
                return self._qual_straight_bet(wagerObj,update_bet)

        else:
            print(f"Node won't be qualified. Status is: {wagerObj.status}, Match Finished: {wagerObj.match.finished}")
            return None

    def _qual_parlay_bet(self,wagerObj):
        if "dynamic" not in wagerObj.bet_data:
            return self._qual_parlay_bet_static(wagerObj)
        else:
            return self._qual_parlay_bet_dynamic(wagerObj)

    def _qual_parlay_bet_dynamic(self,wagerObj):
        if "root_wager" in wagerObj.bet_data:
            nodes = wagerObj.bet_data["nodes"]+[wagerObj.uuid]
            root_wager = wagerObj
        else:
            root_wager = Wager.objects.get(uuid=wagerObj.bet_data["parent"])
            nodes = root_wager.bet_data["nodes"]+[root_wager.uuid]
        ruleset = wagerObj.parlay_ruleset
        total_matches = len(nodes)
        active_rules = ParlayPayoutRulesetEntry.objects.filter(ruleset=ruleset,parlay_legs=total_matches)

        if len(active_rules) == 0:
            logger.warning(f"For Wager {wagerObj.uuid}: No active rules found for {total_matches} legs -  Falling back to static Parlay mode.")
            return self._qual_parlay_bet_static(wagerObj)
        qualify_at = total_matches-active_rules.order_by('-max_losses').only('max_losses').first().max_losses


        if len(active_rules) == 0:
            logger.warning(f"For Wager {wagerObj.uuid}, Parlay is {total_matches}, but no Active ParlayPayoutVHostRulesetEntry records were found. ")
        finished_matches = 0
        total_wins = 0
        total_losses = 0
        # print(nodes)
        for node in nodes:
            nodeObj = Wager.objects.get(uuid=node)
            # print(nodeObj)
            if nodeObj.match.finished and nodeObj.match.score_closed:
                update_wager = False if "root_wager" in nodeObj.bet_data else True
                winner = self._parlay_node_qualify(nodeObj,update_wager)
                finished_matches += 1
                if winner is True:
                    total_wins += 1
                else:
                    print(f"Match: {nodeObj.match.get_match_name()}: Wager Looses!")
                    total_losses += 1
            else:
                logger.warning(f"Match {nodeObj.match} is not finished: {nodeObj.match.finished}, or score is not closed: {nodeObj.match.score_closed}")
        # print(total_matches,finished_matches,total_wins,total_losses)
        if finished_matches >= qualify_at:
            if total_losses == 0 and (finished_matches < total_matches):
                # We have no losses, but less finished matches than total legs
                # in parlay, so we will just pass and fly on here:
                pass
            elif total_losses == 0 and (finished_matches == total_matches):
                # Wager is a winner!! Close nodes; qualify the root and send it up.
                if self._parlay_node_qualify(root_wager):
                    root_wager.status = "W"
                    root_wager.save()
                    for lnode in nodes:
                        lnodeObj = Wager.objects.get(uuid=lnode)
                        lnodeObj.parlay_closed = True
                        lnodeObj.save()
                    root_wager.partial_payout = True
                    root_wager.parlay_closed = True
                    root_wager.save()
                    return True
            elif total_losses >= qualify_at:
                # She's a looser baby; and no one likes her!
                for lnode in nodes:
                    lnodeObj = Wager.objects.get(uuid=lnode)
                    lnodeObj.parlay_closed = True
                    lnodeObj.save()
                root_wager.parlay_closed = True
                root_wager.status = "L"
                root_wager.save()
                return False
            else:
                # Surely, we must have to take an option here to
                # find a payout rule, or the entire wager is lost
                # Condition being, finished matches >= qualify_at and total_losses > 0.
                try:
                    parlay_rule = active_rules.get(max_losses=total_losses)
                except ParlayPayoutRulesetEntry.DoesNotExist:
                    # Oh shit! sorry buddy! Ruleset does not exist, you LOOSE!
                    logger.warning(f"Wager {root_wager.uuid} has no active ParlayPayoutVHostRulesetEntry active for {total_matches} legs with {total_losses} losses. QUALIFYING IT AS LOOSER!")
                    for lnode in nodes:
                        lnodeObj = Wager.objects.get(uuid=lnode)
                        lnodeObj.parlay_closed = True
                        lnodeObj.save()
                    root_wager.parlay_closed = True
                    root_wager.status = "L"
                    root_wager.save()
                    return False
                # We have a ruleset! Let's cash out:
                # Let's start with regrading and removing the loosing wager(s):
                final_odds = []

                for lnode in nodes:
                    lnodeObj = Wager.objects.get(uuid=lnode)
                    if "root_wager" in lnodeObj.bet_data:
                        check = self._parlay_node_qualify(lnodeObj,False)
                    else:
                        check = lnodeObj.status == "W"
                    if check:
                        matchOdds = MatchOddsSummary.objects.get(uuid=lnodeObj.bet_data["hierarchy"])
                        hp, ap, dp = american_juicer(matchOdds.home_price, matchOdds.away_price, matchOdds.draw_price, juice_pct=parlay_rule.juice_percentage/100)
                        # print(hp,ap,dp)
                        if wagerObj.for_draw:
                            final_odds.append(float(dp))
                        elif lnodeObj.team_1 == lnodeObj.match.home_team:
                            final_odds.append(float(hp))
                        elif lnodeObj.match.away_team == lnodeObj.team_1:
                            final_odds.append(float(ap))
                    lnodeObj.parlay_closed = True
                    lnodeObj.save()
                # if self._parlay_node_qualify(root_wager,False):

                # Okay, now we have our final node calculations for payout, compute payout and EAP:
                # print(final_odds)
                final_parlay_odds = parlay_decimal_odds(final_odds)
                bet_data_upd = {
                    "early_payout":True,
                    "final_parlay_odds": float(final_parlay_odds),
                    "total_matches":total_matches,
                    "total_losses": total_losses,
                    "total_wins": total_wins,
                    "ju_pct":parlay_rule.juice_percentage,
                    "eap_pct":parlay_rule.players_percentage,
                    "original_win":float(root_wager.win)
                }
                # print(parlay_rule.juice_percentage)
                # print(final_odds)
                final_payout = (Decimal(root_wager.risk) * Decimal(final_parlay_odds)) * Decimal(parlay_rule.players_percentage/100)
                root_wager.win = round(float(final_payout),2)
                root_wager.qualifier_history.update(bet_data_upd)
                root_wager.partial_payout = True
                root_wager.status = "W"
                root_wager.save()
                logger.warning(
                    f"Dynamic EAP for Parlay Wager: {wagerObj}: Total Legs: {total_matches}, Total Losses: {total_losses}. Original Payout: {bet_data_upd["original_win"]}, New Win: {root_wager.win}, EAP applied: {parlay_rule.players_percentage:.2f}%. Juiced: {parlay_rule.juice_percentage/100}%. ")
                return True

        else:
            # Not yet ready to qualify!
            return None

    def _qual_parlay_bet_static(self,wagerObj):
        # Only qualify root wagers:
        if "root_wager" not in wagerObj.bet_data:
            # If this is a node, we'll qualify the root node:
            if "parent" in wagerObj.bet_data:
                pWagerObj = Wager.objects.get(uuid=wagerObj.bet_data["parent"])
                return self._qual_parlay_bet(pWagerObj)
            else:
                logger.error(f"Unknown Node Parlay Wager without a Parent Node in bet_data. Wager: {wagerObj.uuid}")
                return -1
        logger.info(f"Qualifying Root Parlay Bet: {wagerObj.uuid}")
        # print(f"Qualifying Root Parlay Bet: {wagerObj.uuid}")
        # check that all legs are closed, and won:
        complete = False
        won = False
        losses = 0
        for node in wagerObj.bet_data['nodes']:
            nWagerObj = Wager.objects.get(uuid=node)
            qst = self._parlay_node_qualify(nWagerObj)

            if nWagerObj.status == "L":
                #Lost wager!
                complete = True
                won = False
                losses += 1
                logger.info(f"{nWagerObj.uuid} wager is Lost! Root Wager is lost.")
                # print(f"{nWagerObj.uuid} wager is Lost! Root Wager is lost.")
            elif nWagerObj.status == "W":
                # Won wager!
                won = True
                complete = True
                logger.info(f"{nWagerObj.uuid} wager is Won! Root Wager is so far won.")
            elif nWagerObj.status == "P" or nWagerObj.status == "M":
                complete = False
                logger.info(f"{nWagerObj.uuid} wager in progress! Status is M.")
            else:
                logger.info(f"Root Parlay was not qualified? Status is: {qst}")
        # print(f"Qualifier results: {complete} @ {losses}")
        if not complete and losses == 0:
            wagerObj.status = "M"
            logger.info("Root bet: Not all matches are complete yet. Status is M (Matches in Progress)")
            wagerObj.save()
            return None
        else:
            logger.info("Qualifying ROOT Wager outcome...")
            for node in wagerObj.bet_data['nodes']:
                nWagerObj = Wager.objects.get(uuid=node)
                nWagerObj.parlay_closed = True
                nWagerObj.save()
            wagerObj.parlay_closed = True
            wagerObj.save()
            if won:
                if self._parlay_node_qualify(wagerObj):
                    logger.info(f"Winner winner chicken Dinner! Won Parlay Wager {wagerObj.uuid}")
                    # print(f"Winner winner chicken Dinner! Won Parlay Wager {wagerObj.uuid}")
                    wagerObj.status = "W"
                    wagerObj.save()
                    return True
                else:
                    wagerObj.status = "L"
                    wagerObj.save()
                    logger.info(f"Better luck next time, wager {wagerObj.uuid} lost.")
                    # print(f"Better luck next time, wager {wagerObj.uuid} lost.")
                    return False
            else:
                wagerObj.status = "L"
                wagerObj.save()
                logger.info(f"Better luck next time, wager {wagerObj.uuid} lost.")
                # print(f"Better luck next time, wager {wagerObj.uuid} lost.")
                return False

    def _qualify_dyn_moneyline(self,wagerObj):
        logger.info(f"Qualifying Dynamic Spread for Bet: {wagerObj.uuid}, Period: {wagerObj.bet_data['period']}")
        home_score_obj = MatchScore.objects.get(match=wagerObj.match, team=wagerObj.match.home_team)
        away_score_obj = MatchScore.objects.get(match=wagerObj.match, team=wagerObj.match.away_team)
        home_score, away_score = self._score_period_calc(home_score_obj, away_score_obj, wagerObj.bet_data['period'])
        if home_score and away_score == False:
            logger.warning("_score_period_calc refused to resolve. This wager requires ** MANUAL INTERVENTION **")
            logger.warning(f"**[Wager {wagerObj.uuid}] **")
            wagerObj.qualifier_history = {"auto": True, "fail": True, "retry": True, "msg": "_score_period_calc refused to resolve. Check Syslog / Resolve Manually."}
            wagerObj.save()
            return -1
        if away_score == home_score:
            wagerObj.status = 'D'
            wagerObj.qualifier_history = {"auto": True}
            wagerObj.save()
        if wagerObj.team_1 == wagerObj.match.home_team:
            if home_score > away_score:
                logger.info(f"Winner Winner Chicken Dinner! Won ML wager!")
                wagerObj.status = "W"
                wagerObj.qualifier_history = {"auto": True}
                wagerObj.save()
                return True
            else:
                logger.info(f"Lost wager!")
                wagerObj.status = "L"
                wagerObj.qualifier_history = {"auto": True}
                wagerObj.save()
                return False
        elif wagerObj.team_1 == wagerObj.match.away_team:
            if home_score < away_score:
                logger.info(f"Winner Winner Chicken Dinner! Won ML wager!")
                wagerObj.status = "W"
                wagerObj.qualifier_history = {"auto": True}
                wagerObj.save()
                return True
            else:
                logger.info(f"Lost wager!")
                wagerObj.status = "L"
                wagerObj.qualifier_history = {"auto": True}
                wagerObj.save()
                return False

    def _qualify_moneyline(self,wagerObj):
        logger.info(f"Qualifying Moneyline Bet: {wagerObj.uuid}")
        logger.info(f"Player bet on team: {wagerObj.team_1.uuid}/{wagerObj.team_1.name}")
        if wagerObj.match.winner == wagerObj.team_1:
            logger.info(f"Winner Winner Chicken Dinner! Won ML wager!")
            wagerObj.status = "W"
            wagerObj.qualifier_history = {"auto": True}
            wagerObj.save()
            return True
        else:
            logger.info(f"Lost wager!")
            wagerObj.status = "L"
            wagerObj.qualifier_history = {"auto": True}
            wagerObj.save()
            return False

    def _qualify_dynamic(self,wagerObj):
        logger.info(f"Qualifying Dynamic Bet: {wagerObj.uuid}, Type: {wagerObj.bet_data['dynamic']}")
        mtype = marketMap.get_market_datatype(wagerObj.bet_data['dynamic'])
        if mtype == "player":
            mod_name =  f"sports.qualifiers.{wagerObj.match.sport.group.slug}.{mtype}.{wagerObj.bet_data['dynamic']}.wagers"
            try:
                qual_module = importlib.import_module(mod_name)
                qualified = qual_module.qualify_wager(wagerObj)
                if qualified:
                    logger.info(f"Winner Winner Chicken Dinner! Won Dynamic Wager!")
                    wagerObj.status = "W"
                    wagerObj.qualifier_history = {"auto": True}
                    wagerObj.save()
                    return True
                else:
                    logger.info(f"Lost wager!")
                    wagerObj.status = "L"
                    wagerObj.qualifier_history = {"auto": True}
                    wagerObj.save()
                    return False
            except ImportError:
                logger.error(mod_name)
                return False
        elif mtype == "spr_team":
            qualified = self._qual_dyn_spread_bet(wagerObj)
            if qualified is None:
                wagerObj.status = 'D'
                wagerObj.qualifier_history = {"auto": True}
                wagerObj.save()
            return qualified
        elif mtype == "tot_team":
            qualified = self._qual_dyn_totals_bet(wagerObj)
            return qualified
        elif mtype == "h2h_team":
            qualified = self._qualify_dyn_moneyline(wagerObj)
            return qualified
        else:

            logger.warning(f"For wager {wagerObj.uuid}; Market type is {mtype} - i don't know how to process this.")
            return None

    def qualify_bet(self,wagerObj):
        logger.info(f"**** Qualifying Wager/Bet {wagerObj.uuid} ****")
        if not wagerObj.parlay_closed and wagerObj.status in ["L", "W"] and "parent" in wagerObj.bet_data:
            logger.info(f"This is an executed node of parent wager {wagerObj.bet_data['parent']} - qualifying the parent.")
            # print(f"This is an executed node of parent wager {wagerObj.bet_data['parent']} - qualifying the parent.")
            pWagerObj = Wager.objects.get(uuid=wagerObj.bet_data["parent"])
            return self._qual_parlay_bet(pWagerObj)
        elif wagerObj.status == "W":
            logger.info("Wager is already won, returning true.")
            return True

        if wagerObj.status not in ["P","M"]:
            return False
        if (wagerObj.type == "ST"):
            return self._qual_straight_bet(wagerObj)
        elif (wagerObj.type == "SP"):
            return self._qual_spread_bet(wagerObj)
        elif (wagerObj.type == "TO"):
            return self._qual_totals_bet(wagerObj)
        elif(wagerObj.type in ["PA","TE"]):
            return self._qual_parlay_bet(wagerObj)
        elif(wagerObj.type == "ML"):
            return self._qualify_moneyline(wagerObj)
        elif(wagerObj.type == "DY"):
            return self._qualify_dynamic(wagerObj)



    def parlay_early_payout_validate(self,wagerObj):
        logger.info(f"**** Validating Eligibility for  Parlay Early Payout: {wagerObj.uuid} ****")

        if wagerObj.type != "PA":
            logger.error("Not a Parlay wager.")
            # print("NA")
            return False
        # Only works when starting from a root wager:
        if 'root_wager' not in wagerObj.bet_data:
            logger.error("Not a root parlay wager.")
            # print("RA")
            return False
        losses = 0
        wins = 0
        # Qualify each node to see if we have winners and loosers (including the root):
        nodes = wagerObj.bet_data["nodes"] + [wagerObj.uuid]
        for nuuid in nodes:
            nWagerObj = Wager.objects.get(uuid=nuuid)
            qares = self._parlay_node_qualify(nWagerObj,False)

            if qares is True:
                wins += 1
                # print("Win")
            elif qares is False:
                # print("lOOSE")
                losses += 1
        if losses > 0 or wins < 1:
            return False
        else:
            return True

    def parlay_early_get_beta(self,wagerObj):
        logger.info(f"**** Validating Eligibility for  Parlay Early Payout: {wagerObj.uuid} ****")

        if wagerObj.type != "PA":
            logger.error("Not a Parlay wager.")
            # print("NA")
            return False
        # Only works when starting from a root wager:
        if 'root_wager' not in wagerObj.bet_data:
            logger.error("Not a root parlay wager.")
            # print("RA")
            return False
        beta = 1
        count = -1
        # Qualify each node to see if we have winners and loosers (including the root):
        nodes = wagerObj.bet_data["nodes"] + [wagerObj.uuid]
        for nuuid in nodes:
            try:
                nWagerObj = Wager.objects.get(uuid=nuuid,status="P",match__finished=False)
                if nWagerObj.base_spread > 0:
                    be = (abs(nWagerObj.base_spread) / 100)+1
                elif nWagerObj.base_spread < 0:
                    be = (100 / (abs(nWagerObj.base_spread))) +1
                # print(be)
                beta = beta * be
                count +=1
            except Wager.DoesNotExist:
                pass
        # print(beta)
        return beta,count




