import asyncio
import logging
import signal

from django.core.management.base import BaseCommand

from dataengine.drivers.statelottery.daemons.lottery_daemon import LotteryScrapeDaemon
from parameters.models import VHost


class Command(BaseCommand):
    help = 'Run the lottery scraping daemon'

    def add_arguments(self, parser):
        parser.add_argument("vhost", type=str, nargs="+")
        parser.add_argument(
            '-i', '--interval',
            type=int,
            default=60,
            help='Check interval in seconds (default: 60)'
        )
        parser.add_argument("-l", type=str, nargs="+")

    def handle(self, *args, **options):
        interval = options['interval']
        vHost = VHost.objects.get(pk=options["vhost"][0])

        # Set up logging
        if options.get("l"):
            level = options["l"][0].upper()
            logging.basicConfig(
                level=getattr(logging, level, logging.INFO),
                format="[%(asctime)s] [%(levelname)s] %(name)s: %(message)s",
                force=True,
            )



        self.stdout.write("=" * 60)
        self.stdout.write("Lottery Scrape Daemon")
        self.stdout.write("=" * 60)
        self.stdout.write(f"Check interval: {interval}s")
        self.stdout.write("Press Ctrl+C to stop")
        self.stdout.write("")

        # Create daemon
        daemon = LotteryScrapeDaemon(interval=interval, vhost=vHost, logger=logging.getLogger("lottery_scrape_daemon"))

        # Initialize child-specific resources (models, shutdown event, etc.)
        daemon._child_init()

        # --- Run Event Loop ---
        try:
            asyncio.run(daemon.start())
        except KeyboardInterrupt:
            logging.warning("Daemon interrupted by user. Shutting down...")
        except Exception as e:
            logging.exception(f"Daemon crashed: {e}")
