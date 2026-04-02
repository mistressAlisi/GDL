import json

from django.core.management import BaseCommand
from django.utils.timezone import now

from dataengine.models import DataEngineDriver, DataEngineDriverHistory, DataEngineVHostConfig
from parameters.models import VHost


class Command(BaseCommand):
    help = 'Import a Driver information file for the given vhost'
    def add_arguments(self, parser):
        # Named (optional) arguments
        parser.add_argument("vhost",type=str,nargs="+")
        parser.add_argument("driver", type=str, nargs="+")
    def handle(self, *args, **options):
        vHost = VHost.objects.get(pk=options["vhost"][0])
        driver = DataEngineDriver.objects.get(class_name=options["driver"][0])
        driverEnable = DataEngineVHostConfig.objects.get_or_create(vhost=vHost, driver=driver)[0]
        driverEnable.active = True
        driverEnable.save()
        self.stdout.write(self.style.MIGRATE_LABEL(f'Driver [{driver.name}] on Vhost [{vHost}] - enabled'))