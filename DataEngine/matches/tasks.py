from datetime import timedelta

from celery import shared_task
from django.db import transaction
from django.utils.timezone import now

from matches.models import Match, MatchScore
from toolkit.logger import getLogger

logger =  getLogger("athena.matches.tasks","tasks.log","matches")

@shared_task()
def close_and_score_match(muuid):
    try:
        matchObj = Match.objects.get(uuid=muuid,finished=True,score_closed=False,wagers_paid=False)
    except Match.DoesNotExist:
        logger.warning(f"***Refusing to Close and Score {muuid}. Match does not exist with finished=False,score_closed=True,wagers_paid=False?***")
        return False

    logger.info(f"This is match: {matchObj.away_team.name} at {matchObj.home_team.name}: Commences at {matchObj.commence_time}")
    with transaction.atomic():
        final_scores = MatchScore.objects.filter(match=matchObj).order_by("-score")
        if len(final_scores) == 2:
            max_score = final_scores[0]
            min_score = final_scores[1]
        elif len(final_scores) == 1:
            max_score = final_scores[0]
            # No Min score... create a Zero just for consistency (Zero would imply no marker. Seen in LoI Soccer for example):
            if max_score.team == matchObj.home_team:
                team_tc = matchObj.away_team
            else:
                team_tc = matchObj.home_team
            min_score = MatchScore(match=matchObj,team=team_tc,score=0)
            min_score.save()
        else:
            if  matchObj.commence_time - now() < timedelta(days=-1):
                logger.warning("This match should have finished more than one day ago. Closing arbitrarily.")
                matchObj.active = False
                matchObj.open = False
                matchObj.finished = False
                matchObj.score_closed = False
                matchObj.save()
            else:
                logger.warning(f"***Match does not have at least one score, we can't close it yet.")
            return False
        matchObj.score_closed = True
        logger.info("NOTE: In the CaS Transaction: closing Match.")
        matchObj.open = False
        matchObj.active = False
        if (max_score.score == min_score.score):
            logger.warning(f"***Match {muuid}: is a DRAW! Match Closed.***")
            # DRAW!
            min_score.winner = False
            max_score.winner = False
            # Both get a draw!!
            min_score.team.total_draws += 1
            max_score.team.total_draws += 1
            matchObj.draw=True

            min_score.save()
            max_score.save()
            matchObj.save()
            logger.warning(f"****Match {muuid} is a draw! Match Closed.***")
            return True
        else:
            logger.warning(f"***Match {muuid}: Winner is {max_score.team.name}, {max_score.score} to {min_score.score}! Match Closed.***")
            max_score.winner = True
            max_score.team.total_wins +=1
            min_score.team.total_losses +=1
            min_score.winner = False
            max_score.save()
            min_score.save()
        fscore = f"{max_score.team.name}: {max_score.score} -- {min_score.team.name}: {min_score.score}"
        matchObj.winner=max_score.team
        matchObj.final_score=fscore
        matchObj.save()

        return True


@shared_task()
def close_matches_scheduler():
    # logger.warning("Match Close Scheduler run")
    _matchObj = Match.objects.filter(finished=True, score_closed=False, wagers_paid=False,active=True,live_events=False, open=False)

    #print("Running Match Close Scheduler")
    for match in _matchObj:
        logger.warning(f"I'm closing match {match.uuid}/{match.id}....")
        close_and_score_match.apply_async((str(match.uuid),))




