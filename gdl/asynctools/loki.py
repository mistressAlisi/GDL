import contextlib
import logging
import time
import json
import httpx
import asyncio


class AsyncLokiHandler(logging.Handler):
    """
    Basic async Loki log handler using httpx.AsyncClient.
    Compatible with Loki v3 push API (same v1/push path).
    """

    def __init__(self, endpoint, labels=None, timeout=2.0):
        super().__init__()
        self.endpoint = endpoint.rstrip("/") + "/loki/api/v1/push"
        self.labels = labels or {"job": "python"}
        self.timeout = timeout

        # Dedicated httpx async client for Loki only
        self._client = httpx.AsyncClient(timeout=timeout)

        # Internal queue for log entries (non-blocking for logging thread)
        self._queue = asyncio.Queue()
        self._worker_task = None

    async def start(self):
        """Start background worker."""
        if self._worker_task is None:
            self._worker_task = asyncio.create_task(self._worker())

    async def stop(self):
        """Gracefully stop worker and close client."""
        if self._worker_task:
            self._worker_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._worker_task
        await self._client.aclose()

    def emit(self, record):
        """
        Called by logging. Must be sync, so we queue the log.
        """
        try:
            msg = self.format(record)

            ts_ns = int(time.time() * 1_000_000_000)

            self._queue.put_nowait((ts_ns, msg))
        except Exception:
            self.handleError(record)

    async def _worker(self):
        """Background task: send queued logs to Loki."""
        while True:
            ts, msg = await self._queue.get()

            payload = {
                "streams": [
                    {
                        "stream": self.labels,
                        "values": [[str(ts), msg]],
                    }
                ]
            }

            try:
                await self._client.post(
                    self.endpoint,
                    content=json.dumps(payload),
                    headers={"Content-Type": "application/json"},
                )
            except Exception:
                # Don't raise — log handlers must never crash the app
                pass

    async def aclose(self):
        if self.client:
            await self.client.aclose()

    def close(self):
        try:
            loop = asyncio.get_running_loop()
            if self.client:
                loop.create_task(self.client.aclose())
        except Exception:
            pass
        super().close()

# -----------------------------------------------------------------
# Metric Emitter (unchanged)
# -----------------------------------------------------------------

class LokiMetricEmitter:
    """
    Push structured metric JSON into Loki; Grafana can
    extract numeric fields via LogQL `unwrap`.
    """

    def __init__(self, logger, base_labels=None):
        self.logger = logger
        self.base_labels = base_labels or {}

    def emit(self, metric: str, value: float, **labels):
        record = {
            "metric": metric,
            "value": value,
            "labels": {**self.base_labels, **labels},
        }
        self.logger.info(json.dumps(record))


# -----------------------------------------------------------------
# Metric Emitter (unchanged)
# -----------------------------------------------------------------

class LokiMetricEmitter:
    """
    Push structured metric JSON into Loki; Grafana can
    extract numeric fields via LogQL `unwrap`.
    """

    def __init__(self, logger, base_labels=None):
        self.logger = logger
        self.base_labels = base_labels or {}

    def emit(self, metric: str, value: float, **labels):
        record = {
            "metric": metric,
            "value": value,
            "labels": {**self.base_labels, **labels},
        }
        self.logger.info(json.dumps(record))

