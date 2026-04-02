from matches.models import MatchEvent

from toolkit.logger import getLogger
logger =  getLogger("player_last_td.wagers","qualifier_last_td.log","wagers")




def get_match_last_td(matchObj):
    if not matchObj:
        logger.error("Supply a matchObj!")
        return False
    if not matchObj.sport.key.startswith('americanfootball'):
        logger.error(f"This match, {matchObj} is not an American Football Match.")
        return False
    events = MatchEvent.objects.filter(match=matchObj,type="TD")
    elo = len(events)
    if elo == 0:
        logger.info(f"Match {matchObj} has no TD events")
        return None
    logger.info(f"Match {matchObj} : Last Touchdown is {events[elo]}")
    return events[elo]


def qualify_wager(wagerObj):
    if not wagerObj:
        logger.error("Supply a wagerObj!")
        return False
    touchdown_obj = get_match_last_td(wagerObj.match)
    if not touchdown_obj:
        logger.info("No Touchdowns received!")
        return False
    if touchdown_obj.player.uuid == wagerObj.bet_data["player"]:
        logger.info(f"Wager is a winner! {wagerObj.bet_data['player']} == {touchdown_obj.player.uuid}")
        return True