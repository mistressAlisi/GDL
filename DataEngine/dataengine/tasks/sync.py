from celery import shared_task
from celery.utils.log import get_task_logger

from dataengine.engine import DataEngine
from parameters.models import VHost

logger = get_task_logger(__name__)

@shared_task()
def dataengine_sync_vhost(vhost):
    logger.info(f"Starting DataEngine sync on vhost {vhost}")
    vHObj = VHost.objects.get(uuid=vhost)
    dataEngine = DataEngine(vhost=vHObj)
    dataEngine.call_driver_update()
    dataEngine.sync_authoritative_drivers()


@shared_task()
def dataengine_sync():
    logger.info(f"Starting DataEngine sync run for all Vhosts...")
    vHosts = VHost.objects.filter(active=True)
    for vHost in vHosts:
        dataengine_sync_vhost.apply_async(args=[str(vHost.uuid),])
