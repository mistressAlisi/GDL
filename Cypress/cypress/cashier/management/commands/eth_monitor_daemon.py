import logging
import asyncio
from datetime import datetime

from django.core.management import BaseCommand

from parameters.models import VHost
from cashier.providers.hotwallet.webhook import EthereumTransactionMonitor


class Command(BaseCommand):
    help = 'Ethereum Transaction Monitoring Daemon - Checks for incoming ETH deposits.'

    def add_arguments(self, parser):
        parser.add_argument(
            "vhost",
            type=str,
            help="VHost UUID to monitor"
        )
        parser.add_argument(
            "-i", "--interval",
            type=int,
            default=15,
            help="Polling interval in seconds (default: 15)"
        )
        parser.add_argument(
            "-l", "--log-level",
            type=str,
            default="INFO",
            choices=["DEBUG", "INFO", "WARNING", "ERROR"],
            help="Logging level (default: INFO)"
        )

    def handle(self, *args, **options):
        # Get VHost
        try:
            vhost = VHost.objects.get(pk=options["vhost"])
        except VHost.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f"VHost not found: {options['vhost']}")
            )
            return

        # Configure logging
        log_level = getattr(logging, options["log_level"].upper(), logging.INFO)
        logging.basicConfig(
            level=log_level,
            format="[%(asctime)s] [%(levelname)s] %(name)s: %(message)s",
        )
        logger = logging.getLogger("EthMonitorDaemon")

        self.stdout.write(
            self.style.MIGRATE_HEADING(
                f"Ethereum Transaction Monitor starting for {vhost}"
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                f"Polling interval: {options['interval']} seconds"
            )
        )

        # Initialize monitor
        monitor = EthereumTransactionMonitor(vhost)
        interval = options["interval"]

        # Run monitoring loop
        try:
            while True:
                try:
                    logger.info(f"[{datetime.now()}] Checking for new transactions...")
                    stats = monitor.check_all_wallets()

                    if stats.get("new", 0) > 0 or stats.get("confirmed", 0) > 0:
                        logger.info(
                            f"✅ Stats: {stats['new']} new, "
                            f"{stats['confirmed']} confirmed, "
                            f"{stats['failed']} failed, "
                            f"{stats['checked']} wallets checked"
                        )
                    else:
                        logger.debug(f"No new transactions. Checked {stats.get('checked', 0)} wallets.")

                except Exception as e:
                    logger.exception(f"Error checking transactions: {e}")

                # Sleep for the specified interval
                logger.debug(f"Sleeping for {interval} seconds...")
                asyncio.run(asyncio.sleep(interval))

        except KeyboardInterrupt:
            logger.warning("Daemon interrupted by user. Shutting down...")
            self.stdout.write(self.style.WARNING("Shutdown complete."))
        except Exception as e:
            logger.exception(f"Daemon crashed: {e}")
            self.stdout.write(self.style.ERROR(f"Fatal error: {e}"))
