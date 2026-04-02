import uuid
from django.db import transaction

from django.db import transaction
from django.utils.timezone import now

from ledger.models import AccountLedgerTransaction, DailyLedgerTransactions, AccountTransaction
from linemanager.hierarchy import Hierarchy
from teams.models import Team
from toolkit.ledger.timekeeper import get_weekly_account_ledger, get_weekly_ledger, get_weekday_name
from toolkit.logger import getLogger
from toolkit.matches import get_match_2way_scoredelta
from toolkit.wagers.ledger_tools import win_and_credit, loose_and_debit, account_risk_balance
from toolkit.wagers.scoring_tools import calculate_parlay_total_wins, calculate_straight_bet_wins, \
    calculate_moneyline_payout
from wager.models import Wager, MatchWagers


def validate_bet_risk(hierarchy, account, risk):
    if risk < hierarchy.min_wager:
        return -1
    if risk > hierarchy.max_wager:
        return -2
    if risk > account.available:
        return -3
    if risk < account.min_wager:
        return -4
    if risk > account.max_wager:
        return -5
    return 1

logger =  getLogger("toolkit.wagers","create_tools.log","wagers")
@transaction.atomic
def create_spstraight_bet(vhost, domain, match, account, home_team, risk, points, base, wager_type="ST", remote_addr=None):
    logger.info(f"Creating Straight Bet on {match} for Vh: {vhost}, Domain: {domain}, Account: {account}, Home Team: {home_team}: Points: {points}, Base: {base}: Risking {risk}....")
    hierarchy = Hierarchy(vhost,**{"domain":domain,"match":match,"account":account,"home_team":match.home_team,"away_team":match.away_team})
    hierarchy.get_wager_limits()
    vb = validate_bet_risk(hierarchy, account, risk)
    if vb != 1:
        return vb
    to_win = calculate_straight_bet_wins(risk,base)
    if hierarchy.get_payin_ratio() != 0:
        risk = risk * hierarchy.get_payin_ratio()
    logger.info(f"Payin ratio for this hierarchy/wager is: {hierarchy.get_payin_ratio()}, Final risk pay-in: {risk}...")
    logger.info(f"Final Wager to-win: {to_win}")
    if home_team:
        team = match.home_team
        type = "spread-home-team"
    else:
        team = match.away_team
        type ="spread-away-team"
    bet_data = {"base": base, "risk": float(risk), "hierarchy":str(hierarchy.get_uuid()),"points":float(points),
                "to_win":float(to_win),"type":"straight","mode":wager_type}
    wObj = Wager.objects.create(uuid=uuid.uuid4(), account=account, team_1=team, match=match, risk=risk,
                                base_spread=base, bet_data=bet_data, win=to_win, type=type, vhost=vhost)
    wObj.save()
    if remote_addr:
        wObj.current_ip = remote_addr
    wMObj = MatchWagers.objects.create(match=match, wager=wObj)
    wMObj.save()
    wagers = []
    wagers.append(str(wObj.uuid))
    if not account_risk_balance(account,risk,1,to_win,"wager",now(),wagers):
        logger.error("Unable to deduct account. Rolling Back.")
        raise Exception("Unable to put balance at risk!")

    return wObj

@transaction.atomic
def create_totals_bet(vhost,domain,match,account,risk,points,base,wager_over=True,remote_addr=None):
    logger.info(f"Creating Totals Bet on {match} for Vh: {vhost}, Domain: {domain}, Account: {account}, Points: {points}, Base: {base}: Risking {risk}: Wager Over: {wager_over}....")
    hierarchy = Hierarchy(vhost,**{"domain":domain,"match":match,"account":account,"home_team":match.home_team,"away_team":match.away_team})
    hierarchy.get_wager_limits()
    vb = validate_bet_risk(hierarchy, account, risk)
    if vb != 1:
        return vb
    to_win = calculate_straight_bet_wins(risk, base)
    if hierarchy.get_payin_ratio() != 0:
        risk = risk * hierarchy.get_payin_ratio()
    logger.info(f"Payin ratio for this hierarchy/wager is: {hierarchy.get_payin_ratio()}, Final risk pay-in: {risk}...")
    logger.info(f"Final Wager to-win: {to_win}")
    if wager_over:
        total_mode ="over"
    else:
        total_mode ="under"
    bet_data = {"base": float(base), "risk": float(risk), "hierarchy":str(hierarchy.get_uuid()),"points":float(points),"to_win":float(to_win),"type":"totals","mode":total_mode}
    wObj = Wager.objects.create(uuid=uuid.uuid4(), account=account, team_1=match.home_team, match=match, risk=risk,
                                base_spread=base, bet_data=bet_data, win=to_win, type="TO", vhost=vhost)
    wObj.save()
    if remote_addr:
        wObj.current_ip = remote_addr
    wMObj = MatchWagers.objects.create(match=match, wager=wObj)
    wMObj.save()
    wagers = []
    wagers.append(str(wObj.uuid))
    if not account_risk_balance(account,risk,1,to_win,"wager",now(),wagers):
        logger.error("Unable to deduct account. Rolling Back.")
        raise Exception("Unable to put balance at risk!")

    return wObj


@transaction.atomic
def create_ml_bet(vhost,domain,match,account,risk,price,home_team=True,remote_addr=None):
    logger.info(f"Creating Moneyline Bet on {match} for Vh: {vhost}, Domain: {domain}, Account: {account}, Price: {price}: Risking {risk}: Home Team: {home_team}....")
    hierarchy = Hierarchy(vhost,**{"domain":domain,"match":match,"account":account,"home_team":match.home_team,"away_team":match.away_team})
    hierarchy.get_wager_limits()
    vb = validate_bet_risk(hierarchy, account, risk)
    if vb != 1:
        return vb
    to_win = calculate_moneyline_payout(risk,price)
    if hierarchy.get_payin_ratio() != 0:
        risk = risk * hierarchy.get_payin_ratio()
    logger.info(f"Payin ratio for this hierarchy/wager is: {hierarchy.get_payin_ratio()}, Final risk pay-in: {risk}...")
    logger.info(f"Final Wager to-win: {to_win}")
    if home_team:
        type = "ml-home-team"
        team = match.home_team
    else:
        type = "ml-away-team"
        team = match.away_team
    bet_data = {"ml":float(price),"to_win":float(to_win),"type":type,"team":str(team.uuid)}
    wObj = Wager.objects.create(uuid=uuid.uuid4(), account=account, team_1=team, match=match, risk=risk,
                                base_spread=match.base_line, bet_data=bet_data, win=to_win, type="ML", vhost=vhost)
    wObj.save()
    if remote_addr:
        wObj.current_ip = remote_addr
    wMObj = MatchWagers.objects.create(match=match, wager=wObj)
    wMObj.save()
    wagers = []
    wagers.append(str(wObj.uuid))
    if not account_risk_balance(account,risk,1,to_win,"wager",now(),wagers):
        logger.error("Unable to deduct account. Rolling Back.")
        raise Exception("Unable to put balance at risk!")

    return wObj
