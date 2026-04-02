from django.db.models import Q

GRADER_DAEMON_BASICWAGER_MODULES = {
    "ST":"grader.modules.straight_wager",
    "PA":"grader.modules.parlay_wager",
}
GRADER_DAEMON_BASICWAGER_MODULES_ASYNC = {
    "ST":"grader.modules.straight_wager_async",
    "PA":"grader.modules.parlay_wager_async",
}
GRADER_DAEMON_OUTCOME_FILTER_Q = Q(status_short="FT") | Q(status_long="Finished") | Q(is_end_segment=True) | Q(status_short="AOT") |Q(status_long="Match Finished") |Q(is_end_game=True) | Q(status_long="Retired") | Q(status_short="Retired")| Q(status_short="FINAL") | Q(is_end_game=True)

GRADER_MATCH_FINISHED_STATUS_SHORT = ['FT','AOT','Finished','Retired','FINAL','Final',"Cancelled","CANC","Walk-Over","AP","PPD","POST","OT"]
GRADER_MATCH_FINISHED_STATUS_LONG = ['Finished', "After Over Time", "Match Finished","Retired", "Final","FINAL","Cancelled","Walk-Over","After Penalties","Postponed","Overtime"]