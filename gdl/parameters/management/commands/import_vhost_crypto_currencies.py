from django.core.management.base import BaseCommand
from tablib import Dataset

from parameters.models import VHost, VHostMenuEntry, VHostCryptoExchangeCurrencies


class Command(BaseCommand):
    help = 'Import a Crypto Currencies items  file for the Agent Dashboard for the given VHost.'
    def add_arguments(self, parser):
        # Named (optional) arguments
        parser.add_argument("vhost",type=str,nargs="+")
        parser.add_argument("in_file", type=str, nargs="+")
    def handle(self, *args, **options):
        vHost = VHost.objects.get(pk=options["vhost"][0])
        with open(options["in_file"][0],"r") as fh:
            imported_data = Dataset().load(fh.read(),'json')
            for entry in imported_data.dict:
                vCryptoObj,cc = VHostCryptoExchangeCurrencies.objects.get_or_create(vhost=vHost,symbol=entry["symbol"])
                if cc:
                    vCryptoObj.save()
                vCryptoObj.name = entry["name"]
                vCryptoObj.active=entry["active"]
                vCryptoObj.save()
            self.stdout.write(self.style.MIGRATE_LABEL(f'Virtual Host: {vHost.name} - UUID: {vHost.uuid} - processed'))




