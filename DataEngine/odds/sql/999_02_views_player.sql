--- American Football ---
DROP VIEW IF EXISTS odds_match_first_td_view;
CREATE VIEW odds_match_first_td_view AS SELECT DISTINCT
	odds_match_first_td.match_id as uuid,
	odds_match_first_td.match_id,
	odds_match_first_td.player_id,
	AVG(odds_match_first_td.price) AS price
FROM
	odds_match_first_td
GROUP BY
	odds_match_first_td.match_id,
	odds_match_first_td.player_id;

CREATE RULE no_delete AS ON DELETE TO odds_match_first_td_view DO INSTEAD NOTHING;


DROP VIEW IF EXISTS odds_match_anytime_td_view;
CREATE VIEW odds_match_anytime_td_view AS SELECT DISTINCT
	odds_match_anytime_td.match_id as uuid,
	odds_match_anytime_td.match_id,
	odds_match_anytime_td.player_id,
	AVG(odds_match_anytime_td.price) AS price
FROM
	odds_match_anytime_td
GROUP BY
	odds_match_anytime_td.match_id,
	odds_match_anytime_td.player_id;

CREATE RULE no_delete AS ON DELETE TO odds_match_anytime_td_view DO INSTEAD NOTHING;


DROP VIEW IF EXISTS odds_match_last_td_view;
CREATE VIEW odds_match_last_td_view AS SELECT DISTINCT
	odds_match_last_td.match_id as uuid,
	odds_match_last_td.match_id,
	odds_match_last_td.player_id,
	AVG(odds_match_last_td.price) AS price
FROM
	odds_match_last_td
GROUP BY
	odds_match_last_td.match_id,
	odds_match_last_td.player_id;

CREATE RULE no_delete AS ON DELETE TO odds_match_last_td_view DO INSTEAD NOTHING;


DROP VIEW IF EXISTS odds_match_pass_td_view;
CREATE VIEW odds_match_pass_td_view AS SELECT DISTINCT
	odds_match_pass_td.match_id as uuid,
	odds_match_pass_td.match_id,
	odds_match_pass_td.player_id,
	odds_match_pass_td.type,
	AVG(odds_match_pass_td.price) AS price,
	AVG(odds_match_pass_td.point) AS point
FROM
	odds_match_pass_td
GROUP BY
	odds_match_pass_td.match_id,
	odds_match_pass_td.type,
	odds_match_pass_td.player_id;

CREATE RULE no_delete AS ON DELETE TO odds_match_pass_td_view DO INSTEAD NOTHING;

DROP VIEW IF EXISTS odds_match_pass_yds_view;
CREATE VIEW odds_match_pass_yds_view AS SELECT DISTINCT
	odds_match_pass_yds.match_id as uuid,
	odds_match_pass_yds.match_id,
	odds_match_pass_yds.player_id,
	odds_match_pass_yds.type,
	AVG(odds_match_pass_yds.price) AS price,
	AVG(odds_match_pass_yds.point) AS point
FROM
	odds_match_pass_yds
GROUP BY
	odds_match_pass_yds.match_id,
	odds_match_pass_yds.type,
	odds_match_pass_yds.player_id;
CREATE RULE no_delete AS ON DELETE TO odds_match_pass_yds_view DO INSTEAD NOTHING;

DROP VIEW IF EXISTS odds_match_reception_view;
CREATE VIEW odds_match_reception_view AS SELECT DISTINCT
	odds_match_reception.match_id as uuid,
	odds_match_reception.match_id,
	odds_match_reception.player_id,
	odds_match_reception.type,
	AVG(odds_match_reception.price) AS price,
	AVG(odds_match_reception.point) AS point
FROM
	odds_match_reception
GROUP BY
	odds_match_reception.match_id,
	odds_match_reception.type,
	odds_match_reception.player_id;
CREATE RULE no_delete AS ON DELETE TO odds_match_reception_view DO INSTEAD NOTHING;

DROP VIEW IF EXISTS odds_match_reception_yds_view;
CREATE VIEW odds_match_reception_yds_view AS SELECT DISTINCT
	odds_match_reception_yds.match_id as uuid,
	odds_match_reception_yds.match_id,
	odds_match_reception_yds.player_id,
	odds_match_reception_yds.type,
	AVG(odds_match_reception_yds.price) AS price,
	AVG(odds_match_reception_yds.point) AS point
FROM
	odds_match_reception_yds
GROUP BY
	odds_match_reception_yds.match_id,
	odds_match_reception_yds.type,
	odds_match_reception_yds.player_id;
CREATE RULE no_delete AS ON DELETE TO odds_match_reception_yds_view DO INSTEAD NOTHING;

DROP VIEW IF EXISTS odds_match_reception_longest_view;
CREATE VIEW odds_match_reception_longest_view AS SELECT DISTINCT
	odds_match_reception_longest.match_id as uuid,
	odds_match_reception_longest.match_id,
	odds_match_reception_longest.player_id,
	odds_match_reception_longest.type,
	AVG(odds_match_reception_longest.price) AS price,
	AVG(odds_match_reception_longest.point) AS point
FROM
	odds_match_reception_longest
GROUP BY
	odds_match_reception_longest.match_id,
	odds_match_reception_longest.type,
	odds_match_reception_longest.player_id;
CREATE RULE no_delete AS ON DELETE TO odds_match_reception_longest_view DO INSTEAD NOTHING;

DROP VIEW IF EXISTS odds_match_rush_yds_view;
CREATE VIEW odds_match_rush_yds_view AS SELECT DISTINCT
	odds_match_rush_yds.match_id as uuid,
	odds_match_rush_yds.match_id,
	odds_match_rush_yds.player_id,
	odds_match_rush_yds.type,
	AVG(odds_match_rush_yds.price) AS price,
	AVG(odds_match_rush_yds.point) AS point
FROM
	odds_match_rush_yds
GROUP BY
	odds_match_rush_yds.match_id,
	odds_match_rush_yds.type,
	odds_match_rush_yds.player_id;
CREATE RULE no_delete AS ON DELETE TO odds_match_rush_yds_view DO INSTEAD NOTHING;

DROP VIEW IF EXISTS odds_match_td_over_view;
CREATE VIEW odds_match_td_over_view AS SELECT DISTINCT
	odds_match_td_over.match_id as uuid,
	odds_match_td_over.match_id,
	odds_match_td_over.player_id,
	AVG(odds_match_td_over.price) AS price
FROM
	odds_match_td_over
GROUP BY
	odds_match_td_over.match_id,
	odds_match_td_over.player_id;
CREATE RULE no_delete AS ON DELETE TO odds_match_td_over_view DO INSTEAD NOTHING;

--- Basketball ---
DROP VIEW IF EXISTS odds_match_player_assists_view;
CREATE VIEW odds_match_player_assists_view AS SELECT DISTINCT
	odds_match_player_assists.match_id as uuid,
	odds_match_player_assists.match_id,
	odds_match_player_assists.player_id,
	odds_match_player_assists.type,
	AVG(odds_match_player_assists.price) AS price,
	AVG(odds_match_player_assists.point) AS point
FROM
	odds_match_player_assists
GROUP BY
	odds_match_player_assists.match_id,
	odds_match_player_assists.type,
	odds_match_player_assists.player_id;
CREATE RULE no_delete AS ON DELETE TO odds_match_player_assists_view DO INSTEAD NOTHING;

DROP VIEW IF EXISTS odds_match_player_blocks_view;
CREATE VIEW odds_match_player_blocks_view AS SELECT DISTINCT
	odds_match_player_blocks.match_id as uuid,
	odds_match_player_blocks.match_id,
	odds_match_player_blocks.player_id,
	odds_match_player_blocks.type,
	AVG(odds_match_player_blocks.price) AS price,
	AVG(odds_match_player_blocks.point) AS point
FROM
	odds_match_player_blocks
GROUP BY
	odds_match_player_blocks.match_id,
	odds_match_player_blocks.type,
	odds_match_player_blocks.player_id;
CREATE RULE no_delete AS ON DELETE TO odds_match_player_blocks_view DO INSTEAD NOTHING;

DROP VIEW IF EXISTS odds_match_player_block_steals_view;
CREATE VIEW odds_match_player_block_steals_view AS SELECT DISTINCT
	odds_match_player_block_steals.match_id as uuid,
	odds_match_player_block_steals.match_id,
	odds_match_player_block_steals.player_id,
	odds_match_player_block_steals.type,
	AVG(odds_match_player_block_steals.price) AS price,
	AVG(odds_match_player_block_steals.point) AS point
FROM
	odds_match_player_block_steals
GROUP BY
	odds_match_player_block_steals.match_id,
	odds_match_player_block_steals.type,
	odds_match_player_block_steals.player_id;
CREATE RULE no_delete AS ON DELETE TO odds_match_player_block_steals_view DO INSTEAD NOTHING;

DROP VIEW IF EXISTS odds_match_player_double_double_view;
CREATE VIEW odds_match_player_double_double_view AS SELECT DISTINCT
	odds_match_player_double_double.match_id as uuid,
	odds_match_player_double_double.match_id,
	odds_match_player_double_double.player_id,
	AVG(odds_match_player_double_double.price) AS price
FROM
	odds_match_player_double_double
GROUP BY
	odds_match_player_double_double.match_id,
	odds_match_player_double_double.player_id;
CREATE RULE no_delete AS ON DELETE TO odds_match_player_double_double_view DO INSTEAD NOTHING;

DROP VIEW IF EXISTS odds_match_player_first_basket_view;
CREATE VIEW odds_match_player_first_basket_view AS SELECT DISTINCT
	odds_match_player_first_basket.match_id as uuid,
	odds_match_player_first_basket.match_id,
	odds_match_player_first_basket.player_id,
	AVG(odds_match_player_first_basket.price) AS price
FROM
	odds_match_player_first_basket
GROUP BY
	odds_match_player_first_basket.match_id,
	odds_match_player_first_basket.player_id;
CREATE RULE no_delete AS ON DELETE TO odds_match_player_first_basket_view DO INSTEAD NOTHING;

DROP VIEW IF EXISTS odds_match_player_points_view;
CREATE VIEW odds_match_player_points_view AS SELECT DISTINCT
	odds_match_player_points.match_id as uuid,
	odds_match_player_points.match_id,
	odds_match_player_points.player_id,
	odds_match_player_points.type,
	AVG(odds_match_player_points.price) AS price,
	AVG(odds_match_player_points.point) AS point
FROM
	odds_match_player_points
GROUP BY
	odds_match_player_points.match_id,
	odds_match_player_points.type,
	odds_match_player_points.player_id;
CREATE RULE no_delete AS ON DELETE TO odds_match_player_points_view DO INSTEAD NOTHING;

DROP VIEW IF EXISTS odds_match_player_points_assists_view;
CREATE VIEW odds_match_player_points_assists_view AS SELECT DISTINCT
	odds_match_player_points_assists.match_id as uuid,
	odds_match_player_points_assists.match_id,
	odds_match_player_points_assists.player_id,
	odds_match_player_points_assists.type,
	AVG(odds_match_player_points_assists.price) AS price,
	AVG(odds_match_player_points_assists.point) AS point
FROM
	odds_match_player_points_assists
GROUP BY
	odds_match_player_points_assists.match_id,
	odds_match_player_points_assists.type,
	odds_match_player_points_assists.player_id;
CREATE RULE no_delete AS ON DELETE TO odds_match_player_points_assists_view DO INSTEAD NOTHING;

DROP VIEW IF EXISTS odds_match_player_points_rebounds_view;
CREATE VIEW odds_match_player_points_rebounds_view AS SELECT DISTINCT
	odds_match_player_points_rebounds.match_id as uuid,
	odds_match_player_points_rebounds.match_id,
	odds_match_player_points_rebounds.player_id,
	odds_match_player_points_rebounds.type,
	AVG(odds_match_player_points_rebounds.price) AS price,
	AVG(odds_match_player_points_rebounds.point) AS point
FROM
	odds_match_player_points_rebounds
GROUP BY
	odds_match_player_points_rebounds.match_id,
	odds_match_player_points_rebounds.type,
	odds_match_player_points_rebounds.player_id;
CREATE RULE no_delete AS ON DELETE TO odds_match_player_points_rebounds_view DO INSTEAD NOTHING;



DROP VIEW IF EXISTS odds_match_player_points_rebounds_assists_view;
CREATE VIEW odds_match_player_points_rebounds_assists_view AS SELECT DISTINCT
	odds_match_player_points_rebounds_assists.match_id as uuid,
	odds_match_player_points_rebounds_assists.match_id,
	odds_match_player_points_rebounds_assists.player_id,
	odds_match_player_points_rebounds_assists.type,
	AVG(odds_match_player_points_rebounds_assists.price) AS price,
	AVG(odds_match_player_points_rebounds_assists.point) AS point
FROM
	odds_match_player_points_rebounds_assists
GROUP BY
	odds_match_player_points_rebounds_assists.match_id,
	odds_match_player_points_rebounds_assists.type,
	odds_match_player_points_rebounds_assists.player_id;
CREATE RULE no_delete AS ON DELETE TO odds_match_player_points_rebounds_assists_view DO INSTEAD NOTHING;


DROP VIEW IF EXISTS odds_match_player_rebounds_view;
CREATE VIEW odds_match_player_rebounds_view AS SELECT DISTINCT
	odds_match_player_rebounds.match_id as uuid,
	odds_match_player_rebounds.match_id,
	odds_match_player_rebounds.player_id,
	odds_match_player_rebounds.type,
	AVG(odds_match_player_rebounds.price) AS price,
	AVG(odds_match_player_rebounds.point) AS point
FROM
	odds_match_player_rebounds
GROUP BY
	odds_match_player_rebounds.match_id,
	odds_match_player_rebounds.type,
	odds_match_player_rebounds.player_id;
CREATE RULE no_delete AS ON DELETE TO odds_match_player_rebounds_view DO INSTEAD NOTHING;


DROP VIEW IF EXISTS odds_match_player_rebounds_assists_view;
CREATE VIEW odds_match_player_rebounds_assists_view AS SELECT DISTINCT
	odds_match_player_rebounds_assists.match_id as uuid,
	odds_match_player_rebounds_assists.match_id,
	odds_match_player_rebounds_assists.player_id,
	odds_match_player_rebounds_assists.type,
	AVG(odds_match_player_rebounds_assists.price) AS price,
	AVG(odds_match_player_rebounds_assists.point) AS point
FROM
	odds_match_player_rebounds_assists
GROUP BY
	odds_match_player_rebounds_assists.match_id,
	odds_match_player_rebounds_assists.type,
	odds_match_player_rebounds_assists.player_id;
CREATE RULE no_delete AS ON DELETE TO odds_match_player_rebounds_assists_view DO INSTEAD NOTHING;


DROP VIEW IF EXISTS odds_match_player_steals_view;
CREATE VIEW odds_match_player_steals_view AS SELECT DISTINCT
	odds_match_player_steals.match_id as uuid,
	odds_match_player_steals.match_id,
	odds_match_player_steals.player_id,
	odds_match_player_steals.type,
	AVG(odds_match_player_steals.price) AS price,
	AVG(odds_match_player_steals.point) AS point
FROM
	odds_match_player_steals
GROUP BY
	odds_match_player_steals.match_id,
	odds_match_player_steals.type,
	odds_match_player_steals.player_id;
CREATE RULE no_delete AS ON DELETE TO odds_match_player_steals_view DO INSTEAD NOTHING;


DROP VIEW IF EXISTS odds_match_player_triple_double_view;
CREATE VIEW odds_match_player_triple_double_view AS SELECT DISTINCT
	odds_match_player_triple_double.match_id as uuid,
	odds_match_player_triple_double.match_id,
	odds_match_player_triple_double.player_id,
	AVG(odds_match_player_triple_double.price) AS price
FROM
	odds_match_player_triple_double
GROUP BY
	odds_match_player_triple_double.match_id,
	odds_match_player_triple_double.player_id;
CREATE RULE no_delete AS ON DELETE TO odds_match_player_triple_double_view DO INSTEAD NOTHING;


DROP VIEW IF EXISTS odds_match_player_turnovers_view;
CREATE VIEW odds_match_player_turnovers_view AS SELECT DISTINCT
	odds_match_player_turnovers.match_id as uuid,
	odds_match_player_turnovers.match_id,
	odds_match_player_turnovers.player_id,
	odds_match_player_turnovers.type,
	AVG(odds_match_player_turnovers.price) AS price,
	AVG(odds_match_player_turnovers.point) AS point
FROM
	odds_match_player_turnovers
GROUP BY
	odds_match_player_turnovers.match_id,
	odds_match_player_turnovers.type,
	odds_match_player_turnovers.player_id;
CREATE RULE no_delete AS ON DELETE TO odds_match_player_turnovers_view DO INSTEAD NOTHING;

DROP VIEW IF EXISTS odds_match_player_threes_view;
CREATE VIEW odds_match_player_threes_view AS SELECT DISTINCT
	odds_match_player_threes.match_id as uuid,
	odds_match_player_threes.match_id,
	odds_match_player_threes.player_id,
	odds_match_player_threes.type,
	AVG(odds_match_player_threes.price) AS price,
	AVG(odds_match_player_threes.point) AS point
FROM
	odds_match_player_threes
GROUP BY
	odds_match_player_threes.match_id,
	odds_match_player_threes.type,
	odds_match_player_threes.player_id;
CREATE RULE no_delete AS ON DELETE TO odds_match_player_threes_view DO INSTEAD NOTHING;




















