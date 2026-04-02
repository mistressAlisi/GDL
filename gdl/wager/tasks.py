from celery import shared_task
from django.db import transaction

from matches.models import Match
from toolkit.logger import getLogger
from toolkit.wagers.thequalifier import TheQualifier
from wager.models import Wager, MatchWagers

logger =  getLogger("wager.tasks","tasks.log","wagers")
qualifier = TheQualifier()
@shared_task()
@transaction.atomic
def match_close_wagers(muuid,override=False):
    if not override:
        try:
            matchObj = Match.objects.get(uuid=muuid,finished=True,score_closed=True,wagers_paid=False)
        except Match.DoesNotExist:
            logger.warning(f"Refusing to Close Wagers on: {muuid}. Match does not exist with finished=false,score_closed=True,wagers_paid=False?")
            return False
    else:
        try:
            matchObj = Match.objects.get(uuid=muuid,finished=True)
            return True
        except Match.DoesNotExist:
            logger.warning(f"Refusing to Close Wagers on: {muuid}, even with overrides, match does not exist with finished=true.")
            return False
    logger.info(f"***Closing all open wagers on Match: {matchObj.uuid}/{matchObj.id}***")
    _mWagerObjs = MatchWagers.objects.filter(match=matchObj,wager__status__in=['P','M'],wager__live=False)
    with transaction.atomic():
        for mWagerObj in _mWagerObjs:
            logger.info(f"Processing Wager: {mWagerObj.wager.uuid}")
            if qualifier.qualify_bet(mWagerObj.wager) != None:
                if mWagerObj.wager.status in ["W","L"]:
                    if mWagerObj.wager.execute_close():
                        mWagerObj.wager.closed = True
                        logger.info(f"Wager {mWagerObj.wager.uuid} has been closed (and paid out if relevant).")
        matchObj.wagers_paid = True
        matchObj.save()
    return True


@shared_task()
@transaction.atomic
def qual_wagers_worker(wuuid,closed_mask=False,executed_mask=False,status_mask=["P","M"]):
    with transaction.atomic():
        try:
            wagerObj = Wager.objects.get(closed=closed_mask,executed=executed_mask,status__in=status_mask,uuid=wuuid)
        except Wager.DoesNotExist:
            print(f"Wager {wuuid} not found")
            return True
        logger.warning(f"***Qualifying Wager: {wagerObj.uuid}***")
        if qualifier.qualify_bet(wagerObj) != None:
            if wagerObj.status in ["W","L"]:
                if wagerObj.execute_close():
                    wagerObj.closed = True
                    wagerObj.save()
                    logger.info(f"Wager {wagerObj.uuid} has been closed (and paid out if relevant).")
    return True


@shared_task()
def qual_wagers_scheduler():
    _wagersObj = Wager.objects.filter(closed=False,executed=False,status__in=['P','M'],match__finished=True,live=False,match__score_closed=True)
    for wager in _wagersObj:
        qual_wagers_worker.apply_async((str(wager.uuid),))
    # Close open parlay legs' root nodes where dangling:
    _wagersObj = Wager.objects.filter(parlay_closed=False,type="PA",status__in=["W","L"],bet_data__has_key="parent")
    for wager in _wagersObj:
        # print(wager)
        qual_wagers_worker.apply_async((str(wager.uuid),True,True,["W","L"],))


@shared_task()
@transaction.atomic
def close_wagers_worker(wuuid):
    with transaction.atomic():
        wagerObj = Wager.objects.get(closed=False,executed=False,status__in=['W','L'],uuid=wuuid)
        logger.warning(f"***Closing Wager: {wagerObj.uuid}***")
        if qualifier.qualify_bet(wagerObj) != None:
            if wagerObj.status in ["W","L"]:
                if wagerObj.execute_close():
                    wagerObj.closed = True
                    wagerObj.save()
                    logger.info(f"Wager {wagerObj.uuid} has been closed (and paid out if relevant).")

    return True

@shared_task()
def close_wagers_scheduler():
    _wagersObj = Wager.objects.filter(closed=False,executed=False,status__in=['W','L'],match__finished=True,live=False)
    for wager in _wagersObj:
        close_wagers_worker.apply_async((str(wager.uuid),))



@shared_task()
def close_wagers_on_match(muuid):
    _matchObj = Match.objects.filter(finished=True, uuid=muuid,score_closed=True)
    logger.warning(f"Manual Wager Close Run for Match {muuid}")
    #print("Running Wager Close Scheduler")
    for match in _matchObj:
        logger.warning(f"I'm closing wagers in match {match.uuid}/{match.id}....")
        match_close_wagers.apply_async((str(match.uuid),True,))


@shared_task()
@transaction.atomic()
def close_wagers_on_match_state_progress(muuid):
    try:
        matchObj = Match.objects.get(uuid=muuid)
    except Match.DoesNotExist:
        return False
    # First quarter Finished:
    if matchObj.status_short == "Q2":
        _wagerObjs = Wager.objects.filter(match=matchObj,type="DY",status__in=["P","M","I"],bet_data__period="Q1")
        for wagerObj in _wagerObjs:
            qual_wagers_worker.apply_async((str(wagerObj.uuid),))
    # Second Quarter Finished / First Half Finished:
    elif matchObj.status_short == "Q3" or matchObj.status_short == "H2" or matchObj.status_short == "HT":
        _wagerObjs = Wager.objects.filter(match=matchObj,type="DY",status__in=["P","M","I"],bet_data__period="Q2")
        for wagerObj in _wagerObjs:
            qual_wagers_worker.apply_async((str(wagerObj.uuid),))
        _wagerObjs = Wager.objects.filter(match=matchObj, type="DY", status__in=["P", "M", "I"], bet_data__period="H1")
        for wagerObj in _wagerObjs:
            qual_wagers_worker.apply_async((str(wagerObj.uuid),))
    # Third Quarter Finished:
    elif matchObj.status_short == "Q4":
        _wagerObjs = Wager.objects.filter(match=matchObj,type="DY",status__in=["P","M","I"],bet_data__period="Q3")
        for wagerObj in _wagerObjs:
            qual_wagers_worker.apply_async((str(wagerObj.uuid),))
    # Overtime!
    elif matchObj.status_short == "OT" or matchObj.status_short == "FT" or matchObj.status_short == "AOT":
        _wagerObjs = Wager.objects.filter(match=matchObj,type="DY",status__in=["P","M","I"],bet_data__period="Q4")
        for wagerObj in _wagerObjs:
            qual_wagers_worker.apply_async((str(wagerObj.uuid),))
        _wagerObjs = Wager.objects.filter(match=matchObj,type="DY",status__in=["P","M","I"],bet_data__period="H2")
        for wagerObj in _wagerObjs:
            qual_wagers_worker.apply_async((str(wagerObj.uuid),))






