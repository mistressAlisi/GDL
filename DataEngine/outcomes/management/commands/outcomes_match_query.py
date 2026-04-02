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
        outcomes = engine.get_outcomes(match)
        # print(outcomes)
        for out in outcomes:
            print(out)
            # self.stdout.write(f"\nOutcome: {out['outcome']}\n")
            #
            # # Segments table
            # seg_table = []
            # for seg in out["segments"]:
            #     if type(seg) == str:
            #         row = [seg,"","",""]
            #     else:
            #         row = [
            #             seg.segment,
            #             seg.team.name if hasattr(seg, "team") and seg.team else "-",
            #             seg.score,
            #             seg.is_winner,
            #         ]
            #     seg_table.append(row)
            # if len(seg_table)>1:
            #     self.stdout.write("Segments:")
            #     self.stdout.write(
            #         tabulate(seg_table, headers=["Segment", "Team", "Score", "Winner"], tablefmt="grid")
            #     )
            #
            # # Teams table (home / away split)
            # team_table = []
            # home_teams = out["teams"]["home"]
            # away_teams = out["teams"]["away"]
            # # print(home_teams)
            # # print(away_teams)
            # if home_teams or away_teams:
            #     for ht, at in zip_longest(home_teams[0], away_teams[0], fillvalue=None):
            #         team_table.append(
            #             [
            #                 ht.team.name if ht else "-",
            #                 ht.score if ht else 0,
            #                 ht.is_winner if ht else False,
            #                 at.team.name if at else "-",
            #                 at.score if at else 0,
            #                 at.is_winner if at else False,
            #             ]
            #         )
            #
            #     self.stdout.write("Teams:")
            #     self.stdout.write(
            #         tabulate(
            #             team_table,
            #             headers=["Home Team", "Home Score", "Home Winner", "Away Team", "Away Score", "Away Winner"],
            #             tablefmt="grid",
            #         )
            #     )
