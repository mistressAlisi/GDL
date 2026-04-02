import logging
import asyncio
from django.core.management.base import BaseCommand
from game.gdlcore.gdldaemon.gdldaemon import GDLDaemon


class Command(BaseCommand):
    help = 'Run the GDL async daemon inside Django context'

    def add_arguments(self, parser):
        parser.add_argument(
            '--host',
            type=str,
            default='0.0.0.0',
            help='WebSocket server host to bind'
        )
        parser.add_argument(
            '--port',
            type=int,
            default=9002,
            help='WebSocket server port to bind'
        )
        parser.add_argument(
            '--mgmt-host',
            type=str,
            default='127.0.0.1',
            help='Management host for proxy registration'
        )
        parser.add_argument(
            '--mgmt-port',
            type=int,
            default=9001,
            help='Management port for proxy registration'
        )
        parser.add_argument(
            '--proxy-url',
            type=str,
            help='Proxy registration URL (repeatable)'
        )
        parser.add_argument(
            "-l",
            type=str,
            nargs=1,
            help="Log level (DEBUG, INFO, WARNING, ERROR)"
        )

    def handle(self, *args, **options):
        host = options['host']
        port = options['port']
        mgmt_host = options['mgmt_host']
        mgmt_port = options['mgmt_port']

        proxy_url = options.get('proxy_url') or f"http://{mgmt_host}:{mgmt_port}/v1/backends"

        if options.get("l"):
            level = options["l"][0].upper()
            logging.basicConfig(
                level=getattr(logging, level, logging.INFO),
                format="[%(asctime)s] [%(levelname)s] %(name)s: %(message)s",
                force=True
            )

        self.stdout.write(self.style.SUCCESS(
            f"Starting GDL Daemon on ws://{host}:{port} "
            f"with management at {mgmt_host}:{mgmt_port} "
            f"registering to {proxy_url}"
        ))

        daemon = GDLDaemon(
            host=host,
            port=port,
            mgmt_host=mgmt_host,
            mgmt_port=mgmt_port,
            proxy_register_url=proxy_url or None
        )

        async def _main():
            await daemon.start()

        asyncio.run(_main())
