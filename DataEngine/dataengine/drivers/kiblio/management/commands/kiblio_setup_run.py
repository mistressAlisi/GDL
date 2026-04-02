import json
from uuid import UUID

from django.core.management.base import BaseCommand
from django.db.models import Q
from django.utils.text import slugify

from parameters.models import VHost
from dataengine.drivers.kiblio.api.http import KiblHttpAPI


class Command(BaseCommand):
    help = 'KBL.io api test'

    def add_arguments(self, parser):
        parser.add_argument("vhost",nargs='+', type=UUID,help="VHost to work on.")


    def handle(self, *args, **options):
        vhost = VHost.objects.get(uuid=options['vhost'][0])
        self.stdout.write(self.style.MIGRATE_HEADING(f"Working on VHost {vhost}"))
        apiObj = KiblHttpAPI(vhost)
        # These are basic setup parameters:...
        self.stdout.write(self.style.MIGRATE_HEADING(f"Basic Setup..."))
        print(apiObj.fetch_regions())
        print(apiObj.fetch_market_genres())
        # print(apiObj.get_market_genres())
        print(apiObj.fetch_market_statuses())
        # print(apiObj.get_market_statuses())
        print(apiObj.fetch_segments())
        # print(apiObj.get_segments())
        print(apiObj.fetch_market_types())
        #print(apiObj.get_market_types())
        print(apiObj.fetch_betting_types())
        # print(apiObj.get_betting_types())
        self.stdout.write(self.style.MIGRATE_HEADING(f"Sports Setup..."))
        print(apiObj.fetch_sports())
        self.stdout.write(self.style.MIGRATE_HEADING(f"Leagues Setup..."))
        print(apiObj.fetch_leagues())
        self.stdout.write(self.style.MIGRATE_HEADING(f"Season/Team/State Setup..."))
        print(apiObj.fetch_seasons())
        print(apiObj.fetch_states())
        print(apiObj.fetch_participants())
        print(apiObj.fetch_sides())
        self.stdout.write(self.style.MIGRATE_HEADING(f"Locations, Types and Sportsbooks..."))
        print(apiObj.fetch_locations())
        print(apiObj.fetch_fixture_types())
        print(apiObj.fetch_sportsbooks())
        # ....and from here we go to leagues in season
        self.stdout.write(self.style.MIGRATE_HEADING(f"Fetching upcoming fixtures..."))
        _fixture = apiObj.fetch_upcoming_fixtures()
        # _fixture = apiObj.get_all_fixtures()
        # Get Markets:
        self.stdout.write(self.style.MIGRATE_HEADING(f"Starting Fixture Run"))
        for fixture in _fixture[0:10]:
            self.stdout.write(self.style.MIGRATE_HEADING(f"Working on fixture {fixture}"))
            apiObj.fetch_fixture_markets()



