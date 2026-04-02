CREATE OR REPLACE FUNCTION match_history_update() RETURNS TRIGGER AS $match_history_update$
BEGIN
    INSERT INTO matches_matchscorehistory (uuid,created_at,updated_at,winner,score,score_data,match_id,team_id)
    VALUES (gen_random_uuid(),now(),now(),NEW.winner,NEW.score,NEW.score_data,NEW.match_id,NEW.team_id);
    RETURN NEW;
END;
    $match_history_update$ LANGUAGE plpgsql;
DROP TRIGGER  IF EXISTS  "match_history_update" ON "matches_matchscore";
CREATE TRIGGER "match_history_update" BEFORE UPDATE ON "matches_matchscore"
FOR EACH ROW EXECUTE FUNCTION match_history_update();

DROP TRIGGER  IF EXISTS  "match_history_insert" ON "matches_matchscore";
CREATE TRIGGER "match_history_insert" BEFORE INSERT ON "matches_matchscore"
FOR EACH ROW EXECUTE FUNCTION match_history_update();

