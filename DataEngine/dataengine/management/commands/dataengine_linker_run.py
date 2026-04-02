import importlib
import json
import logging

from django.core.management import BaseCommand
from django.utils.timezone import now

from dataengine.engine import DataEngine
from dataengine.engine.daemon import DataEngineAPIDaemon
from dataengine.linker.sports import DataEngineLinker
from dataengine.models import DataEngineDriver, DataEngineDriverHistory, DataEngineVHostConfig
from parameters.models import VHost


class Command(BaseCommand):
    help = 'Dataengine Linker Runner.'
    def add_arguments(self, parser):
        # Named (optional) arguments
        parser.add_argument("vhost",type=str,nargs="+")
        parser.add_argument("function", type=str, nargs="+")
        parser.add_argument("-l", type=str, nargs="+")
    def handle(self, *args, **options):
        vHost = VHost.objects.get(pk=options["vhost"][0])
        function = options["function"][0]
        self.stdout.write(self.style.MIGRATE_HEADING(f"DataEngine Linker starting for {vHost}: Linkage Type {function}"))
        if options["l"]:
            if options["l"][0] == "INFO":
                logging.basicConfig(level=logging.INFO)
            elif options["l"][0] == "DEBUG":
                logging.basicConfig(level=logging.DEBUG)
            elif options["l"][0] == "WARNING":
                logging.basicConfig(level=logging.WARNING)
            elif options["l"][0] == "ERROR":
                logging.basicConfig(level=logging.ERROR)
        _driver_daemons = importlib.import_module(f"dataengine.linker.{function}")
        dataEngine = _driver_daemons.DataEngineLinker(vhost=vHost)
        dataEngine.start()


#