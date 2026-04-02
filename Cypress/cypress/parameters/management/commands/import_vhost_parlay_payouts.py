from django.core.management.base import BaseCommand
from tablib import Dataset

from parameters.models import VHost, ParlayBetsPayoutSettingsTable
from sports.models import Group


class Command(BaseCommand):
    help = 'Import a Menu items  file for the Parlay Payout Levels for the given VHost.'
    def add_arguments(self, parser):
        # Named (optional) arguments
        parser.add_argument("vhost",type=str,nargs="+")
        parser.add_argument("in_file", type=str, nargs="+")
    def handle(self, *args, **options):
        vHost = VHost.objects.get(pk=options["vhost"][0])
        with open(options["in_file"][0],"r") as fh:
            imported_data = Dataset().load(fh.read(),'json')
            ParlayBetsPayoutSettingsTable.objects.filter(vhost=vHost).delete()
            for entry in imported_data.dict:
                payoutObj = ParlayBetsPayoutSettingsTable(vhost=vHost,num_bets=entry["num_bets"],payout_odds=entry["payout_odds"],draws_push=entry["draws_push"],draws_loose=entry["draws_loose"])
                payoutObj.save()
                for group in entry["groups"]:
                    groupObj = Group.objects.get(slug=group)
                    payoutObj.groups.add(groupObj)
                payoutObj.save()
            self.stdout.write(self.style.MIGRATE_LABEL(f'Virtual Host: {vHost.name} - UUID: {vHost.uuid} - processed'))





