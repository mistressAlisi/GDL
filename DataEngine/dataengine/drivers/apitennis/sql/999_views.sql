CREATE EXTENSION IF NOT EXISTS pg_trgm;
DROP VIEW IF EXISTS apitennis_fixture_view;
CREATE OR REPLACE VIEW apitennis_fixture_view AS
SELECT
    uuid,
    vhost_id,
    inserted_on,
    updated_on,
    event_key,
    event_date,
    event_time,
    commence_time,
    event_first_player_id,
    event_second_player_id,
    event_winner_id,
    event_status,
    event_type_id,
    tournament_id,
    tournament_round,
    tournament_season,
    scores,
    pointbypoint,
    event_qualification,
    event_live,
    statistics,
    -- Combine date + time into timestamp
    (event_date + event_time) AS event_datetime
FROM apitennis_fixture;
