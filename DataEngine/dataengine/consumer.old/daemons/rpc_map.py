TEAM_RPC_FIELD_MAP = {
    "uuid": "uuid",
    "key": "key",
    "apisports_id": "apisports_id",
    "name": "name",
    "total_games": "total_games",
    "total_wins": "total_wins",
    "total_losses": "total_losses",
    "total_draws": "total_draws",
    "last_game": "last_game",
    "flag": "flag",
    "city": "city",
    "owner": "owner",
    "stadium": "stadium",
    "established": "established",
    "team_colour_primary": "team_colour_primary",
    "team_colour_secondary": "team_colour_secondary",
    "team_colour_tertiary": "team_colour_tertiary",
}

TEAM_FILE_FIELDS = {
    "card_logo": "card_logo",
    "large_logo": "large_logo",
}

SPORT_RPC_FIELD_MAP = {
    # -------------------------
    # Identity / core
    # -------------------------
    "uuid": "uuid",
    "key": "key",
    "title": "title",

    # -------------------------
    # External IDs
    # -------------------------
    "apisport_id": "apisport_id",
    "apitennis_id": "apitennis_id",

    # -------------------------
    # Text / description
    # -------------------------
    "description": "description",

    # -------------------------
    # Flags
    # -------------------------
    "active": "active",
    "featured": "featured",
    "has_outrights": "has_outrights",
    "has_wagers": "has_wagers",
    "skip_index_display": "skip_index_display",

    # -------------------------
    # Ordering / limits
    # -------------------------
    "priority": "priority",
    "wager_limit": "wager_limit",
    "min_wager": "min_wager",

    # -------------------------
    # Dates
    # -------------------------
    "start_date": "start_date",
    "end_date": "end_date",
}
SPORT_FILE_FIELDS = {
    "card_logo": "card_logo",
    "large_logo": "large_logo",
}

GROUP_RPC_FIELD_MAP = {
    # -------------------------
    # Identity
    # -------------------------
    "uuid": "uuid",
    "slug": "slug",
    "name": "name",

    # -------------------------
    # Icons / UI
    # -------------------------
    "icon": "icon",
    "generic_icon": "generic_icon",

    # -------------------------
    # Flags
    # -------------------------
    "has_periods": "has_periods",
    "has_teasers": "has_teasers",
    "bookmaker_uses_own_template": "bookmaker_uses_own_template",
    "active": "active",

    # -------------------------
    # Teaser config
    # -------------------------
    "teaser_pts_mask": "teaser_pts_mask",
}

COUNTRY_RPC_FIELD_MAP = {
    # -------------------------
    # Identity
    # -------------------------
    "uuid": "uuid",
    "name": "name",
    "code": "code",

    # -------------------------
    # UI
    # -------------------------
    "icon": "icon",
}
COUNTRY_FILE_FIELDS = {
    "flag": "flag",
}

SEASON_RPC_FIELD_MAP = {
    # -------------------------
    # Identity
    # -------------------------
    "uuid": "uuid",
    "name": "name",
    "season_key": "season_key",

}

MATCH_RPC_FIELD_MAP = {
    # -------------------------
    # Identity / routing
    # -------------------------
    "uuid": "uuid",
    "id": "id",
    "routing_key": "routing_key",
    "apiid": "apiid",
    "name": "name",
    # -------------------------
    # Match metadata
    # -------------------------
    "stage": "stage",
    "week": "week",
    "city": "city",
    "venue": "venue",
    "status_short": "status_short",
    "status_long": "status_long",
    "clock": "clock",
    "commence_time": "commence_time",
    "match_stage": "match_stage",
    "updated": "updated",
    "last_update": "last_update",
    # -------------------------
    # State flags
    # -------------------------
    "is_outrights": "is_outrights",
    "finished": "finished",
    "finished_at": "finished_at",
    "open": "open",
    "active": "active",
    "draw": "draw",
    "being_updated": "being_updated",
    "live_events": "live_events",
    "score_closed": "score_closed",
    "events_fetched": "events_fetched",
    "stats_fetched": "stats_fetched",
    "wagers_graded": "wagers_graded",
    "wagers_paid": "wagers_paid",
    "in_play": "in_play",
    "manual_data": "manual_data",
    # -------------------------
    # Scoring / wagering
    # -------------------------
    "base_line": "base_line",
    "point_purchase_spread": "point_purchase_spread",
    "final_score": "final_score",
    "final_score_consensus": "final_score_consensus",
    "scoring_data": "scoring_data",
    # -------------------------
    # Tournament / bracket
    # -------------------------
    "is_tournament_match": "is_tournament_match",
    "tournament_round": "tournament_round",
    "bracket_position": "bracket_position",
}

MATCH_ODDS_SUMMARY_RPC_FIELD_MAP = {
    "uuid": "uuid",

    # bookkeeping
    "driver": "driver",
    "last_update": "last_update",
    "created_at": "created_at",
    "updated_at": "updated_at",

    # prices
    "home_price": "home_price",
    "home_price_fraction": "home_price_fraction",
    "away_price": "away_price",
    "away_price_fraction": "away_price_fraction",
    "draw_price": "draw_price",
    "draw_price_fraction": "draw_price_fraction",
}

OUTCOME_SEGMENT_SCORE_RPC_FIELD_MAP = {
    "uuid": "uuid",

    # segmentation / routing
    "segment": "segment",
    "driver": "driver",
    "routing_key": "routing_key",

    # scoring
    "score": "score",
    "is_winner": "is_winner",

    # lifecycle
    "inserted_on": "inserted_on",
    "updated_at": "updated_at",

    # external state
    "state_id": "state_id",
}

OUTCOME_TEAMS_RPC_FIELD_MAP = {
    "uuid": "uuid",

    # routing / metadata
    "driver": "driver",
    "routing_key": "routing_key",

    # scoring
    "score": "score",
    "is_winner": "is_winner",

    # lifecycle
    "inserted_on": "inserted_on",
    "updated_at": "updated_at",
}

OUTCOME_FINAL_MATCH_SCORES_RPC_FIELD_MAP = {
    "uuid": "uuid",

    # result flags
    "draw": "draw",
    "manual": "manual",

    # scores
    "home_team_score": "home_team_score",
    "away_team_score": "away_team_score",

    # metadata
    "consensus_data": "consensus_data",

    # lifecycle
    "created_at": "created_at",
    "updated_at": "updated_at",
}

OUTCOME_RPC_FIELD_MAP = {
    "uuid": "uuid",

    # identity / routing
    "segment": "segment",
    "driver": "driver",
    "outcome_id": "outcome_id",
    "routing_key": "routing_key",

    # status / clock
    "clock": "clock",
    "status_short": "status_short",
    "status_long": "status_long",

    # state flags
    "is_current": "is_current",
    "is_start_game": "is_start_game",
    "is_end_game": "is_end_game",
    "is_start_segment": "is_start_segment",
    "is_end_segment": "is_end_segment",

    # scores
    "last_home_score": "last_home_score",
    "last_away_score": "last_away_score",

    # lifecycle
    "inserted_on": "inserted_on",
    "updated_on": "updated_on",

    # state machine
    "state_id": "state_id",
}

TEAM_SPORT_RPC_FIELD_MAP = {
    "active": "active",
}