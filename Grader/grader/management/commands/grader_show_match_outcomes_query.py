import json
import logging

from django.core.management import BaseCommand
from django.db.models import OuterRef, Exists
from django.utils.timezone import now
from tabulate import tabulate

from dataengine.engine import DataEngine
from dataengine.engine.daemon import DataEngineAPIDaemon
from dataengine.models import DataEngineDriver, DataEngineDriverHistory, DataEngineVHostConfig
from grader.daemon.const import GRADER_DAEMON_OUTCOME_FILTER_Q
from matches.models import Match
from outcomes.models import Outcome
from parameters.models import VHost
from grader.daemon.core import GraderDaemon


class Command(BaseCommand):
    help = 'Run the grad†er daemon.'
    def add_arguments(self, parser):
        # Named (optional) arguments
        parser.add_argument("vhost",type=str,nargs="+")
        parser.add_argument("-l", type=str, nargs="+")
    def handle(self, *args, **options):
        vHost = VHost.objects.get(pk=options["vhost"][0])
        self.stdout.write(self.style.MIGRATE_HEADING("Grader: Showing Matches that would be Graded in {vhost}".format(vhost=vHost)))
        # print(options)
        outcomes_subq = Outcome.objects.filter(
            match=OuterRef("pk")
        ).filter(GRADER_DAEMON_OUTCOME_FILTER_Q)

        # Build Matches query first, and process them:
        matchObjects = (
            Match.objects.filter(finished=False, active=True, wagers_paid=False,vhost=vHost)
            .annotate(has_final_outcome=Exists(outcomes_subq))
            .filter(has_final_outcome=True)
        )
        matches = []
        for m in matchObjects:
            matches.append([m.uuid,m.name,m.commence_time,m.status_short,m.status_long,m.clock])
        self.stdout.write(
            tabulate(
                matches,
                headers=["UUID","Name","Commence Time","Status Short","Status Long","Clock"],
                tablefmt="grid",
            )
        )
