import logging
import asyncio

from django.core.management import BaseCommand

from dataengine.drivers.kiblio.driver.async_worker import KIBLIOAsyncWorker

from parameters.models import VHost


class Command(BaseCommand):
    help = 'KIBL Async Rabbit Worker.'

    def add_arguments(self, parser):
        # Named (optional) arguments
        parser.add_argument("vhost", type=str, nargs="+")
        parser.add_argument("-l", type=str, nargs="+")

    def handle(self, *args, **options):
        # --- Get VHost ---
        vHost = VHost.objects.get(pk=options["vhost"][0])
        self.stdout.write(
            self.style.MIGRATE_HEADING(
                f"KIBL ASync Worker {vHost}"
            )
        )

        # --- Logging Level ---
        if options.get("l"):
            level = options["l"][0].upper()
            logging.basicConfig(
                level=getattr(logging, level, logging.INFO),
                format="[%(asctime)s] [%(levelname)s] %(name)s: %(message)s",
                force=True
            )

        # --- Initialize Engine ---
        engine = KIBLIOAsyncWorker(vhost=vHost,logger=logging.getLogger("KIBLIOAsyncWorker"))

        # --- Run Event Loop ---
        try:
            asyncio.run(engine.start())
        except KeyboardInterrupt:
            logging.warning("Daemon interrupted by user. Shutting down...")
        except Exception as e:
            logging.exception(f"Daemon crashed: {e}")
