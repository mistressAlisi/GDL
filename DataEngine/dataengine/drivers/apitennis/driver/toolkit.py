from datetime import datetime

import requests
import logging
import os

from django.conf import settings

from dataengine.drivers.apisports.models import Season
from parameters.models import VHostParameterRegistry

regappid = "dataengine.drivers.apitennis"

def get_api_tennis_key(vhost):
    apiSettings,created = VHostParameterRegistry.objects.get_or_create(vhost=vhost,application=regappid,name="api_key_str")
    if created: apiSettings.save()
    return apiSettings.value_text



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