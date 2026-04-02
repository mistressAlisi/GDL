from matches.models import MatchEvent

from toolkit.logger import getLogger
logger =  getLogger("player_1st_td.wagers","qualifier_1st_td.log","wagers")




def get_match_1st_td(matchObj):
    if not matchObj:
        logger.error("Supply a matchObj!")
        return False
    if not matchObj.sport.key.startswith('americanfootball'):
        logger.error(f"This match, {matchObj} is not an American Football Match.")
        return False
    events = MatchEvent.objects.filter(match=matchObj,type="TD")
    if len(events) == 0:
        logger.info(f"Match {matchObj} has no TD events")
        return None
    logger.info(f"Match {matchObj} : First Touchdown is {events[0]}")
    return events[0]


def qualify_wager(wagerObj):
    if not wagerObj:
        logger.error("Supply a wagerObj!")
        return False
    touchdown_obj = get_match_1st_td(wagerObj.match)
    if not touchdown_obj:
        logger.info("No Touchdowns received!")
        return False
    if touchdown_obj.player.uuid == wagerObj.bet_data["player"]:
        logger.info(f"Wager is a winner! {wagerObj.bet_data['player']} == {touchdown_obj.player.uuid}")
        return True