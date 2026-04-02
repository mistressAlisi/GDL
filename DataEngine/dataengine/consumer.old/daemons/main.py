import asyncio
import json

import aio_pika
from django.conf import settings

from asynctools.abc import AsyncWorkerABC
from asynctools.abcpikarpc import AsyncPikaConsumerMixin
from asynctools.abcpikarpcclient import GenericRPCClientMixin
from asynctools.abcredisstate import RedisStateMixin
from asynctools.rpc_registry import RPC_MODEL_REGISTRY, CONSUMER_MODEL_MAPPING


class DataConsumerDaemon(
    AsyncPikaConsumerMixin,
    GenericRPCClientMixin,
    RedisStateMixin,
    AsyncWorkerABC,
):
    """
    Data Consumer Daemon

    - Consumes AMQP signals
    - Reads materialised state from Redis
    - Fetches missing data via RPC
    - Hands off to downstream drivers
    """

    name = "data-consumer"
    amqp_url = settings.AMQP_PUBLISH_URL

    consumed_queues = [
        "matches.match",
        "odds.matchodds",
        "outcomes.scores",
        "outcomes.consensus",
    ]

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




    # -------------------------------------------------
    # AMQP lifecycle
    # -------------------------------------------------

    async def _amqp_start(self):
        # Redis first
        await self._redis_start()
        await AsyncPikaConsumerMixin._amqp_start(self)
        # await self._init_rpc_client()
        # AMQP setup: connection + single channel + _amqp_channels dict
        if not hasattr(self, "_amqp_channels"):
            self._amqp_channels = {}

        if not hasattr(self, "_amqp_connection") or self._amqp_connection is None:
            self._amqp_connection = await aio_pika.connect_robust(self.amqp_url)

        self._amqp_channel = await self._amqp_connection.channel()

        for queue_name in self.consumed_queues:
            self._amqp_channels[queue_name] = self._amqp_channel
            await self.consume(queue_name, self._handle_signal)

        # RPC client setup
        await self._ensure_rpc_client()

        if self.verbose:
            self.logger.info("Consumer ready for queues: %s", ", ".join(self.consumed_queues))

    async def _amqp_stop(self):
        # 1️⃣ Tear down RPC client first
        await self._teardown_rpc_client()

        # 2️⃣ Cancel queue consumers safely
        if hasattr(self, "_queues"):
            for queue in self._queues.values():
                try:
                    await queue.cancel()
                except Exception:
                    pass

        # 3️⃣ Stop Redis
        await self._redis_stop()

        # 4️⃣ Stop AMQP
        await AsyncPikaConsumerMixin._amqp_stop(self)

    async def publish(self, queue_name, payload, *, correlation_id=None, reply_to=None):
        """
        Send an RPC message over AMQP.
        """
        if not hasattr(self, "_amqp_channel") or self._amqp_channel is None:
            raise RuntimeError("AMQP channel not ready")

        message = aio_pika.Message(
            body=json.dumps(payload).encode(),
            correlation_id=correlation_id,
            reply_to=reply_to,
        )
        await self._amqp_channel.default_exchange.publish(
            message,
            routing_key=queue_name,
        )

    # -------------------------------------------------
    # Signal handler
    # -------------------------------------------------

    def _get_model_from_object_type(self, object_type):
        """
        Map object_type from the AMQP signal to the corresponding ORM/Redis model.
        """
        try:
            return CONSUMER_MODEL_MAPPING[object_type]
        except KeyError:
            raise ValueError(f"No model registered for object_type={object_type}")

    async def read_state_many(self, model, ids):
        """
        Fetch multiple objects from Redis by model and IDs.
        """
        if not ids:
            return []

        # Assuming self.redis is an async Redis client
        keys = [f"{model.__name__}:{id_}" for id_ in ids]

        try:
            values = await self.redis.mget(*keys)
        except Exception as e:
            self.logger.exception("Redis read failed for keys=%s", keys)
            return []

        # deserialize; skip missing
        return [json.loads(v) for v in values if v is not None]


    async def _handle_signal(self, payload: dict):
        """
        Signal-only message handler.

        payload = {
            "type": "match",
            "ids": [...],
            "count": N,
            "since": "...",
            "ts": "..."
        }
        """
        object_type = payload.get("type")
        ids = payload.get("ids", [])

        if not object_type or not ids:
            return

        if self.verbose:
            self.logger.info(
                "Received signal type=%s ids=%d",
                object_type,
                len(ids),
            )

        # 1️⃣ Try Redis first

        model = self._get_model_from_object_type(object_type)
        rows = await self.read_state_many(model, ids)
        rows = rows or {}

        missing_ids = [i for i in ids if i not in rows]

        # 2️⃣ Fetch missing via RPC
        if missing_ids:
            model_key = self._map_object_type(object_type)
            if not model_key:
                if self.verbose:
                    self.logger.warning(
                        "No RPC mapping for object_type=%s",
                        object_type,
                    )
                return

            if self.verbose:
                self.logger.info(
                    "RPC fetch required for %d %s objects",
                    len(missing_ids),
                    object_type,
                )

            rpc_response = await self.rpc_call(
                model=model_key,
                ids=missing_ids,
            )

            fetched = rpc_response.get("rows", [])

            if fetched:
                await self.write_state_many(
                    object_type=object_type,
                    rows=fetched,
                )
                rows.update({r["id"]: r for r in fetched})

        # 3️⃣ Hand off downstream
        await self._dispatch(object_type, rows)

    # -------------------------------------------------
    # Dispatch logic
    # -------------------------------------------------

    async def _dispatch(self, object_type: str, rows: dict):
        """
        Fan-out to downstream drivers.
        """
        if not rows:
            return

        if self.verbose:
            self.logger.info(
                "Dispatching %d %s objects",
                len(rows),
                object_type,
            )

        # TODO: wire drivers here
        # if object_type == "match":
        #     await self.match_driver.process(rows)

    # -------------------------------------------------
    # Required by AsyncWorkerABC
    # -------------------------------------------------

    async def _work_cycle(self):
        """
        Event-driven consumer.
        Never polls.
        Never exits unless cancelled.
        """
        await asyncio.Event().wait()

    # -------------------------------------------------
    # Helpers
    # -------------------------------------------------

    def _map_object_type(self, object_type: str) -> str:
        """
        Map signal object types → RPC registry keys
        """
        return {
            "match": "matches.Match",
            "odds_summary": "odds.MatchOddsSummary",
            "outcome_outcome": "outcomes.Outcome",
            "outcome_segment": "outcomes.OutcomeSegmentScore",
            "outcome_team": "outcomes.OutcomeTeams",
            "outcome_consensus": "outcomes.OutcomeFinalMatchScores",
        }.get(object_type)
