import logging
import asyncio
from django.core.management.base import BaseCommand
from game.gdlgdlcore.gdlproxy.gdlproxy import GDLProxyDaemon, GDLBackendNode


class Command(BaseCommand):
    help = 'Run the GDL Proxy Daemon v1.1 inside Django context'

    def add_arguments(self, parser):
        parser.add_argument('--ws-host', type=str, default='0.0.0.0', help='WebSocket service host to bind')
        parser.add_argument('--ws-port', type=int, default=9000, help='WebSocket service port to bind')
        parser.add_argument('--admin-host', type=str, default='0.0.0.0', help='Admin API host to bind')
        parser.add_argument('--admin-port', type=int, default=9001, help='Admin API port to bind')
        parser.add_argument(
            "--backend", type=str, nargs="*", help="Optional initial backend(s) in host:port format"
        )
        parser.add_argument(
            "-l", type=str, nargs=1, help="Log level (DEBUG, INFO, WARNING, ERROR)"
        )

    def handle(self, *args, **options):
        ws_host = options['ws_host']
        ws_port = options['ws_port']
        admin_host = options['admin_host']
        admin_port = options['admin_port']

        # Setup logging
        if options.get("l"):
            level = options["l"][0].upper()
            logging.basicConfig(
                level=getattr(logging, level, logging.INFO),
                format="[%(asctime)s] [%(levelname)s] %(name)s: %(message)s",
                force=True
            )
        logger = logging.getLogger("gdl_proxy_daemon")

        # Parse optional backends
        backends = []
        if options.get("backend"):
            for bp in options["backend"]:
                try:
                    host, port_str = bp.split(":")
                    port = int(port_str)
                    backends.append(GDLBackendNode(host, port))
                except Exception as e:
                    logger.warning(f"Failed to parse backend '{bp}': {e}")

        logger.info(
            f"Starting GDL Proxy Daemon v1.1 on WS {ws_host}:{ws_port} "
            f"with Admin API on {admin_host}:{admin_port} "
            f"and {len(backends)} initial backends"
        )

        daemon = GDLProxyDaemon(
            listen_host=ws_host,
            listen_port=ws_port,
            admin_host=admin_host,
            admin_port=admin_port,
            backends=backends,
            logger=logger
        )

        async def _main():
            await daemon.start()

        asyncio.run(_main())
