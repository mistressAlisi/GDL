import json

from django.core.management import BaseCommand
from django.utils.timezone import now

from dataengine.engine import DataEngine
from dataengine.engine.daemon import DataEngineAPIDaemon
from dataengine.models import DataEngineDriver, DataEngineDriverHistory, DataEngineVHostConfig
from matches.models import Match
from parameters.models import VHost


class Command(BaseCommand):
    help = 'Grader Run for Unqualified; Closed Matches.'
    def add_arguments(self, parser):
        # Named (optional) arguments
        parser.add_argument("vhost",type=str,nargs="+")
        # parser.add_argument("match", type=str, nargs="+")
    def handle(self, *args, **options):
        vHost = VHost.objects.get(pk=options["vhost"][0])
        self.stdout.write(self.style.MIGRATE_HEADING("Grader: Finding matches that are closed, unqualified; and executing them! {vhost}".format(vhost=vHost)))
        #matchObjects = Match.objects.filter(vhost=vHost,wagers_qualified=False,status_short="FINAL",uuid=options["match"][0])
        matchObjects = Match.objects.filter(vhost=vHost, wagers_qualified=False, status_short="FINAL")
        # print(matchObjects)
        from matches.signals import signal_match_final
        self.stdout.write(self.style.MIGRATE_LABEL(f"Found match {len(matchObjects)} without Qualified Wagers, but in FINAL State. Running the Grader ...."))
        signal_match_final.send(sender=self.__class__,matches=matchObjects,vhost=vHost)
