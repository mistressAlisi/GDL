from collections import defaultdict
from datetime import timedelta
import time
from itertools import batched

from django.conf import settings
from django.utils.timezone import now
from asgiref.sync import sync_to_async

from asynctools.abc import AsyncWorkerABC
from asynctools.abcpika import AsyncPikaPublisherMixin
from asynctools.abcredisstate import RedisStateMixin

from matches.models import Match
from odds.models import MatchOddsSummary
from outcomes.models import (
    Outcome,
    OutcomeSegmentScore,
    OutcomeTeams,
    OutcomeFinalMatchScores,
)
from minerve.toolkit.serialisers import filtered_serialiser_many


class DataPublisherDaemon(
    AsyncPikaPublisherMixin,
    AsyncWorkerABC,
    RedisStateMixin,
):
    amqp_url = settings.AMQP_PUBLISH_URL

    declared_queues = [
        "matches.match",
        "odds.matchodds",
        "outcomes.scores",
        "outcomes.consensus",
    ]

    MODEL_QUEUE_MAPPING = [
        # (Model, queue_name, object_type, updated_field)
        (Match, "matches.match", "match", "updated"),
        (MatchOddsSummary, "odds.matchodds", "odds_summary", "updated_at"),
        (Outcome, "outcomes.scores", "outcome_outcome", "updated_on"),
        (OutcomeSegmentScore, "outcomes.scores", "outcome_segment", "updated_at"),
        (OutcomeTeams, "outcomes.scores", "outcome_team", "updated_at"),
        (OutcomeFinalMatchScores, "outcomes.consensus", "outcome_consensus", "updated_at"),
    ]

    def __init__(
        self,
        vhost=object,
        logger=object,
        name="DataPublisherDaemon",
        interval: float = 100,
        run_in_process: bool = True,
        loki_url=None,
        control_queue=None,
        verbose: bool = True,
    ):
        self.verbose = verbose
        super().__init__(
            vhost,
            logger,
            name,
            interval,
            run_in_process,
            loki_url,
            control_queue,
        )

        # Start with the last 7 days
        self.current_timestamp = now() - timedelta(days=7)
        if self.verbose:
            self.logger.info("Publishing to AMQP: %s", self.amqp_url)

    # ──────────────────────────────
    # AMQP lifecycle
    # ──────────────────────────────

    async def _amqp_start(self):
        self._init_amqp_metrics()
        await self._redis_start()
        await AsyncPikaPublisherMixin._amqp_start(self)

        for queue_name in self.declared_queues:
            await self._amqp_setup_queue(queue_name)

        if self.verbose:
            self.logger.info("Publisher AMQP fully started")

    async def _amqp_stop(self):
        for queue_name in self._amqp_metrics:
            self._emit_amqp_metrics(queue_name, force=True)
        await self._redis_stop()
        await AsyncPikaPublisherMixin._amqp_stop(self)

    # ──────────────────────────────
    # Metrics
    # ──────────────────────────────

    def _init_amqp_metrics(self):
        self._amqp_metrics = defaultdict(
            lambda: {
                "published": 0,
                "failed": 0,
                "empty": 0,
                "latency_ms": [],
                "last_emit": None,
            }
        )

    def _emit_amqp_metrics(self, queue_name, force=False):
        metrics = self._amqp_metrics[queue_name]
        now_ts = time.time()
        if not force and metrics["last_emit"] and now_ts - metrics["last_emit"] < 30:
            return
        metrics["last_emit"] = now_ts
        metrics["latency_ms"] = metrics["latency_ms"][-100:]  # cap growth

        if self.verbose:
            self.logger.info(
                "AMQP[%s] published=%s failed=%s empty=%s",
                queue_name,
                metrics["published"],
                metrics["failed"],
                metrics["empty"],
            )

    # ──────────────────────────────
    # Publish helper
    # ──────────────────────────────

    async def _publish_to_queue(
            self,
            rows,
            since,
            queue_name,
            object_type,
            batch_size=20,
            model=False
    ):
        """
        Materialise rows in Redis and emit AMQP signals.
        """

        metrics = self._amqp_metrics[queue_name]

        if not rows:
            metrics["empty"] += 1
            return

        for batch in batched(rows, batch_size):
            try:
                # Serialize batch
                serialised_rows, _, _ = await sync_to_async(
                    lambda: filtered_serialiser_many(
                        batch,
                        include_files=True,
                        date_isoformat=True,
                    ),
                    thread_sensitive=False,
                )()

                # Materialise Redis state
                await self.set_state_many(self.vhost,model,serialised_rows)

                ids = [r["uuid"] for r in serialised_rows]
                if not ids:
                    continue

                # Emit signal
                payload = {
                    "type": object_type,
                    "ids": ids,
                    "count": len(ids),
                    "since": since.isoformat(),
                    "ts": now().isoformat(),
                }

                start = time.perf_counter()
                await self.publish(queue_name, payload)

                metrics["published"] += 1
                metrics["latency_ms"].append((time.perf_counter() - start) * 1000)

            except Exception:
                metrics["failed"] += 1
                self.logger.exception(
                    "Publish failed [%s] batch_size=%s",
                    queue_name,
                    len(batch),
                )

        # Periodically emit metrics
        if metrics["published"] % 10 == 0:
            self._emit_amqp_metrics(queue_name)

    # ──────────────────────────────
    # Work loop
    # ──────────────────────────────

    async def _work_cycle(self):
        cycle_start_ts = self.current_timestamp
        next_timestamp = now()

        for Model, queue_name, object_type, updated_field in self.MODEL_QUEUE_MAPPING:
            rows = await sync_to_async(
                lambda: list(
                    Model.objects.filter(
                        vhost=self.vhost,
                        **{f"{updated_field}__gte": cycle_start_ts}
                    ).order_by(updated_field)
                ),
                thread_sensitive=False,
            )()

            if self.verbose:
                self.logger.info(
                    "Publishing %d %s rows", len(rows), object_type
                )

            await self._publish_to_queue(
                rows, cycle_start_ts, queue_name, object_type,model=Model
            )

        # Advance timestamp after successful work cycle
        self.current_timestamp = next_timestamp
