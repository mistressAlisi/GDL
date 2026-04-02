# rpc_registry.py
from matches.models import Match
from odds.models import MatchOddsSummary
from outcomes.models import Outcome, OutcomeSegmentScore, OutcomeTeams, OutcomeFinalMatchScores
from teams.models import Team, TeamSport
from sports.models import Sport, Country, Group, Season

RPC_MODEL_REGISTRY = {
    "teams.Team": Team,
    "teams.Sport": TeamSport,
    "sports.Sport": Sport,
    "sports.Group": Group,
    "sports.Country": Country,
    "sports.Season":Season,
    "matches.Match":Match,
    "outcomes.Outcome":Outcome,
}
CONSUMER_MODEL_MAPPING = {
    "match": Match,
    "odds_summary": MatchOddsSummary,
    "outcome_outcome": Outcome,
    "outcome_segment": OutcomeSegmentScore,
    "outcome_team": OutcomeTeams,
    "outcome_consensus": OutcomeFinalMatchScores,
}