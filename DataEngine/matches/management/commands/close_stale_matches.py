from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils.timezone import now, localdate, localtime

from matches.models import Match
from parameters.models import VHost


class Command(BaseCommand):
    help = 'Close all stale and finished matches.'
    def add_arguments(self, parser):
        # Named (optional) arguments
        parser.add_argument("vhost",type=str,nargs="+")
        parser.add_argument("-l", type=str, nargs="+")

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING(f"Close all Stale Matches..."))
        vHost = VHost.objects.get(pk=options["vhost"][0])
        matches = Match.objects.filter(vhost=vHost,commence_time__lte=now(),score_closed=False)
        for match in matches:
            if match.commence_time:
                delta = match.commence_time - localtime()
                print(f"Match: {match.uuid}, Delta: {delta}, Commence time: {match.commence_time}")
                if abs(delta) >= timedelta(hours=12):
                    # print(delta)
                    match.finished = True
                    match.score_closed = True
                    match.save()
                    print(f"Match: {match.uuid}, should be closed.")

        matches = Match.objects.filter(vhost=vHost, commence_time__gte=now(),finished=True)

        for match in matches:
            print(f"Match: {match.uuid}, should not be closed: unclosing: {match.commence_time} / {match.get_match_name()}")
            match.finished = False
            match.score_closed = False
            match.save()
        # matches.update(open=False,finished=True,finished_at=now())
        # self.stdout.write(self.style.SUCCESS(f"Closed {len(matches)} matches."))