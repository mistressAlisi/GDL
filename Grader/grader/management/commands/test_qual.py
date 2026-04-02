import asyncio
import json
import logging

from asgiref.sync import async_to_sync
from django.core.management import BaseCommand
from django.utils.timezone import now

from dataengine.engine import DataEngine
from dataengine.engine.daemon import DataEngineAPIDaemon
from dataengine.models import DataEngineDriver, DataEngineDriverHistory, DataEngineVHostConfig
from grader.modules.straight_wager_async import StraightWagerGraderAsync
from matches.models import Match
from parameters.models import VHost
from grader.daemon.core import GraderDaemon
from wager.models import Wager


class Command(BaseCommand):
    help = 'Run the grader daemon.'
    def add_arguments(self, parser):
        # Named (optional) arguments
        parser.add_argument("wager",type=str,nargs="+")
        parser.add_argument("-l", type=str, nargs="+")
    def handle(self, *args, **options):
        wager = Wager.objects.get(pk=options["wager"][0])
        vHost = wager.vhost
        self.stdout.write(self.style.MIGRATE_HEADING("Grader: Starting Grader Daemon for {vhost}".format(vhost=vHost)))
        # print(options)
        if options["l"]:
            if options["l"][0] == "INFO":
                logging.basicConfig(level=logging.INFO)
            elif options["l"][0] == "DEBUG":
                logging.basicConfig(level=logging.DEBUG)
            elif options["l"][0] == "WARNING":
                logging.basicConfig(level=logging.WARNING)
            elif options["l"][0] == "ERROR":
                logging.basicConfig(level=logging.ERROR)
        gss = StraightWagerGraderAsync(vhost=vHost)
        print(asyncio.get_event_loop().run_until_complete(gss._grade_wager_func(wager)))
        # wager.status = "P"
        # wager.save()
        # for node in wager.bet_data["nodes"]:
        #     wnobj = Wager.objects.get(pk=node)
        #     wnobj.status = "P"
        #     wnobj.save()
        # wager.match.wagers_graded = False
        # worker_thread = GraderWorkerThread(vHost, logging, matchObjs=[wager.match], verbose=True)
        # worker_thread.start()
        # print("*****")
        # print(wager.status)
        # print("*****")
        # for node in wager.bet_data["nodes"]:
        #     wnobj = Wager.objects.get(pk=node)
        #     print(wnobj.status)
        #     print("<><><><>")
        # # qualDaemon.run()
        # # qualDaemon.join()