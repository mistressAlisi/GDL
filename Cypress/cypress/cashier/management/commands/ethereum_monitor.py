import logging

from django.core.management import BaseCommand
from parameters.models import VHost
from cashier.providers.hotwallet.webhook import EthereumTransactionMonitor


class Command(BaseCommand):
    help = 'Run the Ethereum transaction monitor daemon.'

    def add_arguments(self, parser):
        parser.add_argument("vhost", type=str, nargs="+")
        parser.add_argument("-l", type=str, nargs="+")

    def handle(self, *args, **options):
        vHost = VHost.objects.get(pk=options["vhost"][0])
        self.stdout.write(self.style.MIGRATE_HEADING(
            "Ethereum Monitor: Starting for {vhost}".format(vhost=vHost)
        ))

        if options["l"]:
            if options["l"][0] == "INFO":
                logging.basicConfig(level=logging.INFO)
            elif options["l"][0] == "DEBUG":
                logging.basicConfig(level=logging.DEBUG)
            elif options["l"][0] == "WARNING":
                logging.basicConfig(level=logging.WARNING)
            elif options["l"][0] == "ERROR":
                logging.basicConfig(level=logging.ERROR)

        monitor = EthereumTransactionMonitor(vHost)

        if not monitor.config.is_active:
            self.stdout.write(self.style.WARNING(
                "Ethereum monitoring is disabled for this vhost."
            ))
            return

        # Run continuous monitoring
        try:
            while True:
                stats = monitor.check_all_wallets()
                self.stdout.write(self.style.SUCCESS(
                    f"Checked {stats.get('checked', 0)} wallets: "
                    f"{stats.get('new', 0)} new, "
                    f"{stats.get('confirmed', 0)} confirmed, "
                    f"{stats.get('failed', 0)} failed"
                ))

                import time
                time.sleep(monitor.config.polling_interval_seconds)

        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING("\nMonitor stopped by user"))
