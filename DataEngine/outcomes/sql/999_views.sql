DROP VIEW IF EXISTS outcomes_outcome_latest_team_score_view;

CREATE VIEW outcomes_outcome_latest_team_score_view AS
WITH latest_outcome AS (
    SELECT
        o.uuid,
        o.match_id,
        o.vhost_id,
        o.driver,
        o.outcome_id,
        o.clock,
        o.is_current,
        o.updated_on
    FROM outcomes_outcome o
    ORDER BY o.match_id, o.clock ASC, o.updated_on DESC
)
SELECT
    lo.uuid AS uuid,
    ot.is_winner,
    ot.team_id,
    t.name,
    ot.score,
    lo.outcome_id,
    lo.clock,
    lo.is_current,
    lo.match_id,
    lo.vhost_id,
    lo.driver,
    m.status_short,
    m.status_long,
    lo.updated_on
FROM latest_outcome lo
JOIN outcomes_outcometeams ot
    ON lo.uuid = ot.outcome_id
JOIN teams_team t
    ON t.uuid = ot.team_id
JOIN matches_match m
    ON lo.match_id = m.uuid
WHERE
    lo.clock = '00:00' or
    lo.clock = '08:40:00'


