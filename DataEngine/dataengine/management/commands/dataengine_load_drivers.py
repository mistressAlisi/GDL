import json

from django.core.management import BaseCommand
from django.utils.timezone import now

from dataengine.models import DataEngineDriver, DataEngineDriverHistory
from parameters.models import VHost


class Command(BaseCommand):
    help = 'Import a Driver information file for the given vhost'
    def add_arguments(self, parser):
        # Named (optional) arguments
        # parser.add_argument("vhost",type=str,nargs="+")
        parser.add_argument("in_file", type=str, nargs="+")
    def handle(self, *args, **options):
        # vHost = VHost.objects.get(pk=options["vhost"][0])
        with open(options["in_file"][0],"r") as fh:
            imported_data = json.loads(fh.read())
            driverObj,created = DataEngineDriver.objects.get_or_create(class_name=imported_data.get("class_name"))
            driverObj.name = imported_data.get("name")
            driverObj.version = imported_data.get("version")
            driverObj.homepage = imported_data.get("homepage")
            driverObj.author = imported_data.get("author")
            driverObj.save()
            dhObj = DataEngineDriverHistory.objects.create(driver=driverObj)
            dhObj.updated = now()
            dhObj.version = driverObj.version
            dhObj.save()

            self.stdout.write(self.style.MIGRATE_LABEL(f'Driver {driverObj.name} v{driverObj.version} - installed'))
            #



