import asyncio
import json
import logging
from datetime import datetime

from django.core.management import BaseCommand
from django.utils.timezone import now

from dataengine.engine import DataEngine
from dataengine.engine.daemon import DataEngineAPIDaemon
from dataengine.models import DataEngineDriver, DataEngineDriverHistory, DataEngineVHostConfig
from grader.daemon.asynccore import AsyncGraderDaemon
from matches.models import Match
from parameters.models import VHost
from grader.daemon.core import GraderDaemon
from wager.models import Wager


class Command(BaseCommand):
    help = 'Run the grader daemon.'
    def add_arguments(self, parser):
        # Named (optional) arguments
        parser.add_argument("vhost",type=str,nargs="+")
        parser.add_argument("start", type=str, nargs="+")
        parser.add_argument("stop", type=str, nargs="+")
        parser.add_argument("-l", type=str, nargs="+")
    def handle(self, *args, **options):
        # --- Prepare Variables ---
        vHost = VHost.objects.get(pk=options["vhost"][0])
        start = datetime.strptime(options["start"][0],"%Y-%m-%d-%H:%M:%S")
        stop = datetime.strptime(options["stop"][0],"%Y-%m-%d-%H:%M:%S")
        if options["l"]:
            if options["l"][0] == "INFO":
                logging.basicConfig(level=logging.INFO)
            elif options["l"][0] == "DEBUG":
                logging.basicConfig(level=logging.DEBUG)
            elif options["l"][0] == "WARNING":
                logging.basicConfig(level=logging.WARNING)
            elif options["l"][0] == "ERROR":
                logging.basicConfig(level=logging.ERROR)
        # --- Initialize Engine ---
        engine = AsyncGraderDaemon(vhost=vHost,logger=logging.getLogger("AsyncGraderDaemon"))
        # -- Get Wagers ---
        self.stdout.write(self.style.MIGRATE_HEADING(f"Grader: Ungrader starting for {vHost}: Ungrading for wagers with Graded at Time from {start} to {stop}..."))
        loop = asyncio.new_event_loop()
        loop.run_until_complete(engine.ungrade_wagers(start,stop))
