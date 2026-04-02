import abc
import importlib
from logging import getLogger

from django.forms import model_to_dict
from django.utils.text import slugify
from django.utils.timezone import now

from dataengine.models import DataEngineVHostConfig, DataEngineDriver

from abc import ABC
class ABCDataEngineObj(ABC):
    vhost = False
    drivers = []
    auth_driver = []
    logger = None
    debug = False


    def __init__(self, vhost,**kwargs):
        self.vhost = vhost
        auth_drivers = DataEngineVHostConfig.objects.filter(vhost=vhost,active=True,authoritative=True)
        self.auth_driver = self._load_drivers(auth_drivers)[0]
        drivers = DataEngineVHostConfig.objects.filter(vhost=vhost,active=True,authoritative=False)
        self.drivers = self._load_drivers(drivers)
        if "logger_name" in kwargs:
            self.logger = getLogger(f"dataengine.{kwargs['logger_name']}")
        else:
            self.logger = getLogger("dataengine.core")

        if "debug" in kwargs and kwargs["debug"]:
            self.debug = kwargs["debug"]
    def _object_setattrs(self,obj,entry,**kwargs):
        keys = model_to_dict(obj,entry.keys()).keys()
        # print(keys)
        for k in keys:
            # print(k)
            if "rows" in kwargs:
                if hasattr(obj,k) and k in kwargs["rows"]:
                    setattr(obj, k, entry[k])
            elif hasattr(obj,k):
                   setattr(obj,k,entry[k])
        obj.save()

    def _load_drivers(self,drivers):
        load_arr = []
        for driver in drivers:
            _driver_module = importlib.import_module(f"{driver.driver.class_name}.driver.api")
            driver_module = _driver_module.DataEngineDriverAPI(vhost=self.vhost)
            load_arr.append(driver_module)
        # print(load_arr)
        return load_arr


    def _set_systemObj_attr(self,systemObj,dataObj,dataObjAttr):
        systemObj.system_object_uuid = dataObj.uuid
        systemObj.system_object_type = f"{systemObj._meta.app_label}.{systemObj._meta.model_name}.{systemObj._meta.object_name}"
        setattr(systemObj,dataObjAttr,dataObj)
        systemObj.last_sync = now()
        systemObj.save()


class DataEngineDriverAPIABC(ABC):
    def _format_season(self, s):
        season = {
            "id": s.season_id,
            "season_key": s.abrv,
            "name": s.name,
            "inserted_on": s.inserted_on,
            "inserted_on_epoch": s.inserted_on_epoch,
            "object_uuid": s.uuid,
            "object_type": f"{s._meta.app_label}.{s._meta.model_name}.{s._meta.object_name}"
        }
        return season

    def _format_group(self, s):
        group = {
            "id": s.sport_id,
            "slug": s.abrv,
            "name": s.name,
            "inserted_on": s.inserted_on,
            "inserted_on_epoch": s.inserted_on_epoch,
            "object_uuid": s.uuid,
            "object_type": f"{s._meta.app_label}.{s._meta.model_name}.{s._meta.object_name}"
        }
        return group

    def _format_sport(self, s):

        if s.abrv != None:
            key = s.abrv
        else:
            key = slugify(s.name)
        sport = {
            "id":s.league_id,
            "key":key,
            "title":s.name,
            "logo":getattr(s,"logo",None),
            "group":s.sport,
            "sport_mask":getattr(s,"sport_mask",None),
            "group_type": f"{s.sport._meta.app_label}.{s.sport._meta.model_name}.{s.sport._meta.object_name}",
            "group_uuid":s.sport.uuid,
            "inserted_on":s.inserted_on,
            "inserted_on_epoch":s.inserted_on_epoch,
            "object_uuid":s.uuid,
            "object_type": f"{s._meta.app_label}.{s._meta.model_name}.{s._meta.object_name}"
        }
        return sport

    def _format_team(self, s):
        if s.abrv != None:
            key = s.abrv
        else:
            key = slugify(s.name)
        team = {
            "id":s.participant_id,
            "key":key,
            "name":s.name,
            "country": getattr(s,"country",None),
            "bday": getattr(s,"bday",None),
            "logo": getattr(s,"logo",None),
            "mascot": s.mascot,
            "parent_team":s.parent_participant_id,
            "inserted_on":s.inserted_on,
            "sport": s.league,
            "sport_type": f"{s.league._meta.app_label}.{s.league._meta.model_name}.{s.league._meta.object_name}",
            "sport_uuid": s.league.uuid,
            "object_uuid":s.uuid,
            "object_type": f"{s._meta.app_label}.{s._meta.model_name}.{s._meta.object_name}"
        }

        return team

    def _format_segment(self, s):
        segment = {
            "id": s.segment_id,
            "name": s.name,
            "inserted_on": s.inserted_on,
            "abrv": s.abrv,
            "object_uuid": s.uuid,
            "object_type": f"{s._meta.app_label}.{s._meta.model_name}.{s._meta.object_name}"
        }
        return segment