from django.core.management.base import BaseCommand
from tablib import Dataset

from parameters.models import VHost, TeaserBetsPayoutSettingsTable


class Command(BaseCommand):
    help = 'Import a Menu items  file for the Teaser Payout Levels for the given VHost.'
    def add_arguments(self, parser):
        # Named (optional) arguments
        parser.add_argument("vhost",type=str,nargs="+")
        parser.add_argument("in_file", type=str, nargs="+")
    def handle(self, *args, **options):
        vHost = VHost.objects.get(pk=options["vhost"][0])
        with open(options["in_file"][0],"r") as fh:
            imported_data = Dataset().load(fh.read(),'json')
            TeaserBetsPayoutSettingsTable.objects.filter(vhost=vHost).delete()
            for entry in imported_data.dict:
                payoutObj = TeaserBetsPayoutSettingsTable(
                    vhost=vHost,name=entry["name"],
                    payout_odds=entry["payout_odds"],
                    draws_push=entry["draws_push"],
                    draws_loose=entry["draws_loose"],
                    min_teams=entry["min_teams"],
                    max_teams=entry["max_teams"],
                    amf_points=entry["amf_points"],
                    bab_points=entry["bab_points"])
                payoutObj.save()
            self.stdout.write(self.style.MIGRATE_LABEL(f'Virtual Host: {vHost.name} - UUID: {vHost.uuid} - processed'))





