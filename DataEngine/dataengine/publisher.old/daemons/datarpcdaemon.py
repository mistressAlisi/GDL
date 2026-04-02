import asyncio
from django.conf import settings

from asynctools.abc import AsyncWorkerABC
from asynctools.abcpika import AsyncPikaPublisherMixin

from asynctools.abcpikarpc import GenericRPCMixin, AsyncPikaConsumerMixin


class DataPublisherRPCDaemon(
    AsyncPikaPublisherMixin,
    AsyncPikaConsumerMixin,
    GenericRPCMixin,
    AsyncWorkerABC,
):
    """
    RPC daemon
    - Consumes rpc.get
    - Reads authoritative Postgres
    - Replies
    """

    name = "data-publisher-rpc"
    amqp_url = settings.AMQP_PUBLISH_URL
    declared_queues = ["rpc.get"]

    def __init__(
        self,
        vhost=object,
        logger=object,
        name=None,
        interval=0,
        run_in_process=True,
        loki_url=None,
        control_queue=None,
        verbose=True,
    ):
        self.verbose = verbose
        super().__init__(
            vhost=vhost,
            logger=logger,
            name=name or self.name,
            interval=interval,
            run_in_process=run_in_process,
            loki_url=loki_url,
            control_queue=control_queue,
        )

    async def _amqp_start(self):
        await AsyncPikaPublisherMixin._amqp_start(self)
        await self._amqp_setup_queue(self.rpc_queue)
        await self._setup_rpc()

        if self.verbose:
            self.logger.info("RPC daemon ready (authoritative Postgres reader)")

    async def _amqp_stop(self):
        await self._teardown_rpc()
        await AsyncPikaPublisherMixin._amqp_stop(self)

    async def _work_cycle(self):
        # Event-driven daemon: block forever
        await asyncio.Event().wait()
