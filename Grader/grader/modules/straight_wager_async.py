from types import SimpleNamespace

from asgiref.sync import sync_to_async
from django.db import transaction
from django.forms import model_to_dict
from django.utils.timezone import localdate, now

from grader.modules.abcasync import GraderModuleABCAsync
from matches.models import Match
from teams.models import Team


class StraightWagerGraderAsync(GraderModuleABCAsync):

    async def _grade_wager_func(self, wagerObj, **kwargs):
        # Very simple, is this a draw, first?
        # print("GWF")
        wager = await sync_to_async(lambda:SimpleNamespace(**model_to_dict(wagerObj)),thread_sensitive=False)()
        _matchObj = await sync_to_async(lambda:Match.objects.using('default').get(uuid=wager.match),thread_sensitive=False)()
        matchObj = await sync_to_async(lambda:SimpleNamespace(**model_to_dict(_matchObj)),thread_sensitive=False)()
        # print("GWF'")
        if not matchObj.score_closed or not matchObj.finished:
            self.logger.info(f"Match has not been marked as finished with score closed for wager {wager.uuid}: Not grading. Match is: {matchObj.status_short}/F:{matchObj.finished}/SC:{matchObj.score_closed}")
            return False
        # print("'A")
        if "draw" in matchObj.scoring_data and matchObj.draw == True:
            # Okay, it is. Is the wager for a draw?
            if wagerObj.for_draw:
                self.logger.info(f"Player for Wager {wagerObj} bet on Draw. Match is a DRAW. Player Wins!")
                if "no_upd_bets" in kwargs: return True
                wagerObj.status = "W"
                wagerObj.graded = True
                wagerObj.grader_history = {"auto": True, "draw_won": True, "type": "parlay_leg_straight"}
                await sync_to_async(lambda:wagerObj.save(using='default'),thread_sensitive=False)()
                from wager.signals import signal_wager_qualified
                signal_wager_qualified.send(sender=self.__class__, wagerObj=wagerObj, account=wagerObj.account,
                                            vhost=wagerObj.vhost)
                return True
            else:
                # print("'B")
                self.logger.info(f"Match is a Draw! Scoredelta 0!")
                # IF THIS IS a Draws Push mode, mark a D, else, just Loose it outright:
                if "draws_push" in kwargs:
                    if "no_upd_bets" in kwargs:
                        self.logger.info("Not writing changes to to bet: no_upd_bets is set.")
                        return False
                    wagerObj.status = "D"
                    wagerObj.graded = True
                    wagerObj.grader_history = {"auto": True, "type": "parlay_leg_straight", "draw": True,
                                                  "push": True}
                    await sync_to_async(lambda:wagerObj.save(),thread_sensitive=False)()
                    from wager.signals import signal_wager_qualified
                    signal_wager_qualified.send(sender=self.__class__, wagerObj=wagerObj, account=wagerObj.account,
                                                vhost=wagerObj.vhost)
                    return False
                else:
                    if "no_upd_bets" in kwargs:
                        self.logger.info("Not writing changes to to bet: no_upd_bets is set.")
                        return False
                    wagerObj.status = "L"
                    wagerObj.graded = True
                    wagerObj.grader_history = {"auto": True, "type": "parlay_leg_straight", "draw": True,
                                                  "loose": True}
                    await sync_to_async(lambda:wagerObj.save(),thread_sensitive=False)()
                    from wager.signals import signal_wager_qualified
                    signal_wager_qualified.send(sender=self.__class__, wagerObj=wagerObj, account=wagerObj.account,
                                                vhost=wagerObj.vhost)
                    return False
        elif matchObj.winner == wager.team_1:
            # print("'C")
            team =     await sync_to_async(lambda:Team.objects.get(uuid=matchObj.winner),thread_sensitive=False)()
            team_name = await sync_to_async(lambda:team.name,thread_sensitive=False)()
            self.logger.info(f"Player bet on winning team: {team_name}.")
            if "no_upd_bets" in kwargs:
                self.logger.info("Not writing changes to to bet: no_upd_bets is set.")
                return True
            wagerObj.status = "W"
            wagerObj.graded = True
            wagerObj.grader_history = {"auto": True, "type": "parlay_leg_straight", "win": True}
            await sync_to_async(lambda:wagerObj.save(using='default'),thread_sensitive=False)()
            from wager.signals import signal_wager_qualified
            signal_wager_qualified.send(sender=self.__class__, wagerObj=wagerObj, account=wagerObj.account,
                                        vhost=wagerObj.vhost)
            return True

        else:
            # print("'D")
            try:
                team = await sync_to_async(lambda:Team.objects.get(uuid=matchObj.winner),thread_sensitive=False)()
            except Team.DoesNotExist:
                wagerObj.status = "L"
                wagerObj.graded = True
                wagerObj.grader_history = {"auto": True, "type": "parlay_leg_straight", "loose": True,"no_team":True}
                return False
            team_name = await sync_to_async(lambda:team.name,thread_sensitive=False)()
            self.logger.info(f"Player bet on loosing team: {team_name}.")
            if "no_upd_bets" in kwargs:
                self.logger.info("Not writing changes to to bet: no_upd_bets is set.")
                return False
            wagerObj.status = "L"
            wagerObj.graded = True
            wagerObj.grader_history = {"auto": True, "type": "parlay_leg_straight", "loose": True}
            await sync_to_async(lambda:wagerObj.save(using='default'),thread_sensitive=False)()
            from wager.signals import signal_wager_qualified
            signal_wager_qualified.send(sender=self.__class__, wagerObj=wagerObj, account=wagerObj.account,
                                        vhost=wagerObj.vhost)
            return False

    async def _close_wager_func(self, wagerObj, score, **kwargs):
        if wagerObj.status == "L":
            wagerObj.grade_outcome = "L"
            wagerObj.graded_at = now()
            wagerObj.graded = True
        elif wagerObj.status == "W":
            wagerObj.grade_outcome = "W"
            wagerObj.graded_at = now()
            wagerObj.graded = True
        elif wagerObj.status == "D":
            wagerObj.grade_outcome = "D"
            wagerObj.graded_at = now()
            wagerObj.graded = True
        await sync_to_async(lambda:wagerObj.save(),thread_sensitive=False)()




GRADER_MODULE=StraightWagerGraderAsync