# asynctools/abcpikarpc.py
import json

import aio_pika
from asgiref.sync import sync_to_async
from django.core.paginator import Paginator

from asynctools.rpc_registry import RPC_MODEL_REGISTRY
from minerve.toolkit.serialisers import filtered_serialiser_many


class GenericRPCMixin:
    rpc_queue = "rpc.get"

    async def _setup_rpc(self):
        await self._amqp_setup_queue(self.rpc_queue)
        await self.consume(
            self.rpc_queue,
            self._handle_rpc_request,
        )

    async def _teardown_rpc(self):
        await self.cancel_consumer(self.rpc_queue)

    async def _handle_rpc_request(self, payload):
        """
        payload = {
            "model": "matches.Match",
            "ids": [...],
            "page": 1,
            "page_size": 500
        }
        """
        model_key = payload.get("model")
        ids = payload.get("ids", [])
        page = int(payload.get("page", 1))
        page_size = int(payload.get("page_size", 500))

        Model = RPC_MODEL_REGISTRY.get(model_key)
        if not Model:
            return {"error": f"Unknown model '{model_key}'"}

        if not ids:
            return {
                "model": model_key,
                "count": 0,
                "total": 0,
                "page": page,
                "page_size": page_size,
                "rows": [],
            }

        # AUTHORITATIVE READ
        qs = Model.objects.filter(uuid__in=ids).order_by("uuid")

        paginator = Paginator(qs, page_size)
        page_obj = paginator.get_page(page)

        rows = await sync_to_async(list)(
            page_obj.object_list
        )

        serialised, _, _ = await sync_to_async(
            lambda: filtered_serialiser_many(
                rows,
                include_files=True,
                date_isoformat=True,
            ),
            thread_sensitive=False,
        )()

        return {
            "model": model_key,
            "count": len(serialised),
            "total": paginator.count,
            "page": page,
            "page_size": page_size,
            "rows": serialised,
        }

class AsyncPikaConsumerMixin:
    """
    Adds basic AMQP consume / cancel support.

    Requires:
      - self._amqp_connection
      - self._amqp_channels dict
      - self.logger
    """

    def __init__(self, *args, **kwargs):
        self._amqp_consumers = {}
        super().__init__(*args, **kwargs)

    # -------------------------------------------------
    # lifecycle
    # -------------------------------------------------

    async def _amqp_start(self):
        """
        No-op by default.
        Publisher mixin owns connection/channel lifecycle.
        """
        return

    async def _amqp_stop(self):
        for queue_name in list(self._amqp_consumers.keys()):
            await self.cancel_consumer(queue_name)

    # -------------------------------------------------
    # consume
    # -------------------------------------------------

    async def consume(self, queue_name, handler):
        """
        handler(payload) -> response | None
        """

        channel = self._amqp_channels.get(queue_name)
        if not channel:
            raise RuntimeError(f"Queue not declared: {queue_name}")

        queue = await channel.declare_queue(queue_name, durable=True)

        async def _on_message(message: aio_pika.IncomingMessage):
            async with message.process(requeue=False):
                try:
                    payload = json.loads(message.body)

                    result = await handler(payload)

                    # RPC-style reply
                    if message.reply_to and result is not None:
                        response = json.dumps(result).encode()

                        await channel.default_exchange.publish(
                            aio_pika.Message(
                                body=response,
                                correlation_id=message.correlation_id,
                            ),
                            routing_key=message.reply_to,
                        )

                except Exception:
                    self.logger.exception(
                        "Error handling message on %s", queue_name
                    )
                    raise

        consumer_tag = await queue.consume(_on_message)
        self._amqp_consumers[queue_name] = (queue, consumer_tag)

        self.logger.info("Consuming queue=%s", queue_name)

    async def cancel_consumer(self, queue_name):
        entry = self._amqp_consumers.pop(queue_name, None)
        if not entry:
            return

        queue, consumer_tag = entry
        await queue.cancel(consumer_tag)

        self.logger.info("Stopped consuming queue=%s", queue_name)