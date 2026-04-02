from django.core.management.base import BaseCommand
from tablib import Dataset

from parameters.models import VHost, VHostMenuEntry, VHostCryptoExchangeCurrencies


class Command(BaseCommand):
    help = 'Import a Crypto Currencies items  file for the Agent Dashboard for the given VHost.'
    def add_arguments(self, parser):
        # Named (optional) arguments
        parser.add_argument("vhost",type=str,nargs="+")
    def handle(self, *args, **options):
        vHost = VHost.objects.get(pk=options["vhost"][0])
        VHostCryptoExchangeCurrencies.objects.filter(vhost=vHost).delete()
        self.stdout.write(self.style.MIGRATE_LABEL(f'Virtual Host: {vHost.name} - UUID: {vHost.uuid} - processed'))




