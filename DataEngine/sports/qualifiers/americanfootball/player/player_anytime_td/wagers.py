from matches.models import MatchEvent
from players.models import Player

from toolkit.logger import getLogger
logger =  getLogger("player_at_td.wagers","qualifier_at_td.log","wagers")




def get_match_tds_wplayer(matchObj,playerObj):
    if not matchObj:
        logger.error("Supply a matchObj!")
        return False
    if not matchObj.sport.key.startswith('americanfootball'):
        logger.error(f"This match, {matchObj} is not an American Football Match.")
        return False
    events = MatchEvent.objects.filter(match=matchObj,type="TD",player=playerObj)
    if len(events) == 0:
        logger.info(f"Match {matchObj} has no TD events for player {playerObj}")
        return False
    logger.info(f"Match {matchObj} : First Touchdown is {events[0]}")
    return events


def qualify_wager(wagerObj):
    if not wagerObj:
        logger.error("Supply a wagerObj!")
        return False
    playerObj = Player.objects.get(uuid=wagerObj.bet_data["player"])
    touchdown_obj = get_match_tds_wplayer(wagerObj.match,playerObj)
    if not touchdown_obj:
        logger.info("No Touchdowns received!")
        return False
    if len(touchdown_obj) > 0:
        logger.info(f"Wager is a winner! {wagerObj.bet_data['player']}")
        return True