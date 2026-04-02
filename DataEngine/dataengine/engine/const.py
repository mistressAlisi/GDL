from django.forms import model_to_dict

from dataengine.models import GroupSyncStatus, SportSyncStatus, TeamSyncStatus, SeasonSyncStatus, MatchSyncStatus, \
        OddsSyncStatus, SegmentSyncStatus, OutcomeSyncStatus, OutcomeSegmentScoreSyncStatus, OutcomeTeamsSyncStatus

SYSTEM_DATATYPE_MAP = {
        "group":GroupSyncStatus,
        "sport":SportSyncStatus,
        "team":TeamSyncStatus,
        "season":SeasonSyncStatus,
        "match":MatchSyncStatus,
        "ml_odds":OddsSyncStatus,
        "segment":SegmentSyncStatus,
        "outcome":OutcomeSyncStatus,
        "outcome_segment":OutcomeSegmentScoreSyncStatus,
        "outcome_team":OutcomeTeamsSyncStatus
}


