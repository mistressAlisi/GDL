from django.db import transaction

from django.db import transaction

from ledger.models import AccountLedgerTransaction, DailyLedgerTransactions, AccountTransaction
from teams.models import Team
from toolkit.ledger.timekeeper import get_weekly_account_ledger, get_weekly_ledger, get_weekday_name
from toolkit.logger import getLogger
from toolkit.matches import get_match_2way_scoredelta
from toolkit.wagers.ledger_tools import win_and_credit, loose_and_debit
from toolkit.wagers.scoring_tools import calculate_parlay_total_wins, calculate_straight_bet_wins
from wager.models import Wager

logger =  getLogger("toolkit.wagers","close_tools.log","wagers")
### DEPRECATED BELOW? ####
# def close_straight_bet(wagerObj):
#     logger.info("Straight Bet mode")
#     scoredelta,score_0,score_1 = get_match_2way_scoredelta(wagerObj.match)
#     lowscore = min(score_0, score_1)
#     highscore = max(score_0, score_1)
#     #print(wagerObj)
#     if scoredelta == 0:
#         logger.info(f"Match is a Draw! Scoredelta 0! Cancelling Wager {wagerObj.uuid}..")
#         # TODO: CANCEL WAGER HERE
#         return True
#     logger.info(f"Player bet on team: {wagerObj.team_1.uuid}/{wagerObj.team_1.name}")
#     if wagerObj.match.winner == wagerObj.team_1:
#         logger.info(f"Player bet on winning team, by a spread of: {scoredelta}, with a line of: {wagerObj.bet_data['points']}")
#         spread = (scoredelta+(wagerObj.bet_data['points']*1))
#
#         if spread > lowscore:
#             logger.info(f"**Spread is covered: {spread}/{lowscore} Player wins this wager!!")
#
#             return win_and_credit(wagerObj,calculate_straight_bet_wins(int(wagerObj.risk),int(wagerObj.base_spread)))
#         else:
#             logger.info("**Spread is NOT covered: Player loses this wager!!")
#             return loose_and_debit(wagerObj)
#
#     else:
#         logger.info(f"Player bet on loosing team, by a spread of: {scoredelta}, with a line of: {wagerObj.bet_data['points']}")
#         spread = (wagerObj.bet_data['points']*1)+lowscore
#         if spread > highscore:
#             logger.info(f"**Spread is covered: {spread}/{highscore} Player wins this wager!!")
#             return win_and_credit(wagerObj,calculate_straight_bet_wins(int(wagerObj.risk),int(wagerObj.base_spread)))
#         else:
#             logger.info(f"**Spread is NOT covered: {spread}/{highscore} Player loses this wager!!")
#             return loose_and_debit(wagerObj)
#
# def process_parlay_match(wagerObj,matchObj):
#     logger.info(f"Processing Parlay for wager {wagerObj.uuid}, Match: {matchObj.uuid}")
#     # step one; find the wager leg:
#     current_leg = False
#     current_leg_id = 0
#     for leg in wagerObj.bet_data['legs']:
#         leg_data = wagerObj.bet_data['legs'][leg]
#         muuid = str(matchObj.uuid)
#         if leg_data["match"] == muuid:
#             current_leg = leg_data
#             current_leg_id = leg
#             break
#     if not current_leg:
#         logger.error(f"Match {matchObj.uuid} has no leg in Wager {wagerObj.uuid}.")
#         return False
#     # is leg already closed?
#     if current_leg["complete"]:
#         logger.info(f"Wager {wagerObj.uuid}: Leg {current_leg['match']} is complete - skipping...")
#         return False
#     # step two, compute outcome for leg:
#     scoredelta, score_0, score_1 = get_match_2way_scoredelta(matchObj)
#     if not scoredelta:
#         return False
#     # TODO : handle Scoredelta zero.
#     lowscore = min(score_0, score_1)
#     highscore = max(score_0, score_1)
#     teamObj = Team.objects.filter(uuid=current_leg["team"])
#     if matchObj.winner == teamObj:
#         logger.info(f"Player bet on winning team, by a spread of: {scoredelta}, with a line of: {current_leg['points']}")
#         spread = scoredelta + float(current_leg['points'])
#
#         if spread > lowscore:
#             logger.info(f"**Spread is covered: {spread}/{lowscore} Player wins this wager!!")
#             wagerObj.bet_data['legs'][current_leg_id]["won"] = True
#         else:
#             logger.info("**Spread is NOT covered: Player loses this wager!!")
#             wagerObj.bet_data['legs'][current_leg_id]["won"] = False
#
#     else:
#         logger.info(f"Player bet on loosing team, by a spread of: {scoredelta}, with a line of: {current_leg['points']}")
#         spread = float(current_leg['points'] ) + lowscore
#         if spread > highscore:
#             logger.info(f"**Spread is covered: {spread}/{highscore} Player wins this wager!!")
#             wagerObj.bet_data['legs'][current_leg_id]["won"] = True
#         else:
#             logger.info(f"**Spread is NOT covered: {spread}/{highscore} Player loses this wager!!")
#             wagerObj.bet_data['legs'][current_leg_id]["won"] = False
#
#     wagerObj.bet_data['legs'][current_leg_id]['complete'] = True
#     wagerObj.save()
#     logger.info("Wager Leg Closed!")
#     return True
#

#
# def close_parlay_wager(wagerObj):
#     logger.info(f"Processing Parlay wager {wagerObj.uuid}: Attempting to close")
#     # check that all legs are closed, and won:
#     complete = False
#     won = False
#     for leg in wagerObj.bet_data['legs']:
#         leg_data = wagerObj.bet_data['legs'][leg]
#         complete = leg_data["complete"]
#         won = leg_data["won"]
#         if not complete:
#             logger.info(f"Leg {leg_data['match']} not yet complete.")
#     if not complete:
#         logger.info("Will not Close Parlay Wager: Still has unfinished legs.")
#         wagerObj.status = "M"
#         wagerObj.save()
#         return False
#
#     # Believe it or not, we're ready to compute if the player won or not!
#     if won:
#         logger.info(f"***PLAYER WINS PARLAY BET {wagerObj.uuid}***")
#         wagerObj.status = "W"
#         wagerObj.save()
#         return win_and_credit(wagerObj,calculate_parlay_total_wins(wagerObj.bet_data["risk"],wagerObj.bet_data["final_odds"]))
#     else:
#         logger.info(f"***PLAYER LOOSES PARLAY BET {wagerObj.uuid}***")
#         wagerObj.status = "L"
#         wagerObj.save()
#         return loose_and_debit(wagerObj)



def cancel_wager(wagerObj,destroy=False,user=False):
    if destroy and not user:
        logger.error("Can't call cancel_wager with destroy and not user.")
        return False
    if destroy and user:
        if not user.has_perm("ledger.audit_transactions"):
            logger.error("Can't call cancel_wager with destroy and not user.")
            return False
    # Handle Parlays and Teasers:
    if wagerObj.type in ['PA', 'TE']:
        if hasattr(wagerObj.bet_data, "root_wager") and wagerObj.bet_data["root_wager"]:
            for n in wagerObj.bet_data["nodes"]:
                try:
                    nWagerObj = Wager.objects.get(uuid=n, status__in=["P", "M", "W", "L", "X", "E", "D", "I"])
                    cancel_wager(nWagerObj, destroy, user)
                except Wager.DoesNotExist:
                    pass
    with transaction.atomic():
        _transObj = AccountTransaction.objects.filter(relations__wagers__contains=str(wagerObj.uuid))
        for transObj in _transObj:
            try:
                altObj = AccountLedgerTransaction.objects.get(transaction=transObj)
            except AccountLedgerTransaction.DoesNotExist:
                altObj = False
            try:
                dlObj = DailyLedgerTransactions.objects.get(transaction=transObj)
            except DailyLedgerTransactions.DoesNotExist:
                dlObj = False
            acct_wkl_ledger = get_weekly_account_ledger(wagerObj.account, transObj.created)
            wkl_ledger = get_weekly_ledger(wagerObj.vhost,transObj.created)
            day_name = get_weekday_name(transObj.created)
            if transObj.type == "wager_won":
                if altObj:
                    altObj.transactions -= -1
                    altObj.gain -= transObj.gain
                    altObj.flow -= transObj.gain
                    altObj.save()
                acct_gains = getattr(acct_wkl_ledger, f'{day_name}_gains') - transObj.gain
                setattr(acct_wkl_ledger, f'{day_name}_gains', acct_gains)
                acct_wkl_ledger.end_gains -= transObj.gain
                acct_wkl_ledger.save()
                if dlObj:
                    dlObj.ledger.loss -= transObj.gain
                    dlObj.ledger.flow -= transObj.gain
                    dlObj.ledger.save()
                wkl_ledger.end_losses -= transObj.gain
                wkl_ledger.save()
                wagerObj.account.available -= transObj.gain
                wagerObj.account.current -= transObj.gain
                wagerObj.account.withdrawable -= transObj.gain
                wagerObj.account.save()
            elif transObj.type == "wager_lost":
                if altObj:
                    altObj.transactions -= -1
                    altObj.loss -= transObj.gain
                    altObj.flow += transObj.gain
                    altObj.save()
                acct_gains = getattr(acct_wkl_ledger, f'{day_name}_gains') - transObj.gain
                setattr(acct_wkl_ledger, f'{day_name}_gains', acct_gains)
                acct_wkl_ledger.end_losses -= transObj.gain
                acct_wkl_ledger.save()
                if dlObj:
                    dlObj.ledger.gain -= transObj.gain
                    dlObj.ledger.flow -= transObj.gain
                    dlObj.ledger.save()
                wkl_ledger.end_losses -= transObj.gain
                wkl_ledger.save()
                wagerObj.account.available += transObj.gain
                wagerObj.account.at_risk -= transObj.gain
                wagerObj.account.withdrawable += transObj.gain
                wagerObj.account.save()
            elif transObj.type == "wager":
                total_wagers = getattr(acct_wkl_ledger, f"{day_name}_total_wagers") -1
                total_wagered = getattr(acct_wkl_ledger, f"{day_name}_wagered") - transObj.risk
                setattr(acct_wkl_ledger, f"{day_name}_total_wagers", total_wagers)
                setattr(acct_wkl_ledger, f"{day_name}_wagered", total_wagered)
                acct_wkl_ledger.save()
                total_wagers = getattr(wkl_ledger, f"{day_name}_total_wagers") - 1
                total_wagered = getattr(wkl_ledger, f"{day_name}_wagered") - transObj.risk
                setattr(wkl_ledger, f"{day_name}_total_wagers", total_wagers)
                setattr(wkl_ledger, f"{day_name}_wagered", total_wagered)
                wkl_ledger.save()
                wagerObj.account.available += transObj.risk
                wagerObj.account.current += transObj.risk
                wagerObj.account.withdrawable += transObj.risk
                wagerObj.account.at_risk -= transObj.risk
                wagerObj.account.save()
            wagerObj.status = 'C'
            wagerObj.closed = True
            wagerObj.cancelled = True
            if destroy:
                if altObj:
                    altObj.delete()
                wagerObj.delete()
                return True
            else:
                wagerObj.save()
                return True
