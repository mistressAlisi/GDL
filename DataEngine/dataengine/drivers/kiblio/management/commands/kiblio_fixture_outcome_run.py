import json
from uuid import UUID

from django.core.management.base import BaseCommand
from django.db.models import Q
from django.utils.text import slugify

from parameters.models import VHost
from providers.apisports.models import League,CoreSportMap
from dataengine.drivers.kiblio.api.http import KiblHttpAPI
from sports.models import Sport
from providers.apisports.tasks import amf, bab, base, fball


class Command(BaseCommand):
    help = 'KBL.io api test'

    def add_arguments(self, parser):
        parser.add_argument("vhost",nargs='+', type=UUID,help="VHost to work on.")
        parser.add_argument("--fixture",nargs='+', type=int,help="Fixture to work on.")


    def handle(self, *args, **options):
        vhost = VHost.objects.get(uuid=options['vhost'][0])
        self.stdout.write(self.style.MIGRATE_HEADING(f"Working on VHost {vhost}"))
        apiObj = KiblHttpAPI(vhost)

        self.stdout.write(self.style.MIGRATE_HEADING(f"Fetching upcoming fixtures..."))
        # _fixture = apiObj.fetch_upcoming_fixtures()
        if "fixture" in options and options["fixture"] != None:
            _fixture = apiObj.get_fixture(options['fixture'][0])
        else:
            _fixture = apiObj.get_all_fixtures()
        # Get Markets:
        # print(_fixture)
        self.stdout.write(self.style.MIGRATE_HEADING(f"Starting Fixture Run"))
        for fixture in _fixture:
            self.stdout.write(self.style.MIGRATE_HEADING(f"Working on fixture {fixture}"))
            fdata = apiObj.fetch_fixture_outcomes(fixture=fixture)
            print(fdata)




