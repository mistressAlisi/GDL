from itertools import zip_longest
from uuid import UUID

from tabulate import tabulate
from django.core.management.base import BaseCommand

from matches.models import Match
from outcomes.engine import OutcomesEngine
from outcomes.models import Outcome, OutcomeTeams, OutcomeSegmentScore
from parameters.models import VHost


class Command(BaseCommand):
    help = "Print outcomes for a given match in a terminal table"

    def add_arguments(self, parser):

        parser.add_argument("vhost_id", type=UUID, help="ID of the vhost")
        parser.add_argument("match_id", type=UUID, help="ID of the match")
    def handle(self, *args, **options):

        vhost = VHost.objects.get(uuid=options["vhost_id"])
        match = Match.objects.get(uuid=options["match_id"])

        engine = OutcomesEngine(vhost=vhost)
        print(match)
        fso = engine.get_final_scores(match)
        for fs in fso:
            print(f"--------[{fs}]--------")
            print(fso[fs]["score"])
            print("************")
            print(fso[fs]["status"])