DROP VIEW IF EXISTS odds_match_totals_h1_view;
CREATE VIEW odds_match_totals_h1_view AS SELECT DISTINCT
	odds_match_totals_h1.match_id as uuid,
	odds_match_totals_h1.match_id,
	AVG(odds_match_totals_h1.over_price) AS over_price,
	AVG(odds_match_totals_h1.under_price) AS under_price,
    AVG(odds_match_totals_h1.over_point) AS over_point,
	AVG(odds_match_totals_h1.under_point) AS under_point
FROM
	odds_match_totals_h1
GROUP BY
	odds_match_totals_h1.match_id;
CREATE RULE no_delete AS ON DELETE TO odds_match_totals_h1_view DO INSTEAD NOTHING;

DROP VIEW IF EXISTS odds_match_totals_h2_view;
CREATE VIEW odds_match_totals_h2_view AS SELECT DISTINCT
	odds_match_totals_h2.match_id as uuid,
	odds_match_totals_h2.match_id,
	AVG(odds_match_totals_h2.over_price) AS over_price,
	AVG(odds_match_totals_h2.under_price) AS under_price,
    AVG(odds_match_totals_h2.over_point) AS over_point,
	AVG(odds_match_totals_h2.under_point) AS under_point
FROM
	odds_match_totals_h2
GROUP BY
	odds_match_totals_h2.match_id;
CREATE RULE no_delete AS ON DELETE TO odds_match_totals_h2_view DO INSTEAD NOTHING;

DROP VIEW IF EXISTS odds_match_totals_q1_view;
CREATE VIEW odds_match_totals_q1_view AS SELECT DISTINCT
	odds_match_totals_q1.match_id as uuid,
	odds_match_totals_q1.match_id,
	AVG(odds_match_totals_q1.over_price) AS over_price,
	AVG(odds_match_totals_q1.under_price) AS under_price,
    AVG(odds_match_totals_q1.over_point) AS over_point,
	AVG(odds_match_totals_q1.under_point) AS under_point
FROM
	odds_match_totals_q1
GROUP BY
	odds_match_totals_q1.match_id;
CREATE RULE no_delete AS ON DELETE TO odds_match_totals_q1_view DO INSTEAD NOTHING;

DROP VIEW IF EXISTS odds_match_totals_q2_view;
CREATE VIEW odds_match_totals_q2_view AS SELECT DISTINCT
	odds_match_totals_q2.match_id as uuid,
	odds_match_totals_q2.match_id,
	AVG(odds_match_totals_q2.over_price) AS over_price,
	AVG(odds_match_totals_q2.under_price) AS under_price,
    AVG(odds_match_totals_q2.over_point) AS over_point,
	AVG(odds_match_totals_q2.under_point) AS under_point
FROM
	odds_match_totals_q2
GROUP BY
	odds_match_totals_q2.match_id;
CREATE RULE no_delete AS ON DELETE TO odds_match_totals_q2_view DO INSTEAD NOTHING;

DROP VIEW IF EXISTS odds_match_totals_q3_view;
CREATE VIEW odds_match_totals_q3_view AS SELECT DISTINCT
	odds_match_totals_q3.match_id as uuid,
	odds_match_totals_q3.match_id,
	AVG(odds_match_totals_q3.over_price) AS over_price,
	AVG(odds_match_totals_q3.under_price) AS under_price,
    AVG(odds_match_totals_q3.over_point) AS over_point,
	AVG(odds_match_totals_q3.under_point) AS under_point
FROM
	odds_match_totals_q3
GROUP BY
	odds_match_totals_q3.match_id;
CREATE RULE no_delete AS ON DELETE TO odds_match_totals_q3_view DO INSTEAD NOTHING;

DROP VIEW IF EXISTS odds_match_totals_q4_view;
CREATE VIEW odds_match_totals_q4_view AS SELECT DISTINCT
	odds_match_totals_q4.match_id as uuid,
	odds_match_totals_q4.match_id,
	AVG(odds_match_totals_q4.over_price) AS over_price,
	AVG(odds_match_totals_q4.under_price) AS under_price,
    AVG(odds_match_totals_q4.over_point) AS over_point,
	AVG(odds_match_totals_q4.under_point) AS under_point
FROM
	odds_match_totals_q4
GROUP BY
	odds_match_totals_q4.match_id;
CREATE RULE no_delete AS ON DELETE TO odds_match_totals_q4_view DO INSTEAD NOTHING;

DROP VIEW IF EXISTS odds_match_team_totals_q1_view;
CREATE VIEW odds_match_team_totals_q1_view AS SELECT DISTINCT
	odds_match_team_totals_q1.match_id as uuid,
	odds_match_team_totals_q1.match_id,
	odds_match_team_totals_q1.team_id,
	AVG(odds_match_team_totals_q1.over_price) AS over_price,
	AVG(odds_match_team_totals_q1.under_price) AS under_price,
    AVG(odds_match_team_totals_q1.over_point) AS over_point,
	AVG(odds_match_team_totals_q1.under_point) AS under_point
FROM
	odds_match_team_totals_q1
GROUP BY
    odds_match_team_totals_q1.team_id,
	odds_match_team_totals_q1.match_id;
CREATE RULE no_delete AS ON DELETE TO odds_match_team_totals_q1_view DO INSTEAD NOTHING;

DROP VIEW IF EXISTS odds_match_team_totals_q2_view;
CREATE VIEW odds_match_team_totals_q2_view AS SELECT DISTINCT
	odds_match_team_totals_q2.match_id as uuid,
	odds_match_team_totals_q2.match_id,
	odds_match_team_totals_q2.team_id,
	AVG(odds_match_team_totals_q2.over_price) AS over_price,
	AVG(odds_match_team_totals_q2.under_price) AS under_price,
    AVG(odds_match_team_totals_q2.over_point) AS over_point,
	AVG(odds_match_team_totals_q2.under_point) AS under_point
FROM
	odds_match_team_totals_q2
GROUP BY
	odds_match_team_totals_q2.team_id,
    odds_match_team_totals_q2.match_id;
CREATE RULE no_delete AS ON DELETE TO odds_match_team_totals_q2_view DO INSTEAD NOTHING;

DROP VIEW IF EXISTS odds_match_team_totals_q3_view;
CREATE VIEW odds_match_team_totals_q3_view AS SELECT DISTINCT
	odds_match_team_totals_q3.match_id as uuid,
	odds_match_team_totals_q3.match_id,
	odds_match_team_totals_q3.team_id,
	AVG(odds_match_team_totals_q3.over_price) AS over_price,
	AVG(odds_match_team_totals_q3.under_price) AS under_price,
    AVG(odds_match_team_totals_q3.over_point) AS over_point,
	AVG(odds_match_team_totals_q3.under_point) AS under_point
FROM
	odds_match_team_totals_q3
GROUP BY
    odds_match_team_totals_q3.team_id,
	odds_match_team_totals_q3.match_id;
CREATE RULE no_delete AS ON DELETE TO odds_match_team_totals_q3_view DO INSTEAD NOTHING;


DROP VIEW IF EXISTS odds_match_team_totals_q4_view;
CREATE VIEW odds_match_team_totals_q4_view AS SELECT DISTINCT
	odds_match_team_totals_q4.match_id as uuid,
	odds_match_team_totals_q4.match_id,
	odds_match_team_totals_q4.team_id,
	AVG(odds_match_team_totals_q4.over_price) AS over_price,
	AVG(odds_match_team_totals_q4.under_price) AS under_price,
    AVG(odds_match_team_totals_q4.over_point) AS over_point,
	AVG(odds_match_team_totals_q4.under_point) AS under_point
FROM
	odds_match_team_totals_q4
GROUP BY
    odds_match_team_totals_q4.team_id,
	odds_match_team_totals_q4.match_id;
CREATE RULE no_delete AS ON DELETE TO odds_match_team_totals_q4_view DO INSTEAD NOTHING;
