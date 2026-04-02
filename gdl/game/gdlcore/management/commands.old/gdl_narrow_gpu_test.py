import numpy as np
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models import Q
from tablib import Dataset
from texttable import Texttable

from game.gdlgdlcore.algos.core import GDLCore
from game.gdlgdlcore.algos.gpucore_narrow import GDLGPUCore

from odds.models import MatchOddsSummary
from parameters.models import VHost, VHostMenuEntry, VHostCryptoExchangeCurrencies
from game.gdlgdlcore.tasks import gdl_algo_parallel_by_count

MATRIX_MAX_DEPTH=7
MATRIX_SIZE = 25
GDL = GDLCore()

class Command(BaseCommand):
    help = "Test GDL algo Narrow"
    def add_arguments(self, parser):
        # Named (optional) arguments
        parser.add_argument("--min_payout",type=int,nargs="+",default=6000)
        parser.add_argument("--count", type=int, nargs="+",default=8)
        parser.add_argument("--depth", type=int, nargs="+",default=6)
        parser.add_argument("--stake", type=int, nargs="+",default=6)

    def handle(self, *args, **options):
        if not options["min_payout"]:
            min_payout = 6000
            self.stdout.write(self.style.MIGRATE_HEADING(f"Selecting Possible Lines for GDL"))
        else:
            min_payout = options["min_payout"]

        if options["count"] != 0:
            count = options["count"][0]
        else:
            count = 32
        if options["depth"] != 0:
            depth = options["depth"]
        else:
            depth = 7
        if options["stake"] !=0:
            stake = options["stake"]
        else:
            stake = 6
        self.stdout.write(self.style.MIGRATE_HEADING(
                f"Selecting Possible Lines for GDL With min payout odds of {stake}:{min_payout} or more. Total of {count} tickets."))
        lines = MatchOddsSummary.objects.filter(Q(match__active=True) &  Q(match__open=True) & (Q(home_price__gt=0) | Q(away_price__gt=0) | Q (draw_price__gt=0)))
        line_ids = []
        for line in lines:
            line_ids.append(str(line.uuid))
        gdl_gpu = GDLGPUCore()
        col_data_list, updated_qs = gdl_gpu._run_gdl_algo1(
            line_ids=line_ids,
            lines_qs=MatchOddsSummary.objects.all(),
            min_payout=min_payout,
            stake=stake,
            depth=depth,
            count=count,
            serialise=True,
            neg_limit=-200,
            debug=True
        )
        # print(col_data_list)
        # print(updated_qs)
        # res = gdl_algo_parallel_by_count(min_payout,count,depth,stake).get(timeout=300)
        from texttable import Texttable
        import shutil
        # # Get current terminal width
        terminal_width = shutil.get_terminal_size((80, 20)).columns
        t = Texttable(max_width=terminal_width)
        labels = [f"Match {i + 1}" for i in range(0,depth)] + ["Total Odds","To Win"]
        # # print(labels)
        output = [labels]
        for col in col_data_list:
            data = []
            for i in range(0,depth):
                try:
                    data.append(col["odds"][i][1])
                except IndexError:
                    data.append("-")
            data.append(col["total_odds"])
            data.append(col["total_odds"]*stake)
            output.append(data)
        t.add_rows(output)
        print(t.draw())




