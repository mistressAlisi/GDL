import asyncio
import json
import logging
from types import SimpleNamespace

from asgiref.sync import sync_to_async
from aio_pika import connect_robust, IncomingMessage, ExchangeType
from django.db import close_old_connections
from django.utils.timezone import localtime

from asynctools.abc import AsyncWorkerABC


class AsyncKIBLAMQPWorker(AsyncWorkerABC):
    """
    Async AMQP consumer daemon using aio_pika.
    Integrated with AsyncWorkerABC lifecycle.
    """

    def __init__(
        self,
        vhost,
        logger=logging.getLogger("AsyncKIBLAMQPWorker"),
        name="KIBLAMQPWorker",
        interval: float = 5,
        run_in_process: bool = True,
        loki_url=None,
    ):
        super().__init__(
            vhost=vhost, logger=logger, name=name, interval=interval, run_in_process=run_in_process,loki_url=loki_url
        )



    def _child_init(self):
        """
        Runs inside the forked child *after* django.setup().
        Safe place for model imports.
        """
        super()._child_init()
        self._connection = None
        self._channel = None
        self._queues = []
        self._connected = asyncio.Event()
        self.amqp_url = "amqps://miker:MikeR88!@rabbitmq.kibl.io/"
        from dataengine.drivers.kiblio.models import Sportsbook, Fixture, Participant, FixtureMarket

        from parameters.models import Timezone, VHostParameterRegistry
        self.last_timestamp = localtime()
        self.models = SimpleNamespace(
            Sportsbook=Sportsbook,
            Fixture=Fixture,
            Participant=Participant,
            FixtureMarket=FixtureMarket,
            Timezone=Timezone,
            VHostParameterRegistry=VHostParameterRegistry,

        )

        from ...api.common import process_fixture_market_data, KIBL_MARKET_UPDATE_FIELDS, process_fixture_data, \
            process_fixture_outcomes_data
        self.process_fixture_market_data = process_fixture_market_data
        self.KIBL_MARKET_UPDATE_FIELDS = KIBL_MARKET_UPDATE_FIELDS
        self.process_fixture_data = process_fixture_data
        self.process_fixture_outcomes_data = process_fixture_outcomes_data

    async def _connect(self):
        """Establish AMQP connection and channel."""
        try:
            self._connection = await connect_robust(self.amqp_url)
            self._channel = await self._connection.channel()
            self._connected.set()
            self.logger.info("Connected to RabbitMQ.")
        except Exception as e:
            self.logger.error(f"AMQP connection failed: {e}")
            await asyncio.sleep(10)

    async def _subscribe(self):
        """Attach consumers to queues."""
        queues = [
            ("miker.get.info.markets", self._on_mkt_message),
            ("miker.get.info.fixtures", self._on_fxt_message),
            ("miker.get.info.outcomes", self._on_outc_message),
        ]
        for queue_name, handler in queues:
            try:
                queue = await self._channel.declare_queue(queue_name, durable=True)
                await queue.consume(lambda msg: asyncio.create_task(handler(msg)))
                self._queues.append(queue)
                self.logger.info(f"Subscribed to queue: {queue_name}")
            except Exception as e:
                self.logger.error(f"Failed to subscribe to {queue_name}: {e}")

    async def _work_cycle(self):
        """Periodic heartbeat, ensures connection health."""
        if not self._connection or self._connection.is_closed:
            self._connected.clear()
            await self._connect()
            if self._connection and not self._connection.is_closed:
                await self._subscribe()
        self.logger.debug("KIBL AMQP worker heartbeat tick.")

    async def _run(self):
        """Custom run loop integrated with ABC lifecycle."""
        await AsyncWorkerABC._run(self)
        try:
            await self._connect()
            if self._connection and not self._connection.is_closed:
                await self._subscribe()

            while self._running:
                await self._work_cycle()
                # await sync_to_async(lambda:close_old_connections(),thread_sensitive=True)()
                await asyncio.sleep(self.interval)

        except asyncio.CancelledError:
            self.logger.info(f"{self.name} cancelled.")
        except Exception as e:
            self.logger.exception(f"{self.name} crashed: {e}")
        finally:
            await self._cleanup()

    async def _on_mkt_message(self, message: IncomingMessage):
        async with message.process(ignore_processed=True):
            try:
                mkt_msg = json.loads(message.body.decode("utf-8"))
                for entry in mkt_msg.get("result", []):
                    for participant in entry.get("participants", []):
                        await self._handle_market_update(participant)
            except Exception as e:
                self.logger.exception(f"Error processing market message: {e}")

    async def _on_fxt_message(self, message: IncomingMessage):
        async with message.process(ignore_processed=True):
            try:
                fxt_msg = json.loads(message.body.decode("utf-8"))
                api_key = fxt_msg.get("api_key")

                if api_key == "get_sport_market_info_by_interest:markets":
                    return await self._on_mkt_message(message)
                if api_key != "get_sport_market_info_by_interest:fixtures":
                    self.logger.debug(f"Ignored fixture message with key: {api_key}")
                    return

                for entry in fxt_msg.get("result", []):
                    fixture_obj = await sync_to_async(self.process_fixture_data)(entry, self.vhost)
                    self.logger.info(f"Updated fixture {fixture_obj.fixture_id}")

            except Exception as e:
                self.logger.exception(f"Error processing fixture message: {e}")

    async def _on_outc_message(self, message: IncomingMessage):
        async with message.process(ignore_processed=True):
            try:
                outc_msg = json.loads(message.body.decode("utf-8"))
                api_key = outc_msg.get("api_key")

                if api_key == "get_sport_market_info_by_interest:markets":
                    return await self._on_mkt_message(message)
                if api_key != "get_sport_market_info_by_interest:outcomes":
                    self.logger.debug(f"Ignored outcome message with key: {api_key}")
                    return

                for entry in outc_msg.get("result", []):
                    outcome_obj, _, _ = await sync_to_async(self.process_fixture_outcomes_data,thread_sensitive=False)(
                        entry, self.vhost
                    )
                    if outcome_obj:
                        osync = await sync_to_async(lambda: outcome_obj.fixture.fixture_id,thread_sensitive=False)()
                        self.logger.info(f"Updated fixture {osync} outcomes.")
            except Exception as e:
                self.logger.exception(f"Error processing outcome message: {e}")

    async def _handle_market_update(self, participant):
        """ORM handler for market messages."""
        try:
            sbk_obj = await sync_to_async(lambda:self.models.Sportsbook.objects.get(feed_source_id=participant["feed_source_id"],vhost=self.vhost),thread_sensitive=False)()
            fixture_obj = await sync_to_async(lambda:self.models.Fixture.objects.get(fixture_id=participant["fixture_id"],vhost=self.vhost),thread_sensitive=False)(
            )
            fmx_obj = await sync_to_async(self.process_fixture_market_data,thread_sensitive=False)(
                participant, self.vhost, fixture_obj, sbk_obj
            )
            if fmx_obj:
                osync = await sync_to_async(lambda: fixture_obj.fixture_id,thread_sensitive=False)()
                self.logger.info(f"Updated Markets for fixture {osync}")
        except Exception as e:
            self.logger.warning(f"Market update failed for participant {participant}: {e}")


    async def _cleanup(self):
        """Graceful shutdown and resource cleanup."""
        try:
            if self._connection and not self._connection.is_closed:
                await self._connection.close()
                self.logger.info("Disconnected from RabbitMQ.")
        except Exception as e:
            self.logger.warning(f"Error closing AMQP connection: {e}")