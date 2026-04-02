import json
import logging
import asyncio

from django.core.management import BaseCommand
from django.utils.timezone import now

from dataengine.drivers.kiblio.driver.async_worker import KIBLIOAsyncWorker
from dataengine.models import DataEngineDriver, DataEngineDriverHistory, DataEngineVHostConfig
from parameters.models import VHost


class Command(BaseCommand):
    help = 'DataEngine Async Daemon Runner.'

    def add_arguments(self, parser):
        # Named (optional) arguments
        parser.add_argument("vhost", type=str, nargs="+")
        parser.add_argument("-l", type=str, nargs="+")

    def handle(self, *args, **options):
        # --- Get VHost ---
        vHost = VHost.objects.get(pk=options["vhost"][0])
        self.stdout.write(
            self.style.MIGRATE_HEADING(
                f"DataEngine KIBLIO Async Daemon starting for {vHost}"
            )
        )

        # --- Logging Level ---
        if options.get("l"):
            level = options["l"][0].upper()
            logging.basicConfig(
                level=getattr(logging, level, logging.INFO),
                format="[%(asctime)s] [%(levelname)s] %(name)s: %(message)s",
            )

        # --- Initialize Engine ---
        engine = KIBLIOAsyncWorker(vhost=vHost,logger=logging.getLogger("KIBLIOAsyncWorker"))
        engine._child_init()

        # --- Run Event Loop ---
        try:
            asyncio.run(engine.start())
        except KeyboardInterrupt:
            logging.warning("Daemon interrupted by user. Shutting down...")
        except Exception as e:
            logging.exception(f"Daemon crashed: {e}")
