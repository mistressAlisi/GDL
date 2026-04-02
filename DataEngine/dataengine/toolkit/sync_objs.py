import importlib

from dataengine.models import DataEngineVHostConfig


def find_driver_data_source_obj(vhost,object_type,object_uuid):
    """
    Finds the Driver Data Source Object for the given object type and uuid,
    And returns the driver that owns it, and the object itself or false,false.
    :param vhost: VHost to search data sources in
    :param object_type: Object type to search for
    :param object_uuid:  Object UUID to search for
    :return: driver,object or false,false.
    """
    for driver in DataEngineVHostConfig.objects.filter(vhost=vhost,active=True):
        _driver_module = importlib.import_module(f"{driver.driver.class_name}.driver.api")
        driver_module = _driver_module.DataEngineDriverAPI(vhost=vhost)
        driver_ret = driver_module.get_api_object(object_type,object_uuid)
        if driver_ret:
            return driver.driver,driver_ret
    return False,False