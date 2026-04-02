import abc
import importlib
from logging import getLogger

from django.forms import model_to_dict
from django.utils.timezone import now

from dataengine.models import DataEngineVHostConfig, DataEngineDriver

from abc import ABC
class ABCDataEngineObj(ABC):
    vhost = False
    drivers = False
    auth_drivers = False
    logger = None
    currentDriverObject = None
    debug = False
    def __init__(self, vhost,**kwargs):
        self.vhost = vhost
        self.drivers = DataEngineVHostConfig.objects.filter(vhost=vhost,active=True,authoritative=False)
        self.auth_drivers = DataEngineVHostConfig.objects.filter(vhost=vhost,active=True,authoritative=True)
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

    def _load_driver(self,driver):
        _driver_module = importlib.import_module(f"{driver.class_name}.driver.api")
        driver_module = _driver_module.DataEngineDriverAPI(vhost=self.vhost)
        self.currentDriverObject = driver_module


    def _set_systemObj_attr(self,systemObj,dataObj,dataObjAttr):
        systemObj.system_object_uuid = dataObj.uuid
        systemObj.system_object_type = f"{systemObj._meta.app_label}.{systemObj._meta.model_name}.{systemObj._meta.object_name}"
        setattr(systemObj,dataObjAttr,dataObj)
        systemObj.last_sync = now()
        systemObj.save()


    def load_driver(self,driver_name):
        try:
            driver = self.drivers.get(driver__class_name=driver_name)
        except DataEngineDriver.DoesNotExist:
            self.logger.error(f"driver {driver_name} does not exist")
            return False
        self._load_driver(driver.driver)
        self.logger.debug(f"loaded driver {driver_name}")
        return True