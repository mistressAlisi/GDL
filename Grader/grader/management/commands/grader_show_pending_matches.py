import json
import logging
from itertools import zip_longest

from django.core.management import BaseCommand
from django.db.models import OuterRef, Q, Exists
from django.utils.timezone import now, localtime
from tabulate import tabulate

import wager
from dataengine.engine import DataEngine
from dataengine.engine.daemon import DataEngineAPIDaemon
from dataengine.models import DataEngineDriver, DataEngineDriverHistory, DataEngineVHostConfig
from matches.models import Match
from outcomes.engine import OutcomesEngine
from parameters.models import VHost
from grader.daemon.core import GraderDaemon
from wager.models import Wager


class Command(BaseCommand):
    help = 'Run the grader daemon.'
    def add_arguments(self, parser):
        # Named (optional) arguments
        parser.add_argument("vhost",type=str,nargs="+")
        parser.add_argument("-l", type=str, nargs="+")
    def handle(self, *args, **options):
        vHost = VHost.objects.get(pk=options["vhost"][0])
        self.stdout.write(self.style.MIGRATE_HEADING("Grader: Showing pending Wagers and Matches in {vhost}".format(vhost=vHost)))
        engine = OutcomesEngine(vhost=vHost)
        # print(options)
        # if options["l"]:
        #     if options["l"][0] == "INFO":
        #         logging.basicConfig(level=logging.INFO)
        #     elif options["l"][0] == "DEBUG":
        #         logging.basicConfig(level=logging.DEBUG)
        #     elif options["l"][0] == "WARNING":
        #         logging.basicConfig(level=logging.WARNING)
        #     elif options["l"][0] == "ERROR":
        #         logging.basicConfig(level=logging.ERROR)
        # grade_daemon = GraderDaemon()
        # grade_daemon.setup(vHost, logging, True)
        # grade_daemon.run()
        # grade_daemon.join()
        wagers_subq = Wager.objects.filter(
            match=OuterRef("pk")
        ).filter(
            Q(status="P") | Q(status="M")
        )

        # main query
        match_qs = (
            Match.objects.filter(
                finished=False,
                # commence_time__gte=localtime()
            )
            .annotate(has_wagers=Exists(wagers_subq))
            .filter(has_wagers=True)
        )
        # print(match_qs)
        for match in match_qs:
            self.stdout.write(f"******Match:")
            self.stdout.write(
                tabulate(
                    [[match.uuid,match.home_team.name,match.away_team.name,match.commence_time.strftime("%Y/%m/%d %H:%I:%S"),match.status_short,match.status_long]],
                    headers=["UUID","Home Team", "Away Team", "Commence Time","Status Short", "Status Long"],
                    tablefmt="grid",
                )
            )
            self.stdout.write(f">>>Outcomes:")
            outcomes = engine.get_final_scores(match)
            for key,data in outcomes.items():
                self.stdout.write(f"******Outcome from: {key}")
                self.stdout.write(
                    tabulate(
                        [[data["score"]["home"],data["score"]["away"],data["status"]["status_short"],data["status"]["status_long"],data["status"]["is_end_segment"]]],
                        headers=["Home Score", "Away Score", "Status Short", "Status Long","IS End Segment"],
                        tablefmt="grid",
                    )
                )

            self.stdout.write(f">>>Wagers:")
            wager_table = []
            for wagerObj in Wager.objects.filter(match=match,vhost=vHost):
                wager_table.append([
                    wagerObj.uuid,
                    wagerObj.account.acctnum,
                    wagerObj.type,
                    wagerObj.status,
                    wagerObj.application_type.name if wagerObj.application_type else "",
                    wagerObj.team_1.name if wagerObj.team_1 else "",
                    wagerObj.team_2.name if  wagerObj.team_2 else "",
                    wagerObj.risk,
                    wagerObj.win,
                    wagerObj.created.strftime("%Y/%m/%d %H:%I:%S"),
                ])

            self.stdout.write(
                tabulate(
                    wager_table,
                    headers=["UUID","Acct","Type","Status","Application","Team 1","Team 2","Risk","Win","Created"],
                    tablefmt="grid",
                )
            )
            print("<><>**<><>**<><>**<><>**<><>**<><>**<><>**<><>**<><>**<><>")


