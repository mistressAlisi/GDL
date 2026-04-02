
DROP VIEW IF EXISTS  matches_outcome_team_scores_view;
CREATE VIEW matches_outcome_team_scores_view AS  SELECT DISTINCT
	outcomes_outcome.uuid,
	outcomes_outcome.outcome_id,
	outcomes_outcometeams.routing_key as team_routing_key,
	outcomes_outcometeams.score,
	outcomes_outcometeams.inserted_on,
	outcomes_outcometeams.team_id,
	outcomes_outcome.clock,
	outcomes_outcome.is_current,
	outcomes_outcome.is_start_game,
	outcomes_outcome.is_start_segment,
	outcomes_outcome.is_end_segment,
	outcomes_outcome.state_id,
	teams_team."key" AS team_key,
	teams_team."name" AS team_name,
	matches_match.uuid As match_id,
	matches_match."name" AS match_name,
	matches_match.routing_key AS match_routing_key,
	matches_match.sport_id,
	matches_match.season_id,
	matches_match.away_team_id,
	matches_match.home_team_id,
	matches_match.draw,
	matches_match.final_score,
    outcomes_segment."name" AS segment_name,
	outcomes_segment.abrv AS segment_abrv,
	outcomes_outcome.segment_id

FROM
	outcomes_outcometeams
	INNER JOIN
	outcomes_outcome
	ON
		outcomes_outcometeams.outcome_id = outcomes_outcome.uuid
	INNER JOIN
	teams_team
	ON
		outcomes_outcometeams.team_id = teams_team.uuid
	INNER JOIN
	matches_match
	ON
		outcomes_outcome.match_id = matches_match.uuid
	INNER JOIN
	outcomes_segment
	ON
		outcomes_outcome.segment_id = outcomes_segment.uuid
