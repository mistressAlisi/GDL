DROP VIEW IF EXISTS odds_match_h2h_h1_view;
CREATE VIEW odds_match_h2h_h1_view AS SELECT DISTINCT
	odds_match_h2h_h1.match_id as uuid,
	odds_match_h2h_h1.match_id,
	odds_match_h2h_h1.home_team_id,
	odds_match_h2h_h1.away_team_id,
	AVG(odds_match_h2h_h1.home_price) AS home_price,
	AVG(odds_match_h2h_h1.away_price) AS away_price
FROM
	odds_match_h2h_h1
GROUP BY
	odds_match_h2h_h1.match_id,
	odds_match_h2h_h1.home_team_id,
	odds_match_h2h_h1.away_team_id;

CREATE RULE no_delete AS ON DELETE TO odds_match_h2h_h1_view DO INSTEAD NOTHING;

DROP VIEW IF EXISTS odds_match_h2h_h2_view;
CREATE VIEW odds_match_h2h_h2_view AS SELECT DISTINCT
	odds_match_h2h_h2.match_id as uuid,
	odds_match_h2h_h2.match_id,
	odds_match_h2h_h2.home_team_id,
	odds_match_h2h_h2.away_team_id,
	AVG(odds_match_h2h_h2.home_price) AS home_price,
	AVG(odds_match_h2h_h2.away_price) AS away_price
FROM
	odds_match_h2h_h2
GROUP BY
	odds_match_h2h_h2.match_id,
	odds_match_h2h_h2.home_team_id,
	odds_match_h2h_h2.away_team_id;

CREATE RULE no_delete AS ON DELETE TO odds_match_h2h_h2_view DO INSTEAD NOTHING;

DROP VIEW IF EXISTS odds_match_h2h_q1_view;
CREATE VIEW odds_match_h2h_q1_view AS SELECT DISTINCT
	odds_match_h2h_q1.match_id as uuid,
	odds_match_h2h_q1.match_id,
	odds_match_h2h_q1.home_team_id,
	odds_match_h2h_q1.away_team_id,
	AVG(odds_match_h2h_q1.home_price) AS home_price,
	AVG(odds_match_h2h_q1.away_price) AS away_price
FROM
	odds_match_h2h_q1
GROUP BY
	odds_match_h2h_q1.match_id,
	odds_match_h2h_q1.home_team_id,
	odds_match_h2h_q1.away_team_id;

CREATE RULE no_delete AS ON DELETE TO odds_match_h2h_q1_view DO INSTEAD NOTHING;

DROP VIEW IF EXISTS odds_match_h2h_q2_view;
CREATE VIEW odds_match_h2h_q2_view AS SELECT DISTINCT
	odds_match_h2h_q2.match_id as uuid,
	odds_match_h2h_q2.match_id,
	odds_match_h2h_q2.home_team_id,
	odds_match_h2h_q2.away_team_id,
	AVG(odds_match_h2h_q2.home_price) AS home_price,
	AVG(odds_match_h2h_q2.away_price) AS away_price
FROM
	odds_match_h2h_q2
GROUP BY
	odds_match_h2h_q2.match_id,
	odds_match_h2h_q2.home_team_id,
	odds_match_h2h_q2.away_team_id;

CREATE RULE no_delete AS ON DELETE TO odds_match_h2h_q2_view DO INSTEAD NOTHING;


DROP VIEW IF EXISTS odds_match_h2h_q3_view;
CREATE VIEW odds_match_h2h_q3_view AS SELECT DISTINCT
	odds_match_h2h_q3.match_id as uuid,
	odds_match_h2h_q3.match_id,
	odds_match_h2h_q3.home_team_id,
	odds_match_h2h_q3.away_team_id,
	AVG(odds_match_h2h_q3.home_price) AS home_price,
	AVG(odds_match_h2h_q3.away_price) AS away_price
FROM
	odds_match_h2h_q3
GROUP BY
	odds_match_h2h_q3.match_id,
	odds_match_h2h_q3.home_team_id,
	odds_match_h2h_q3.away_team_id;

CREATE RULE no_delete AS ON DELETE TO odds_match_h2h_q3_view DO INSTEAD NOTHING;


DROP VIEW IF EXISTS odds_match_h2h_q4_view;
CREATE VIEW odds_match_h2h_q4_view AS SELECT DISTINCT
	odds_match_h2h_q4.match_id as uuid,
	odds_match_h2h_q4.match_id,
	odds_match_h2h_q4.home_team_id,
	odds_match_h2h_q4.away_team_id,
	AVG(odds_match_h2h_q4.home_price) AS home_price,
	AVG(odds_match_h2h_q4.away_price) AS away_price
FROM
	odds_match_h2h_q4
GROUP BY
	odds_match_h2h_q4.match_id,
	odds_match_h2h_q4.home_team_id,
	odds_match_h2h_q4.away_team_id;

CREATE RULE no_delete AS ON DELETE TO odds_match_h2h_q4_view DO INSTEAD NOTHING;