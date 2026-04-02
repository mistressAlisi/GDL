from datetime import datetime

import requests
import logging
import os

from asgiref.sync import sync_to_async
from django.conf import settings



regappid = "dataengine.drivers.apisports"

def get_api_sports_session(vhost):
    from dataengine.drivers.apisports.models import Season
    from parameters.models import VHostParameterRegistry
    apiSettings,created = VHostParameterRegistry.objects.get_or_create(vhost=vhost,application=regappid,name="api_key_str")
    if created: apiSettings.save()
    session = requests.session()
    session.headers.update({
        'x-rapidapi-key': apiSettings.value_text,
    })
    return session,apiSettings



from django.conf import settings


def getLogger(log_name,file_name=False,directory=False):
    logger = logging.getLogger(log_name)
    chl = logging.StreamHandler()
    logger.addHandler(chl)
    if os.path.exists(settings.LOG_DIR) and file_name:
        if directory:
            if not os.path.isdir(f"{settings.LOG_DIR}/{directory}"):
                os.makedirs(f"{settings.LOG_DIR}/{directory}")
            if os.path.isdir(f"{settings.LOG_DIR}/{directory}/"):
                fhl = logging.FileHandler(f"{settings.LOG_DIR}/{directory}/{file_name}")
                logFormatter = logging.Formatter("%(asctime)s [%(levelname)s]  %(message)s")
                fhl.setFormatter(logFormatter)
                logger.addHandler(fhl)
    return logger


def get_league_active_season(seasons,vhost):
    from dataengine.drivers.apisports.models import Season

    for season in seasons:
        start = datetime.strptime(season["start"], '%Y-%m-%d')
        end = datetime.strptime(season["end"], '%Y-%m-%d')
        now = datetime.now()
        if "current" in season:
            current = season["current"]
        else:
            current = False
        if current or ((start <= now) and (now <= end)):
                if "year" in season:
                    seasonObj = Season.objects.get_or_create(active=True, season_key=season["year"],vhost=vhost)
                else:
                    seasonObj = Season.objects.get_or_create(active=True, season_key=season["season"],vhost=vhost)
                if seasonObj[1]:
                    seasonObj[0].save()
                return season,seasonObj[0]
    else:
        return False,False


async def aget_league_active_season(seasons,vhost):
    from dataengine.drivers.apisports.models import Season

    for season in seasons:
        start = datetime.strptime(season["start"], '%Y-%m-%d')
        end = datetime.strptime(season["end"], '%Y-%m-%d')
        now = datetime.now()
        if "current" in season:
            current = season["current"]
        else:
            current = False
        if current or ((start <= now) and (now <= end)):

                if "year" in season:
                    try:
                        seasonObj = await sync_to_async(lambda:Season.objects.get_or_create(active=True, season_key=season["year"],vhost=vhost),thread_sensitive=False)()
                    except Season.MultipleObjectsReturned:
                        seasonObj = await sync_to_async(
                            lambda: Season.objects.filter(active=True, season_key=season["year"], vhost=vhost).first(),
                            thread_sensitive=False)()
                        return season,seasonObj
                else:
                    try:
                        seasonObj = await sync_to_async(lambda:Season.objects.get_or_create(active=True, season_key=season["season"],vhost=vhost),thread_sensitive=False)()
                    except Season.MultipleObjectsReturned:
                        seasonObj = await sync_to_async(
                            lambda: Season.objects.filter(active=True, season_key=season["season"], vhost=vhost).first(),
                            thread_sensitive=False)()
                        return season, seasonObj
                if seasonObj[1]:
                    seasonObj[0].save()
                return season,seasonObj[0]
    else:
        return False,False