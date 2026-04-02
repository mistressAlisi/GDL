import logging
import asyncio

from django.core.management import BaseCommand

from dataengine.drivers.apisports.driver.daemon.async_worker import APISportsAsyncWorker

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
                f"DataEngine APISports Async Daemon starting for {vHost}"
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
        engine = APISportsAsyncWorker(vhost=vHost,logger=logging.getLogger("APISportsAsyncWorker"))
        engine._child_init()
        # --- Run Event Loop ---
        try:
            asyncio.run(engine.start())
        except KeyboardInterrupt:
            logging.warning("Daemon interrupted by user. Shutting down...")
        except Exception as e:
            logging.exception(f"Daemon crashed: {e}")
