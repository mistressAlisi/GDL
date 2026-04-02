DROP VIEW IF EXISTS "sports_sport_group_view";
CREATE VIEW sports_sport_group_view AS SELECT
	sports_sport.uuid AS "id",
	sports_group.slug AS group_slug,
	sports_group."name" AS group_name,
	sports_group.icon AS group_icon,
	sports_sport."key" AS sport_key,
	sports_sport.title AS sport_title,
	sports_sport.card_logo AS sport_card_logo,
	sports_sport.large_logo AS sport_large_logo,
	sports_sport.description AS sport_description,
	sports_sport.featured as sport_featured
FROM
	sports_group
	INNER JOIN
	sports_sport
	ON
		sports_group.uuid = sports_sport.group_id
WHERE
    sports_sport.skip_index_display IS FALSE
ORDER BY sports_sport.priority;