DROP VIEW IF EXISTS kiblio_group_view;
CREATE VIEW kiblio_group_view AS SELECT
	kiblio_sport.uuid,
	kiblio_sport.sport_id,
	kiblio_sport.active,
	kiblio_sport.abrv as slug,
	kiblio_sport."name",
	kiblio_sport.vhost_id

FROM
	kiblio_sport;
DROP VIEW IF EXISTS kiblio_season_view;
CREATE VIEW kiblio_season_view AS SELECT
	kiblio_season.uuid,
	kiblio_season."name",
	kiblio_season.vhost_id,
	kiblio_season.abrv AS season_key
FROM
	kiblio_season;

DROP VIEW IF EXISTS kiblio_sport_view;
CREATE VIEW kiblio_sport_view AS SELECT
	kiblio_sport.uuid,
	kiblio_sport.sport_id,
	kiblio_sport."name" AS title,
	kiblio_sport.abrv AS "key",
	kiblio_sport.active,
	kiblio_sport.vhost_id
FROM
	kiblio_sport;

DROP VIEW IF EXISTS kiblio_fixture_mkt_summary_view;
CREATE VIEW kiblio_fixture_mkt_summary_view AS SELECT f.uuid AS fixture_uuid,
    f.name AS fixture_name,
    max(fm.price_american) FILTER (WHERE (s.name ~~* 'home%'::text OR s.abrv ~~* 'home%'::text) AND mt.name ~~* '%moneyline%'::text AND seg.name ~~* '%full%'::text AND fm.is_current = true) AS home_moneyline_price_american,
    max(fm.point) FILTER (WHERE (s.name ~~* 'home%'::text OR s.abrv ~~* 'home%'::text) AND mt.name ~~* '%moneyline%'::text AND seg.name ~~* '%full%'::text AND fm.is_current = true) AS home_moneyline_point,
    max(p.name) FILTER (WHERE (s.name ~~* 'home%'::text OR s.abrv ~~* 'home%'::text) AND mt.name ~~* '%moneyline%'::text AND seg.name ~~* '%full%'::text AND fm.is_current = true) AS home_participant_name,
    max(fm.price_american) FILTER (WHERE (s.name ~~* 'visit%'::text OR s.name ~~* 'away%'::text OR s.abrv ~~* 'visit%'::text OR s.abrv ~~* 'away%'::text) AND mt.name ~~* '%moneyline%'::text AND seg.name ~~* '%full%'::text AND fm.is_current = true) AS away_moneyline_price_american,
    max(fm.point) FILTER (WHERE (s.name ~~* 'visit%'::text OR s.name ~~* 'away%'::text OR s.abrv ~~* 'visit%'::text OR s.abrv ~~* 'away%'::text) AND mt.name ~~* '%moneyline%'::text AND seg.name ~~* '%full%'::text AND fm.is_current = true) AS away_moneyline_point,
    max(p.name) FILTER (WHERE (s.name ~~* 'visit%'::text OR s.name ~~* 'away%'::text OR s.abrv ~~* 'visit%'::text OR s.abrv ~~* 'away%'::text) AND mt.name ~~* '%moneyline%'::text AND seg.name ~~* '%full%'::text AND fm.is_current = true) AS away_participant_name,
    max(fm.point) FILTER (WHERE mt.name ~~* '%spread%'::text AND seg.name ~~* '%full%'::text AND (s.name ~~* 'home%'::text OR s.abrv ~~* 'home%'::text) AND fm.is_current = true) AS spread_home_point,
    max(fm.price_american) FILTER (WHERE mt.name ~~* '%spread%'::text AND seg.name ~~* '%full%'::text AND (s.name ~~* 'home%'::text OR s.abrv ~~* 'home%'::text) AND fm.is_current = true) AS spread_home_price_american,
    max(fm.point) FILTER (WHERE mt.name ~~* '%spread%'::text AND seg.name ~~* '%full%'::text AND (s.name ~~* 'visit%'::text OR s.name ~~* 'away%'::text OR s.abrv ~~* 'visit%'::text OR s.abrv ~~* 'away%'::text) AND fm.is_current = true) AS spread_away_point,
    max(fm.price_american) FILTER (WHERE mt.name ~~* '%spread%'::text AND seg.name ~~* '%full%'::text AND (s.name ~~* 'visit%'::text OR s.name ~~* 'away%'::text OR s.abrv ~~* 'visit%'::text OR s.abrv ~~* 'away%'::text) AND fm.is_current = true) AS spread_away_price_american,
    max(fm.inserted_on) AS last_market_update
   FROM kiblio_fixturemarket fm
     JOIN kiblio_fixture f ON f.uuid = fm.fixture_id
     LEFT JOIN kiblio_sides s ON s.uuid = fm.side_id
     LEFT JOIN kiblio_markettype mt ON mt.uuid = fm.market_type_id
     LEFT JOIN kiblio_segment seg ON seg.uuid = fm.segment_id
     LEFT JOIN kiblio_participant p ON p.uuid = fm.participant_id
  GROUP BY f.uuid, f.name
  ORDER BY f.name;


DROP VIEW IF EXISTS kiblio_fixture_markets_view;
CREATE VIEW kiblio_fixture_markets_view AS SELECT DISTINCT
    kiblio_fixture.fixture_id AS fixture_id,
    kiblio_markettype.name AS market_type,
    kiblio_fixturemarket.point,
    kiblio_fixturemarket.uuid,
    kiblio_fixturemarket.price_american,
    kiblio_fixturemarket.price_fraction,
    kiblio_fixturemarket.max_limit,
    kiblio_fixturemarket.is_live,
    kiblio_fixturemarket.is_opener,
    kiblio_fixturemarket.is_previous,
    kiblio_fixturemarket.is_current,
    kiblio_fixturemarket.is_main,
    kiblio_participant.name AS team_name,
    kiblio_fixturemarket.participant_id,
    kiblio_league.name AS league_name,
    kiblio_fixturemarket.league_id,
    kiblio_fixturemarket.segment_id,
    kiblio_segment.name AS segment_name,
    kiblio_fixturemarket.side_id,
    kiblio_sides.name AS side_name,
    kiblio_fixture.name AS fixture_name,
    kiblio_fixturemarket.market_type_id
   FROM kiblio_fixturemarket
     FULL JOIN kiblio_markettype ON kiblio_fixturemarket.market_type_id = kiblio_markettype.uuid
     FULL JOIN kiblio_participant ON kiblio_fixturemarket.participant_id = kiblio_participant.uuid
     FULL JOIN kiblio_league ON kiblio_fixturemarket.league_id = kiblio_league.uuid
     FULL JOIN kiblio_segment ON kiblio_fixturemarket.segment_id = kiblio_segment.uuid
     JOIN kiblio_sides ON kiblio_fixturemarket.side_id = kiblio_sides.uuid
     JOIN kiblio_fixture ON kiblio_fixturemarket.fixture_id = kiblio_fixture.uuid;



DROP VIEW IF EXISTS  kiblio_fixture_outcome_view;
CREATE VIEW kiblio_fixture_outcome_view AS  SELECT DISTINCT kiblio_outcome.outcome_id,
    kiblio_outcome.routing_key AS outcome_routing_key,
    kiblio_fixture.uuid AS fixture_uuid,
    kiblio_fixture.fixture_id,
    kiblio_fixture.routing_key,
    kiblio_fixture.name,
    kiblio_fixture.vhost_id,
    kiblio_fixture.fixture_type_id,
    kiblio_fixture.league_id,
    kiblio_fixture.season_id,
    kiblio_fixture.location_id,
    kiblio_state.state_id,
    kiblio_state.name AS state_name,
    kiblio_state.abrv AS state_abrv,
    kiblio_segment.name AS segment_name,
    kiblio_segment.segment_id,
    kiblio_segment.abrv AS segment_abrv,
    kiblio_outcome.clock,
    kiblio_outcome.is_current,
    kiblio_outcome.is_start_game,
    kiblio_outcome.is_end_game,
    kiblio_outcome.is_start_segment,
    kiblio_outcome.is_end_segment,
    kiblio_fixture.uuid AS uuid,
    kiblio_outcome.uuid AS outcome_uuid
   FROM kiblio_fixture
     JOIN kiblio_outcome ON kiblio_fixture.uuid = kiblio_outcome.fixture_id
     JOIN kiblio_state ON kiblio_outcome.state_id = kiblio_state.state_id
     JOIN kiblio_segment ON kiblio_outcome.segment_id = kiblio_segment.uuid;


