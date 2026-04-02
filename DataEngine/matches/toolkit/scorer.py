from django.contrib.postgres.search import TrigramSimilarity

from dataengine.consensus.daemon.builder import consensus_build_live_data_table
from outcomes.engine import OutcomesEngine
from outcomes.models import OutcomeSegmentScore, OutcomeTeams, Outcome, OutcomeTeamsLatestScoreView, \
    OutcomeFinalMatchScores

TRIGRAM_THRESHOLD = 0.55

def get_final_match_scores(match):
    oe = OutcomesEngine(match.vhost)
    home_score,away_score = oe.get_final_score_frontend(match)
    # print(home_score,away_score)
    retr = {
        "match":match,
        "home_team": {"team":match.home_team,"score":home_score},
        "away_team": {"team": match.away_team, "score": away_score},
        "winner":match.winner,
        "status_long":match.status_long,
        "status_short":match.status_short,
    }
    # print(retr)
    return retr


def get_live_match_scores(match):
    oe = OutcomesEngine(match.vhost)
    home_score,away_score,status = oe.get_score_frontend(match)
    # print(home_score,away_score)

    retr = {
        "match":match,
        "home_team": {"team":match.home_team,"score":home_score},
        "away_team": {"team": match.away_team, "score": away_score},
        "status_long":match.status_long,
        "status_short":match.status_short,
    }
    return retr

def get_match_consensus_score(match,format=True):
    try:
        finalScoreObj = OutcomeFinalMatchScores.objects.get(match=match)
    except OutcomeFinalMatchScores.DoesNotExist:
        return False
    except OutcomeFinalMatchScores.MultipleObjectsReturned:
        finalScoreObj = OutcomeFinalMatchScores.objects.filter(match=match).first()
    if not format:
        return finalScoreObj.home_team_score,finalScoreObj.away_team_score
    retr = {
        "match": match,
        "home_team": {"team": match.home_team, "score": finalScoreObj.home_team_score},
        "away_team": {"team": match.away_team, "score": finalScoreObj.away_team_score},
        "status_long": "Final Score",
        "status_short": "FT"
    }
    return retr



def get_live_match_scores_v2(match,format=True):
    home_scores = []
    away_scores = []
    home_score = 0
    away_score = 0
    status_long = match.status_long
    status_short = match.status_short
    data_table = consensus_build_live_data_table(match)
    for k,v in data_table.items():
        if v["home_score"] and v["home_score"] != "":
            home_scores.append(v["home_score"])

        if v["away_score"] and v["away_score"] != "":
            away_scores.append(v["away_score"])
        if v["status_short"] and v["status_short"] != "UP":
            status_short = v["status_short"]
        if v["status_long"] and v["status_long"] != "Upcoming":
            status_long = v["status_long"]

    # Just a test:
    if len(home_scores) == 0:
        home_score = 0

    else:
        home_score = max(home_scores)
    if len(away_scores) == 0:
        away_score = 0

    else:
        away_score = min(away_scores)
    if format:
        retr = {
            "match":match,
            "home_team": {"team":match.home_team,"score":home_score},
            "away_team": {"team": match.away_team, "score": away_score},
            "status_long":status_long,
            "status_short":status_short,
        }
        return retr
    else:
        return home_score,away_score

