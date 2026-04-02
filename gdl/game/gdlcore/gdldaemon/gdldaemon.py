import asyncio
import json
import logging
import httpx
import websockets
from collections.abc import Iterable
from websockets.exceptions import ConnectionClosed
from django.utils.timezone import localtime

from game.gdlcore.gdldaemon.handlers import CommandHandler
from asynctools.abc import AsyncWorkerABC


class GDLDaemon(AsyncWorkerABC):

    def _child_init(self):
        """
        Runs in worker context.
        Must ALWAYS ensure shutdown primitives exist.
        """
        from parameters.models import VHost

        if not hasattr(self, "_shutdown_event") or self._shutdown_event is None:
            self._shutdown_event = asyncio.Event()

        if self._vhost_uuid and self.vhost is None:
            self.vhost = VHost.objects.get(uuid=self._vhost_uuid)

    def __init__(
        self,
        host: str = "0.0.0.0",
        hosts: Iterable[str] | None = None,
        port: int = 19002,
        mgmt_host: str = "127.0.0.1",
        mgmt_port: int = 19001,
        proxy_register_url: str | None = None,
        watchdog_interval: int = 30,
        watchdog_max_failures: int = 3,
        registration_retry_interval: int = 5,
        registration_max_retries: int = 5,
        *args,
        **kwargs
    ):
        super().__init__(name="gdl_daemon", interval=5, *args, **kwargs)

        # ---- network ----
        self.bind_host = host
        self.port = port

        if hosts:
            self.advertised_hosts = list(dict.fromkeys(hosts))
        else:
            self.advertised_hosts = [host]

        self.mgmt_host = mgmt_host
        self.mgmt_port = mgmt_port

        # ---- proxy ----
        self.PROXY_REGISTER_URL = proxy_register_url
        self.WATCHDOG_INTERVAL = watchdog_interval
        self.WATCHDOG_MAX_FAILURES = watchdog_max_failures
        self.REG_RETRY_INTERVAL = registration_retry_interval
        self.REG_MAX_RETRIES = registration_max_retries

        # ---- runtime ----
        self.server = None
        self.server_task: asyncio.Task | None = None
        self.active_connections: set[websockets.WebSocketServerProtocol] = set()
        self.last_timestamp = None
        self._watchdog_failures = 0

        # ---- CRITICAL: must exist before start() ----
        self._shutdown_event = asyncio.Event()

    # -------------------
    # WebSocket server
    # -------------------
    async def _initialize_server(self):
        async def ws_handler(websocket):
            self.active_connections.add(websocket)
            handler = CommandHandler(websocket)

            try:
                async for raw in websocket:
                    try:
                        message = json.loads(raw)
                        await handler.handle(message)
                    except Exception as e:
                        await websocket.send(
                            json.dumps({"type": "error", "error": str(e)})
                        )
            except ConnectionClosed:
                pass
            finally:
                self.active_connections.discard(websocket)

        try:
            self.server = await websockets.serve(
                ws_handler,
                self.bind_host,
                self.port,
            )

            self.logger.info(
                f"GDL WebSocket server started on ws://{self.bind_host}:{self.port}"
            )

            if self.PROXY_REGISTER_URL:
                await self._register_with_proxy()

        except asyncio.CancelledError:
            # Expected during shutdown; do NOT treat as failure
            raise

        except Exception as e:
            self.logger.exception(f"Failed to start WebSocket server: {e}")
            self.server = None

    async def _stop_server(self):
        self.logger.info("Stopping GDL WebSocket server...")

        # ---- close clients ----
        if self.active_connections:
            await asyncio.gather(
                *[
                    ws.close(code=1001, reason="Server shutdown")
                    for ws in list(self.active_connections)
                ],
                return_exceptions=True,
            )
            self.active_connections.clear()

        # ---- stop server ----
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            self.server = None

        # ---- deregister ----
        if self.PROXY_REGISTER_URL:
            await self._deregister_from_proxy(self.PROXY_REGISTER_URL)

    async def _work_cycle(self):
        self.last_timestamp = localtime()

        self.logger.debug(
            f"GDL Heartbeat @ {self.last_timestamp} | "
            f"Active connections: {len(self.active_connections)}"
        )

        if not self.server:
            self.logger.warning("WebSocket server not running — attempting restart.")
            await self._initialize_server()

        if not hasattr(self, "_last_watchdog_check"):
            self._last_watchdog_check = asyncio.get_running_loop().time()

        now = asyncio.get_running_loop().time()
        if now - self._last_watchdog_check >= self.WATCHDOG_INTERVAL:
            await self._watchdog_check()
            self._last_watchdog_check = now

    async def _watchdog_check(self):
        if not self.server:
            self._watchdog_failures += 1
            self.logger.warning(
                f"Watchdog: WebSocket server not active "
                f"({self._watchdog_failures}/{self.WATCHDOG_MAX_FAILURES})"
            )
        else:
            self._watchdog_failures = 0

        if self._watchdog_failures >= self.WATCHDOG_MAX_FAILURES:
            self.logger.error("Watchdog: Server unresponsive, restarting...")
            await self._stop_server()
            await asyncio.sleep(2)
            await self._initialize_server()
            self._watchdog_failures = 0

    async def _cleanup(self):
        await self._stop_server()
        await super()._cleanup()

    # -------------------
    # Proxy registration
    # -------------------
    async def _register_with_proxy(self):
        url = self.PROXY_REGISTER_URL

        for attempt in range(1, self.REG_MAX_RETRIES + 1):
            try:
                async with httpx.AsyncClient() as client:
                    payload = {
                        "host": self.bind_host,
                        "port": self.port,
                        "mgmt_host": self.mgmt_host,
                        "mgmt_port": self.mgmt_port,
                    }

                    r = await client.post(url, json=payload, timeout=5)

                    if r.status_code in (200, 201, 204, 409):
                        self.logger.info(f"Registered with proxy {url}")
                        return

                    self.logger.warning(
                        f"Proxy {url} rejected registration: "
                        f"{r.status_code} {r.text}"
                    )

            except Exception as e:
                self.logger.warning(
                    f"Proxy {url} registration failed (attempt {attempt}): {e}"
                )

            await asyncio.sleep(self.REG_RETRY_INTERVAL)

        self.logger.error(f"Failed to register with proxy {url}")

    async def _deregister_from_proxy(self, url: str):
        try:
            async with httpx.AsyncClient() as client:
                payload = {
                    "host": self.bind_host,
                    "port": self.port,
                }

                r = await client.delete(url, json=payload, timeout=5)

                if r.status_code in (200, 204, 404):
                    self.logger.info(f"Deregistered from proxy {url}")
                else:
                    self.logger.warning(
                        f"Proxy {url} deregistration failed: "
                        f"{r.status_code} {r.text}"
                    )

        except Exception as e:
            self.logger.warning(f"Proxy {url} deregistration error: {e}")
