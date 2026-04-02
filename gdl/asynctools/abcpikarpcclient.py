# asynctools/abcpikarpcclient.py
import asyncio
import uuid

class GenericRPCClientMixin:
    rpc_queue = "rpc.get"
    rpc_timeout = 30

    async def _ensure_rpc_client(self):
        """
        Prepare the RPC reply queue on the existing AMQP channel.
        """
        if getattr(self, "_rpc_reply_queue", None) is not None:
            return  # already set up

        if not hasattr(self, "_amqp_channel") or self._amqp_channel is None:
            raise RuntimeError("AMQP channel not ready for RPC client setup")

        # Declare a temporary exclusive reply queue
        self._rpc_reply_queue = await self._amqp_channel.declare_queue(
            "",  # empty name → server generates unique queue name
            exclusive=False,
            auto_delete=False,
            durable=True,
        )

        # Register channel so `consume()` works
        self._amqp_channels[self._rpc_reply_queue.name] = self._amqp_channel

        # Start consuming for replies
        await self.consume(self._rpc_reply_queue.name, self._handle_rpc_response)

        # ✅ Mark RPC client as ready
        self._rpc_ready = True

        # Initialize the futures dict if not already
        if not hasattr(self, "_rpc_futures"):
            self._rpc_futures = {}

    async def _teardown_rpc_client(self):
        """
        Tear down the RPC client safely.
        """
        if getattr(self, "_rpc_reply_queue", None):
            try:
                await self._rpc_reply_queue.delete()
            except Exception:
                pass
            self._rpc_reply_queue = None

        self._rpc_ready = False
        self._rpc_futures = {}

    async def rpc_call(self, *, model, ids, page=1, page_size=500):
        # Ensure channel + reply queue exist
        await self._ensure_rpc_client()

        if not getattr(self, "_rpc_ready", False):
            raise RuntimeError("RPC client not ready (AMQP channel unavailable)")

        correlation_id = uuid.uuid4().hex
        loop = asyncio.get_running_loop()
        fut = loop.create_future()

        self._rpc_futures[correlation_id] = fut

        payload = {
            "model": model,
            "ids": ids,
            "page": page,
            "page_size": page_size,
        }

        await self.publish(
            self.rpc_queue,
            payload,
            correlation_id=correlation_id,
            reply_to=self._rpc_reply_queue.name,
        )

        try:
            return await asyncio.wait_for(fut, timeout=self.rpc_timeout)
        finally:
            self._rpc_futures.pop(correlation_id, None)

    async def _handle_rpc_response(self, payload, *, correlation_id=None, **_):
        if not correlation_id:
            return

        fut = self._rpc_futures.get(correlation_id)
        if fut and not fut.done():
            fut.set_result(payload)
