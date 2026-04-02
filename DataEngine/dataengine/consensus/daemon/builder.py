from uuid import UUID

from django.contrib.postgres.search import TrigramSimilarity
from django.db.models import Q

from outcomes.models import OutcomeTeamsLatestScoreView, Outcome, OutcomeSegmentScore, OutcomeTeams
RENAME_TABLE = {
    "apisports.match.babgame":"apisports",
    "apisports.match.fballgame":"apisports",
    "apisports.match.amfgame":"apisports",
    "apisports.match.basegame":"apisports",
    "apisports.match.hockgame":"apisports",
    "apisports.match.*":"apisports",
    "kiblio.fixture.Fixture":"kibl",
    "dataengine.drivers.kiblio":"kibl",
    "apitennis.fixture.Fixture":"apitennis",
    "goalserve.match.baseballfixture": "goalserve",
    "goalserve.match.fballgame": "goalserve",
    "goalserve.match.amfgame": "goalserve",
    "goalserve.match.basketballfixture": "goalserve",
    "goalserve.match.soccerfixture": "goalserve",
    "goalserve.match.hockgame": "goalserve",
    "goalserve.match.TennisFixture": "goalserve",
    "manual":"manual"
}
from rapidfuzz import fuzz

FUZZ_THRESHOLD = 60

def resolve_team_scores(
    sys_home_team,
    sys_away_team,
    team_objs,
    logger=None,
):
    """
    Returns (home_score, away_score, flipped)
    flipped:
        False -> normal
        True  -> flipped
        None  -> ambiguous
    """

    if len(team_objs) < 2:
        return None, None, None

    # Extract names once
    sys_home_name = sys_home_team.name
    sys_away_name = sys_away_team.name

    team_a, team_b = team_objs[0], team_objs[1]
    name_a = team_a.team.name
    name_b = team_b.team.name

    # Similarities
    sim_home_a = fuzz.partial_ratio(sys_home_name, name_a)
    sim_home_b = fuzz.partial_ratio(sys_home_name, name_b)
    sim_away_a = fuzz.partial_ratio(sys_away_name, name_a)
    sim_away_b = fuzz.partial_ratio(sys_away_name, name_b)

    mappingA_score = sim_home_a + sim_away_b  # home->A, away->B
    mappingB_score = sim_home_b + sim_away_a  # home->B, away->A

    if mappingA_score >= mappingB_score and mappingA_score >= 2 * FUZZ_THRESHOLD:
        return team_a.score, team_b.score, False

    if mappingB_score > mappingA_score and mappingB_score >= 2 * FUZZ_THRESHOLD:
        return team_b.score, team_a.score, True

    if logger:
        logger.warning(
            f"[CONSENSUS] Ambiguous team mapping "  
            f"(A={mappingA_score}, B={mappingB_score}) "
            f"sys_home='{sys_home_name}', sys_away='{sys_away_name}', "
            f"teams='{name_a}', '{name_b}'"
        )

    return None, None, None

def consensus_build_data_table(matchObj):
    consensus_table = {}

    outcomes = (
        Outcome.objects
        .using("default")
        .filter(match=matchObj, is_end_game=True)
        .select_related()
    )

    for outObj in outcomes:
        key = RENAME_TABLE[outObj.driver]

        base_payload = {
            "is_end_game": outObj.is_end_game,
            "is_end_segment": outObj.is_end_segment,
            "status_short": outObj.status_short,
            "status_long": outObj.status_long,
        }

        # ---------------------------------------------------
        # Fast path: explicit final scores
        # ---------------------------------------------------
        if outObj.last_home_score is not None and outObj.last_away_score is not None:
            consensus_table[key] = {
                **base_payload,
                "home_score": float(outObj.last_home_score),
                "away_score": float(outObj.last_away_score),
            }
            continue

        # ---------------------------------------------------
        # Fallback: fuzzy team resolution
        # ---------------------------------------------------
        team_objs = list(
            OutcomeTeams.objects
            .using("default")
            .filter(outcome=outObj)
            .select_related("team")
        )

        home_score, away_score, flipped = resolve_team_scores(
            sys_home_team=matchObj.home_team,
            sys_away_team=matchObj.away_team,
            team_objs=team_objs,
            logger=getattr(matchObj, "logger", None),
        )

        consensus_table[key] = {
            **base_payload,
            "home_score": (
                float(home_score) if home_score is not None else None
            ),
            "away_score": (
                float(away_score) if away_score is not None else None
            ),
            # Optional but useful for debugging / audits
            "flipped": flipped,
        }

    return consensus_table



def consensus_build_live_data_table(matchObj):
    consensus_table = {}

    outcomes = (
        Outcome.objects
        .using("default")
        .filter(match=matchObj, is_current=True)
        .select_related()
    )

    for outObj in outcomes:
        key = RENAME_TABLE[outObj.driver]

        base_payload = {
            "is_end_segment": outObj.is_end_segment,
            "is_end_game": outObj.is_end_game,
            "status_short": outObj.status_short,
            "status_long": outObj.status_long,
            "outcome": outObj.uuid,
        }

        # ---------------------------------------------------
        # Fast path: direct scores already resolved
        # ---------------------------------------------------
        if outObj.last_home_score is not None and outObj.last_away_score is not None:
            consensus_table[key] = {
                **base_payload,
                "home_score": float(outObj.last_home_score),
                "away_score": float(outObj.last_away_score),
            }
            continue

        # ---------------------------------------------------
        # Fallback: fuzzy team resolution
        # ---------------------------------------------------
        team_objs = list(
            OutcomeTeams.objects
            .using("default")
            .filter(outcome=outObj)
            .select_related("team")
        )

        home_score, away_score, flipped = resolve_team_scores(
            sys_home_team=matchObj.home_team,
            sys_away_team=matchObj.away_team,
            team_objs=team_objs,
            logger=getattr(matchObj, "logger", None),
        )

        consensus_table[key] = {
            **base_payload,
            "home_score": home_score,
            "away_score": away_score,
            "flipped": flipped,
        }

    return consensus_table
