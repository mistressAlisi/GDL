import json

from django.core.management import BaseCommand
from django.utils.timezone import now

from dataengine.engine import DataEngine
from dataengine.models import DataEngineDriver, DataEngineDriverHistory, DataEngineVHostConfig
from parameters.models import VHost


class Command(BaseCommand):
    help = 'Dataengine Self-Test.'
    def add_arguments(self, parser):
        # Named (optional) arguments
        parser.add_argument("vhost",type=str,nargs="+")
    def handle(self, *args, **options):
        vHost = VHost.objects.get(pk=options["vhost"][0])
        self.stdout.write(self.style.MIGRATE_HEADING("DataEngine Self-Test for Vhost {vhost}".format(vhost=vHost)))
        dataEngine = DataEngine(vhost=vHost)
        dataEngine._load_driver(dataEngine.drivers[0].driver)
        # print(dataEngine.sync_segments(True))
        print(dataEngine.sync_outcomes(True))
#