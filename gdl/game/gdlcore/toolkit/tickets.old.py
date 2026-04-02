import itertools

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


def _gdl_ticket_leg_factory(vhost,account,current_ip,matchObj,lineObj,type,**kwargs):
    gdlAppObj = AvailableApplication.objects.get(slug="gamedaylotto",studio__slug="solstic")
    wager_data = {
        "type":"PA",
        "current_ip": current_ip,
        "gdl_ticket":True,
        "match": matchObj,
        "bet_data": {
            "type": "straight",
            "mode": "parlay",
            "dynamic": True,
            "hierarchy": [str(lineObj.uuid)],
            }
        }
    if account.parlay_rules:
        wager_data["parlay_ruleset"] = account.parlay_rules
    if type == "home_price" or type == "home":
        wager_data["team_1"] = matchObj.home_team
    elif type == "away_price" or type == "away":
        wager_data["team_1"] = matchObj.away_team
    elif type == "draw_price" or type == "draw":
        wager_data["for_draw"] = True
    if "no_metrics" in kwargs:
        wager_data["no_metrics"] = True
    if "outcome_meta" in kwargs:
        wager_data["bet_data"]["outcome_meta"] = kwargs["outcome_meta"]
    wagerObj = create_application_wager(account,gdlAppObj,vhost,**wager_data)
    return wagerObj

    # wagerObj = Wager(
    #             account=account,
    #             type="PA",
    #             match=matchObj,
    #             current_ip=current_ip,
    #             gdl_ticket=True,
    #             application_type = gdlAppObj,
    #             bet_data={
    #                 "type": "straight",
    #                 "mode": "parlay",
    #                 "dynamic":True,
    #                 "hierarchy":[str(lineObj.uuid)]
    #             }
    #         )
    # if account.parlay_rules:
    #     wagerObj.parlay_ruleset = account.parlay_rules
    # if type == "home_price":
    #     wagerObj.team_1 = matchObj.home_team
    # elif type == "away_price":
    #     wagerObj.team_1 = matchObj.away_team
    # elif type == "draw_price":
    #     wagerObj.team_1 = matchObj.home_team
    #     wagerObj.for_draw = True


def create_gdl_ticket(vhost,account,current_ip,ticket_data):
    """
    Create a GameDayLotto Ticket with the specified parameters. The account must have at least the risk amount as balance.
    :param vhost: VHost Object
    :param account:  Account Object
    :param current_ip: Originating IP for transaction
    :param ticket_data: Ticket Data including matches=[],lines=[],types=[],stake,returns)
    :return:     Returns a Root_wager,nodes,node uuids tuple if successful, or a False,None,None if no balance.
    """
    nodes = []
    root_wager = None
    cashier = Cashier(account=account,vhost=vhost)
    # print(ticket_data)
    if ticket_data["stake"] > cashier.get_available_balance():
        return False,None,None
    for i in range(0,len(ticket_data["matches"]),1):
        matchObj = Match.objects.get(uuid=ticket_data["matches"][i])
        lineObj = MatchOddsSummary.objects.get(uuid=ticket_data["lines"][i])
        type = ticket_data["types"][i]
        if i == 0:
            root_wager = _gdl_ticket_leg_factory(vhost,account,current_ip,matchObj,lineObj,type,**{"risk":ticket_data["stake"],"win":ticket_data["returns"],"outcome_meta":ticket_data["outcome_meta"]})
        else:
            nodes.append(_gdl_ticket_leg_factory(vhost,account,current_ip,matchObj,lineObj,type,**{"no_metrics":True}))
    root_wager.bet_data["root_wager"] = True
    root_wager.risk = ticket_data["stake"]
    root_wager.win = ticket_data["returns"]
    ruleset = False
    if account.parlay_rules:
        # self.logger.info(f"Account {root_wager.account} has rules specified. Using this data.")
        ruleset = root_wager.account.parlay_rules
    elif account.account_level.parlay_ruleset:
        # self.logger.info(f"Account Level {root_wager.account.account_level} has rules specified. Using this data.")
        ruleset = root_wager.account.account_level.parlay_ruleset
    root_wager.ruleset = ruleset
    root_wager.save()
    wgt = MatchWagers.objects.get_or_create(wager=root_wager,match=root_wager.match)[0]
    wgt.save()
    nuuids = []
    for node in nodes:
        node.bet_data["parent"] = str(root_wager.uuid)
        node.hide_in_reports = True
        node.save()
        wgt = MatchWagers.objects.get_or_create(wager=node, match=node.match)[0]
        wgt.save()
        nuuids.append(str(node.uuid))
    root_wager.bet_data["nodes"] = nuuids
    root_wager.save()

    return root_wager,nodes,nuuids



def get_gdl_ticket(rootWagerObj,serialise=True,add_scores=False):
    ticketData = {
        "uuid": str(rootWagerObj.uuid),
        "matches": [],
        "wagers":[],
        "sports": [],
        "status":rootWagerObj.status,
        "mlen": 0,
        "returns": float(rootWagerObj.win),
        "stake": int(rootWagerObj.risk),
        "payload":str(rootWagerObj.uuid),
        "grade_outcome":rootWagerObj.get_grade_outcome_display(),

    }
    if add_scores:
        # oe = OutcomesEngine(rootWagerObj.vhost)
        home_score,away_score = get_live_match_scores_v2(rootWagerObj.match,False)
        # print("RS",home_score,away_score)
    else:
        rootScoreObj = None
    if serialise:
        ticketData["matches"].append(str(rootWagerObj.match.uuid))
        ticketData["wagers"].append(str(rootWagerObj.uuid))
    else:
        ticketData["matches"].append(rootWagerObj.match)
        if not add_scores:
            ticketData["wagers"].append(rootWagerObj)
        else:
            ticketData["wagers"].append([rootWagerObj,home_score,away_score])
    if serialise:
        ticketData["sports"].append(
            [str(rootWagerObj.match.sport.uuid), rootWagerObj.match.sport.title, rootWagerObj.match.sport.group.name, rootWagerObj.match.sport.group.icon])
    else:
        ticketData["sports"].append(rootWagerObj.match.sport)
    ticketData["mlen"] += 1
    for wager in rootWagerObj.bet_data["nodes"]:
        wagerObj = Wager.objects.get(uuid=wager)
        if add_scores:
            home_score,away_score = get_live_match_scores_v2(wagerObj.match,False)
        if serialise:
            ticketData["matches"].append(str(wagerObj.match.uuid))
            ticketData["wagers"].append(str(wagerObj.uuid))
        else:
            ticketData["matches"].append(wagerObj.match)
            if not add_scores:
                ticketData["wagers"].append(wagerObj)
            else:
                ticketData["wagers"].append([wagerObj,home_score,away_score])
        if serialise:
            ticketData["sports"].append(
                [str(wagerObj.match.sport.uuid), wagerObj.match.sport.title, wagerObj.match.sport.group.name,
                wagerObj.match.sport.group.icon])
        else:
            ticketData["sports"].append(wagerObj.match.sport)
        ticketData["mlen"] += 1
    # print(ticketData)
    return ticketData


def get_gdl_ticket_matches(rootWagerObj,ncol=5):
    tickets = []
    # tickets.append([rootWagerObj,rootWagerObj.match])
    for wager in [rootWagerObj.uuid]+rootWagerObj.bet_data["nodes"]:
        wagerObj = Wager.objects.get(uuid=wager)
        if wagerObj.match.final_score_consensus:
            scores = get_match_consensus_score(wagerObj.match)
            if not scores:
                scores = get_live_match_scores_v2(wagerObj.match)
        else:
            scores = get_live_match_scores_v2(wagerObj.match)
        tickets.append([wagerObj, wagerObj.match,scores])
    return list(itertools.batched(tickets,ncol))