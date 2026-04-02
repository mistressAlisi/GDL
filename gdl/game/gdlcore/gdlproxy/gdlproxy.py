import asyncio
import json
import logging
from typing import List, Optional

import websockets
from websockets.exceptions import ConnectionClosed
from fastapi import FastAPI
from pydantic import BaseModel
from uvicorn import Config, Server


# -------------------
# Backend Node
# -------------------
class GDLBackendNode:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.alive = False

    @property
    def uri(self):
        return f"ws://{self.host}:{self.port}"


# -------------------
# Proxy Daemon v1.1
# -------------------
class GDLProxyDaemon:
    VERSION = "v1.1"
    def _child_init(self):
        from parameters.models import VHost
        if self._vhost_uuid and self.vhost is None:
            self.vhost = VHost.objects.get(uuid=self._vhost_uuid)
        self._shutdown_event = asyncio.Event()
    def __init__(
        self,
        listen_host: str = "0.0.0.0",
        listen_port: int = 19000,
        admin_host: str = "0.0.0.0",
        admin_port: int = 19001,
        backends: Optional[List[GDLBackendNode]] = None,
        retry_interval: int = 2,
        logger: Optional[logging.Logger] = None,
    ):
        self.listen_host = listen_host
        self.listen_port = listen_port
        self.admin_host = admin_host
        self.admin_port = admin_port
        self.backends = backends or []
        self.backend_index = 0
        self.retry_interval = retry_interval
        self.active_connections: set[websockets.WebSocketServerProtocol] = set()
        self.metrics = {
            "total_connections": 0,
            "failed_connections": 0,
        }
        self.server: Optional[asyncio.AbstractServer] = None
        self.logger = logger or logging.getLogger("gdl_proxy_daemon")
        self.logger.info(
            f"GDL Proxy Daemon {self.VERSION} initialized on WS {listen_host}:{listen_port} with Admin API on {admin_host}:{admin_port}"
        )

        # FastAPI app for management
        self.app = FastAPI(title=f"GDL Proxy Daemon {self.VERSION}")
        self._setup_admin_routes()

    # -------------------
    # Admin API
    # -------------------
    def _setup_admin_routes(self):
        daemon = self

        class BackendNodeModel(BaseModel):
            host: str
            port: int

        @self.app.post("/v1/backends")
        async def register_backend(node: BackendNodeModel):
            daemon.logger.debug(f"Received registration request: {node}")
            for b in daemon.backends:
                if b.host == node.host and b.port == node.port:
                    daemon.logger.info(f"Backend {node.host}:{node.port} already registered")
                    return {"status": "already_registered"}
            daemon.backends.append(GDLBackendNode(node.host, node.port))
            daemon.logger.info(f"Registered backend {node.host}:{node.port}")
            return {"status": "registered"}

        @self.app.delete("/v1/backends")
        async def deregister_backend(node: BackendNodeModel):
            daemon.logger.debug(f"Received deregistration request: {node}")
            before_count = len(daemon.backends)
            daemon.backends[:] = [b for b in daemon.backends if not (b.host == node.host and b.port == node.port)]
            if len(daemon.backends) < before_count:
                daemon.logger.info(f"Deregistered backend {node.host}:{node.port}")
                return {"status": "deregistered"}
            else:
                daemon.logger.warning(f"Attempted to deregister unknown backend {node.host}:{node.port}")
                return {"status": "not_found"}

        @self.app.get("/v1/backends")
        async def list_backends():
            return [
                {"host": b.host, "port": b.port, "alive": b.alive}
                for b in daemon.backends
            ]

        @self.app.get("/v1/metrics")
        async def metrics():
            return daemon.get_metrics()

    # -------------------
    # WebSocket proxy
    # -------------------
    async def _client_handler(self, client_ws, path=False):
        self.active_connections.add(client_ws)
        self.metrics["total_connections"] += 1
        try:
            await self.proxy_with_failover(client_ws)
        finally:
            self.active_connections.discard(client_ws)

    def select_backend(self) -> Optional[GDLBackendNode]:
        alive_nodes = [n for n in self.backends if n.alive]
        if not alive_nodes:
            return None
        node = alive_nodes[self.backend_index % len(alive_nodes)]
        self.backend_index += 1
        return node

    async def proxy_with_failover(self, client_ws):
        attempt = 0
        max_attempts = len(self.backends)
        while attempt < max_attempts:
            backend = self.select_backend()
            if not backend:
                await client_ws.send(json.dumps({"type": "error", "error": "No backend available"}))
                await client_ws.close()
                self.metrics["failed_connections"] += 1
                return
            self.logger.info(f"Proxying client to backend {backend.uri}")
            try:
                async with websockets.connect(backend.uri) as backend_ws:
                    await asyncio.gather(
                        self._pipe(client_ws, backend_ws),
                        self._pipe(backend_ws, client_ws)
                    )
                    return
            except (ConnectionClosed, OSError) as e:
                self.logger.warning(f"Backend {backend.uri} failed: {e}, retrying...")
                backend.alive = False
                attempt += 1
                await asyncio.sleep(self.retry_interval)

        await client_ws.send(json.dumps({"type": "error", "error": "All backends unavailable"}))
        await client_ws.close()
        self.metrics["failed_connections"] += 1

    async def _pipe(self, ws_from, ws_to):
        try:
            async for message in ws_from:
                await ws_to.send(message)
        except ConnectionClosed:
            pass

    # -------------------
    # Metrics
    # -------------------
    def get_metrics(self):
        return {
            "active_connections": len(self.active_connections),
            "total_connections": self.metrics["total_connections"],
            "failed_connections": self.metrics["failed_connections"],
            "backend_status": {b.uri: b.alive for b in self.backends},
        }

    # -------------------
    # Backend health checks
    # -------------------
    async def _health_check_loop(self):
        while True:
            for node in self.backends:
                try:
                    # Timeout prevents blocking on hung backends
                    async with asyncio.timeout(3):
                        async with websockets.connect(node.uri, ping_interval=5, ping_timeout=3):
                            node.alive = True
                            self.logger.debug(f"Backend {node.uri} alive")
                except Exception as e:
                    node.alive = False
                    self.logger.warning(f"Backend {node.uri} unreachable: {e}")
            await asyncio.sleep(5)

    # -------------------
    # Main run
    # -------------------
    async def start(self):
        self.logger.info(
            f"Starting GDL Proxy Daemon {self.VERSION} WS={self.listen_host}:{self.listen_port}, Admin API={self.admin_host}:{self.admin_port}"
        )

        # Start WebSocket server
        self.server = await websockets.serve(self._client_handler, self.listen_host, self.listen_port)
        self.logger.info(
            f"GDL Proxy Daemon {self.VERSION} WebSocket server listening on ws://{self.listen_host}:{self.listen_port}"
        )

        # Setup Uvicorn server programmatically
        config = Config(self.app, host=self.admin_host, port=self.admin_port, log_level="info", loop="asyncio")
        server = Server(config)

        # Start both tasks concurrently: admin API and backend health checks
        await asyncio.gather(
            server.serve(),
            self._health_check_loop()
        )
