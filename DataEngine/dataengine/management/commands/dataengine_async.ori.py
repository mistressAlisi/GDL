import asyncio
import logging

from django.core.management import BaseCommand

from dataengine.drivers.apitennis.driver.daemons.apitennisasyncdaemon import APITennisAsyncDaemon
from dataengine.drivers.kiblio.driver.daemons.aioaqmpd import AsyncKIBLAMQPWorker
from dataengine.drivers.kiblio.driver.daemons.kiblasynchttpd import KIBLAsyncHTTPDDaemon
from parameters.models import VHost

# --- Import your worker classes ---
from dataengine.drivers.apisports.driver.daemon.async_worker import APISportsAsyncWorker
from dataengine.drivers.apitennis.driver.async_worker import APITennisAsyncWorker
from dataengine.drivers.kiblio.driver.async_worker import KIBLIOAsyncWorker


WORKER_MAP = {
    "KIBL": KIBLIOAsyncWorker,
    "KIBLAMQPD":AsyncKIBLAMQPWorker,
    "KIBLHTTPd":KIBLAsyncHTTPDDaemon,
    "Sports": APISportsAsyncWorker,
    "Tennis": APITennisAsyncDaemon,
}


class Command(BaseCommand):
    help = "DataEngine Async Daemon Runner for multiple workers."

    def add_arguments(self, parser):
        parser.add_argument("vhost", type=str, nargs=1, help="VHost primary key")
        parser.add_argument(
            "-l", type=str, nargs=1, help="Log level (DEBUG, INFO, WARNING, ERROR)"
        )
        parser.add_argument(
            "--workers",
            type=str,
            nargs="+",
            default=["Sports", "Tennis", "KIBL","KIBLAMQPD","KIBLHTTPd"],
            help="List of workers to start (e.g., Sports Tennis)",
        )

    def handle(self, *args, **options):
        # --- Get VHost ---
        vHost = VHost.objects.get(pk=options["vhost"][0])
        self.stdout.write(
            self.style.MIGRATE_HEADING(
                f"DataEngine Async Daemon starting for {vHost} with workers: {', '.join(options['workers'])}"
            )
        )

        # --- Logging Level ---
        if options["l"]:
            if options["l"][0] == "INFO":
                logging.basicConfig(level=logging.INFO, force=True)
            elif options["l"][0] == "DEBUG":
                logging.basicConfig(level=logging.DEBUG, force=True)
            elif options["l"][0] == "WARNING":
                logging.basicConfig(level=logging.WARNING, force=True)
            elif options["l"][0] == "ERROR":
                logging.basicConfig(level=logging.ERROR, force=True)

        workers = []
        for name in options["workers"]:
            if name not in WORKER_MAP:
                logging.warning(f"Unknown worker '{name}', skipping.")
                continue

            worker_cls = WORKER_MAP[name]
            worker_logger = logging.getLogger(name)
            worker = worker_cls(vhost=vHost, logger=worker_logger)
            workers.append(worker)

        if not workers:
            logging.error("No valid workers configured. Exiting.")
            return

        # --- Async Runner ---
        async def run_workers():
            tasks = [asyncio.create_task(w.start()) for w in workers]
            try:
                await asyncio.gather(*tasks,return_exceptions=True)
            except asyncio.CancelledError:
                logging.warning("Workers cancelled.")
            except Exception as e:
                logging.exception(f"Daemon crashed: {e}")
            finally:
                # Graceful shutdown
                await asyncio.gather(*(w.stop() for w in workers), return_exceptions=True)

        # --- Launch Event Loop ---
        try:
            asyncio.run(run_workers())
        except KeyboardInterrupt:
            logging.warning("Daemon interrupted by user. Shutting down...")
        except Exception as e:
            logging.exception(f"Daemon crashed: {e}")
