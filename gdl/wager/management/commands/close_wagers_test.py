from django.core.management.base import BaseCommand

from wager import tasks


class Command(BaseCommand):
    help = 'Imports all the Sports Groups from The Odds API'

    def handle(self, *args, **options):
        #matchid = "beedd8d6-4abe-4583-a4c8-d9968f00169f"
        matchid = "2b34c20c-c848-4659-8431-8271be1ac25d"
        #matchid = "2fa2d848-e31a-4fe9-8da3-f73bc19791a4"
        #matchid = "921bdde3-97ac-4759-98b6-06a02a864254"
        #matchid  = "3758485d-f978-49e2-9724-b684fb724bfd"
        #matchid = "183e40f9-cff3-47ca-829b-f165a2a541f3"
        self.stdout.write(self.style.MIGRATE_HEADING(f"Queueing Task Close Wagers for {matchid} in Celery Workers..."))
        tasks.match_close_wagers.delay(matchid)