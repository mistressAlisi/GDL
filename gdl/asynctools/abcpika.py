from collections import defaultdict
import time
import aio_pika
import asyncio
import json
from typing import Dict


class AsyncPikaPublisherMixin:
    """
    Adds async AMQP publishing capability to AsyncWorkerABC.
    """

    amqp_url: str = None  # must be provided
    publish_queues: Dict[str, float] = {}  # queue_name -> interval seconds
    _amqp_setup_lock: asyncio.Lock | None = None
    _amqp_connection: aio_pika.RobustConnection | None = None
    _amqp_channels: Dict[str, aio_pika.Channel]
    _amqp_exchanges: Dict[str, aio_pika.Exchange]
    _publish_tasks: list[asyncio.Task]

    async def _amqp_start(self):
        self.logger.info("Starting AMQP publisher")
        if self.publish_queues and not hasattr(self, "_build_publish_payload"):
            raise RuntimeError(
                "publish_queues defined but _build_publish_payload not implemented"
            )
        self._amqp_channels = {}
        self._amqp_exchanges = {}
        self._publish_tasks = []

        self._amqp_connection = await aio_pika.connect_robust(
            self.amqp_url
        )

        for queue_name in self.publish_queues:
            await self._amqp_setup_queue(queue_name)

        # start per-queue publish loops
        for queue_name, interval in self.publish_queues.items():
            task = asyncio.create_task(
                self._publish_loop(queue_name, interval),
                name=f"publish:{queue_name}",
            )
            self._publish_tasks.append(task)

    async def _amqp_setup_queue(self, queue_name: str):
        channel = await self._amqp_connection.channel(
            publisher_confirms=True
        )
        await channel.set_qos(prefetch_count=10)

        exchange = await channel.declare_exchange(
            name=f"{queue_name}.exchange",
            type=aio_pika.ExchangeType.DIRECT,
            durable=True,
        )

        queue = await channel.declare_queue(
            name=queue_name,
            durable=True,
        )

        await queue.bind(exchange, routing_key=queue_name)

        self._amqp_channels[queue_name] = channel
        self._amqp_exchanges[queue_name] = exchange

        self.logger.info(f"AMQP ready for queue={queue_name}")


    async def publish(self, queue_name: str, payload: dict):
        if self._amqp_setup_lock is None:
            self._amqp_setup_lock = asyncio.Lock()

        # 🔒 ensure setup exactly once
        if queue_name not in self._amqp_exchanges:
            async with self._amqp_setup_lock:
                if queue_name not in self._amqp_exchanges:
                    await self._amqp_setup_queue(queue_name)

        exchange = self._amqp_exchanges[queue_name]

        message = aio_pika.Message(
            body=json.dumps(payload).encode(),
            content_type="application/json",
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
        )

        await exchange.publish(message, routing_key=queue_name)

    async def _publish_loop(self, queue_name: str, interval: float):
        """
        One independent async loop per queue.
        Override _build_publish_payload in worker.
        """
        self.logger.info(f"Publish loop started for {queue_name}")

        while self._running and not self._exit:
            try:
                payload = await self._build_publish_payload(queue_name)
                if payload is not None:
                    await self.publish(queue_name, payload)
            except Exception:
                self.logger.exception(
                    f"Publish loop error queue={queue_name}"
                )

            await asyncio.sleep(interval)

    async def _amqp_stop(self):
        self.logger.info("Stopping AMQP publisher")

        for task in self._publish_tasks:
            task.cancel()

        await asyncio.gather(*self._publish_tasks, return_exceptions=True)

        if self._amqp_connection:
            await self._amqp_connection.close()

    def _init_amqp_metrics(self):
        self._amqp_metrics = defaultdict(lambda: {
            "published": 0,
            "failed": 0,
            "dropped": 0,
            "empty":0,
            "latency_ms": [],
        })

    def _emit_amqp_metrics(self, queue_name: str):
        if not self.loki_url or not hasattr(self,"loki"):
            return

        m = self._amqp_metrics[queue_name]

        if not m["latency_ms"]:
            avg_latency = 0
        else:
            avg_latency = sum(m["latency_ms"]) / len(m["latency_ms"])

        self.metrics_logger.info(json.dumps({
            "type": "amqp_publish_metrics",
            "queue": queue_name,
            "published": m["published"],
            "failed": m["failed"],
            "dropped": m["dropped"],
            "avg_latency_ms": round(avg_latency, 2),
            "samples": len(m["latency_ms"]),
            "interval": self.publish_queues.get(queue_name),
            "pid": self.pid,
            "worker": self.__class__.__name__,
        }))

        # reset rolling window
        m["latency_ms"].clear()