import asyncio
import base64
import contextlib
import copy
import gzip
import json
import logging
import os
import queue
import re
import time
import traceback
import unicodedata
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from multiprocessing import Process, Queue
import multiprocessing as mp

import httpx
import psutil

from asgiref.sync import sync_to_async
from django.conf import settings
from django.core.files.base import ContentFile
from django.db import connections, models, close_old_connections
from django.db.models import Func, F, Value, FileField, ForeignKey
from django.forms import ImageField
from django.utils.text import slugify
from django.utils.timezone import now

from asynctools.loki import AsyncLokiHandler


# ──────────────────────────────────────────────
# Sync metadata
# ──────────────────────────────────────────────
SYNC_RELATED_FIELD_MAP = {
    "group": "group",
    "sport": "sport",
    "season": "season",
    "team": "team",
    "match": "match",
    "segment": "segment",
    "odds": "matchOdds",
    "outcome_teams_sync": "team",
}

NOISE = {
    "fc", "sc", "bc", "ac", "cf",
    "club", "sporting", "team", "the",
}


# ──────────────────────────────────────────────
# DB helper: unaccent Func
# ──────────────────────────────────────────────
class Unaccent(Func):
    function = "unaccent"
    output_field = models.TextField()


# ──────────────────────────────────────────────
# Async Worker ABC
# ──────────────────────────────────────────────
class AsyncWorkerABC(ABC):
    MAX_RETRIES = 10
    RETRY_DELAY = 10
    TRIGRAM_THRESHOLD = 0.2

    verbose = False
    debug = False

    # ──────────────────────────────────────────────
    # Pickle safety
    # ──────────────────────────────────────────────
    def __getstate__(self):
        state = self.__dict__.copy()
        for k in (
                "client",
                "http_sem",
                "_shutdown_event",
                "_task",
                "process",
                "logger",
                "metrics_logger",

        ):
            state.pop(k, None)
        if not self.run_in_process:
            state.pop("control_queue", None)
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self.client = None
        self.http_sem = None
        self._shutdown_event = None
        self._task = None
        self.process = None

    # ──────────────────────────────────────────────
    # Init
    # ──────────────────────────────────────────────
    def __init__(
        self,
        vhost=None,
        logger=None,
        name="worker",
        interval=10,
        run_in_process=True,
        loki_url=None,
    ):
        self.name = name
        self.vhost = vhost
        self._vhost_uuid = getattr(vhost, "uuid", vhost)
        self.interval = interval
        self.run_in_process = run_in_process
        self.loki_url = loki_url



        self._running = False
        self._exit = False
        self._task = None
        self._shutdown_event = None
        self.process = None
        self.pid = None

        self.max_workers = max(50, os.cpu_count() or 1)

        self.logger = logging.getLogger(f"{name}.thread")
        self.logger.setLevel(logging.INFO)

        self.metrics_logger = logging.getLogger(f"{name}.metrics")
        self.metrics_logger.setLevel(logging.INFO)

        self.httpx_limits = httpx.Limits(
            max_connections=40,
            max_keepalive_connections=20,
        )
        self.httpx_timeout = httpx.Timeout(
            connect=10,
            read=30,
            write=10,
            pool=30,
        )
        self.client = httpx.AsyncClient(
            limits=self.httpx_limits,
            timeout=self.httpx_timeout,
        )
        self.http_sem = asyncio.Semaphore(25)

    # ──────────────────────────────────────────────
    # Child bootstrap
    # ──────────────────────────────────────────────
    def _bind_models(self):
        from dataengine.models import (
            GroupSyncStatus,
            SportSyncStatus,
            SeasonSyncStatus,
            TeamSyncStatus,
            MatchSyncStatus,
            SegmentSyncStatus,
            OddsSyncStatus,
            OutcomeTeamsSyncStatus,
        )
        from outcomes.models import Outcome, OutcomeTeams, OutcomeSegmentScore

        self.GroupSyncStatus = GroupSyncStatus
        self.SportSyncStatus = SportSyncStatus
        self.SeasonSyncStatus = SeasonSyncStatus
        self.TeamSyncStatus = TeamSyncStatus
        self.MatchSyncStatus = MatchSyncStatus
        self.SegmentSyncStatus = SegmentSyncStatus
        self.OddsSyncStatus = OddsSyncStatus
        self.OutcomeTeamsSyncStatus = OutcomeTeamsSyncStatus

        self.Outcome = Outcome
        self.OutcomeTeams = OutcomeTeams
        self.OutcomeSegmentScore = OutcomeSegmentScore

        self.SYNC_TYPE_TABLE = {
            "group": GroupSyncStatus,
            "sport": SportSyncStatus,
            "season": SeasonSyncStatus,
            "team": TeamSyncStatus,
            "match": MatchSyncStatus,
            "segment": SegmentSyncStatus,
            "odds": OddsSyncStatus,
            "outcome_teams_sync": OutcomeTeamsSyncStatus,

        }

    def _child_init(self):
        from parameters.models import VHost

        if self._vhost_uuid and self.vhost is None:
            self.vhost = VHost.objects.get(uuid=self._vhost_uuid)
        self._shutdown_event = asyncio.Event()
        self.http_sem = asyncio.Semaphore(25)

        self.httpx_limits = httpx.Limits(max_connections=40, max_keepalive_connections=20)
        self.httpx_timeout = httpx.Timeout(connect=10, read=30, write=10, pool=30)
        self.client = httpx.AsyncClient(
            limits=self.httpx_limits,
            timeout=self.httpx_timeout,
        )

        self._bind_models()

        self.logger = logging.getLogger(self.name)
        self.metrics_logger = logging.getLogger(f"{self.name}.metrics")

        if self.debug:
            self.logger.debug("Child process initialized")

    # ──────────────────────────────────────────────
    # Loki logging
    # ──────────────────────────────────────────────
    async def loki_logger_start(self):
        handler = AsyncLokiHandler(
            self.loki_url,
            labels={
                "pid": self.pid,
                "worker": self.__class__.__name__,
                "vhost": str(self.vhost.uuid),
                "service": self.__class__.__name__,
            },
        )
        handler.setLevel(logging.INFO)
        await handler.start()

        self.logger.setLevel(logging.INFO)
        self.logger.propagate = False
        self.logger.addHandler(handler)

        metrics_handler = AsyncLokiHandler(
            self.loki_url,
            labels={
                "pid": self.pid,
                "worker": self.__class__.__name__,
                "vhost": str(self.vhost.uuid),
                "service": self.__class__.__name__,
                "metrics": True,
            },
        )
        metrics_handler.setLevel(logging.INFO)
        await metrics_handler.start()

        self.metrics_logger.setLevel(logging.INFO)
        self.metrics_logger.propagate = False
        self.metrics_logger.addHandler(metrics_handler)


    # ──────────────────────────────────────────────
    # Lifecycle
    # ──────────────────────────────────────────────

    async def _fetch_with_retry(self, turl,**kwargs):
        async with self.http_sem:
            for attempt in range(1, self.MAX_RETRIES + 1):
                try:
                    if "params" in kwargs:
                        response = await self.client.get(turl,params=kwargs["params"])
                    else:
                        response = await self.client.get(turl)
                    response.raise_for_status()
                    return response
                except httpx.HTTPStatusError as e:
                    if e.response.status_code == 404:
                        return None
                    if e.response.status_code == 401:
                        if hasattr(self,"_reset_auth"):
                            await self._reset_auth()
                        # return False
                    if "params" in kwargs:
                        self.logger.warning(f"[Retry] HTTP Status Error on {turl}, attempt {attempt}/{self.MAX_RETRIES} With Params {kwargs['params']}: {e}")
                    else:
                        self.logger.warning(f"[Retry] HTTP Status Error on {turl}, attempt {attempt}/{self.MAX_RETRIES}: {e}")
                    if attempt < self.MAX_RETRIES:
                        await asyncio.sleep(self.RETRY_DELAY)
                    else:
                        self.logger.info(f"[Error] Max retries exceeded for {turl}")
                        return None
                except httpx.ReadTimeout:
                    if "params" in kwargs:
                        self.logger.warning(f"[Retry] ReadTimeout on {turl}, attempt {attempt}/{self.MAX_RETRIES} With Params {kwargs['params']}")
                    else:
                        self.logger.warning(f"[Retry] ReadTimeout on {turl}, attempt {attempt}/{self.MAX_RETRIES}")
                    if attempt < self.MAX_RETRIES:
                        await asyncio.sleep(self.RETRY_DELAY)
                    else:
                        self.logger.info(f"[Error] Max retries exceeded for {turl}")
                        return None

                except httpx.RequestError as e:
                    # Optional: catch other network errors too
                    self.logger.error(f"[Error] Request failed for {turl}: {e}")
                    print(e)
                    return None

    async def run_in_batches(self, items, handler, batch_size=50, label="task"):
        """
        Runs `handler(item)` for items in batches, with bounded concurrency and:
          - per-batch timing & progress logs
          - per-item progress logs inside a batch
          - collects per-batch exceptions & tracebacks for summary
          - FAIL-FAST: any exception bubbles out and aborts remaining batches
        """
        # prefer explicit MAX_WORKERS if set, otherwise fallback to lower-case attribute (from base)
        concurrency = getattr(self, "MAX_WORKERS", getattr(self, "max_workers", 10))
        sem = asyncio.Semaphore(concurrency)

        total = len(items)
        if total == 0:
            self.logger.info(f"[{label}] No items to process.")
            return
        else:
            self.logger.info(f"[{label}] {total} items to process.")
        # bookkeeping for summary
        batch_timings = []  # list of (batch_num, elapsed_seconds)
        batch_exceptions = []  # list of (batch_num, exception, traceback_str)
        items_processed = 0

        try:
            for i in range(0, total, batch_size):
                batch = items[i: i + batch_size]
                batch_num = i // batch_size + 1
                batch_count = len(batch)
                if self.verbose:
                    self.logger.info(
                        f"[{label}] Batch {batch_num}: {batch_count} items "
                        f"({min(i + batch_count, total)}/{total}) — concurrency={concurrency}"
                    )

                batch_start = time.perf_counter()

                # per-item wrapper executes handler with semaphore, retrying via retry_wrapper
                async def sem_task(idx_in_batch, item):
                    async with sem:
                        # log per-item start
                        if self.verbose:
                            self.logger.debug(f"[{label}] Batch {batch_num} Item {idx_in_batch}/{batch_count} starting")
                        # call retry_wrapper which will raise on final failure
                        result = await self.retry_wrapper(handler, item, retries=3, label=label)
                        # log per-item completion
                        if self.verbose:
                            self.logger.debug(f"[{label}] Batch {batch_num} Item {idx_in_batch}/{batch_count} done")
                        return result

                # create tasks for batch
                tasks = [asyncio.create_task(sem_task(idx + 1, item)) for idx, item in enumerate(batch)]

                # Await batch tasks WITHOUT return_exceptions (fail-fast behavior)
                # Any exception in a task will be propagated out of gather and into the outer try/except.
                await asyncio.gather(*tasks)

                batch_elapsed = time.perf_counter() - batch_start
                batch_timings.append((batch_num, batch_elapsed))
                items_processed += batch_count

                # log batch-level progress
                avg_per_item = batch_elapsed / batch_count if batch_count else 0
                if self.verbose:
                    self.logger.info(
                        f"[{label}] Batch {batch_num} completed: {batch_count} items in {batch_elapsed:.2f}s "
                        f"(avg {avg_per_item:.3f}s/item). Progress: {items_processed}/{total}"
                    )

        except Exception as exc:
            # Collect traceback for summary and re-raise to bubble up
            tb = traceback.format_exc()
            # Determine failing batch number if possible (best-effort)
            failing_batch = None
            # If tasks exist in local scope, try to find which one failed (best-effort, don't break on errors)
            try:
                # find last batch number from batch_timings if present, else compute from items_processed
                failing_batch = (items_processed // batch_size) + 1 if items_processed is not None else None
            except Exception:
                failing_batch = None

            batch_exceptions.append((failing_batch, exc, tb))
            # log the immediate error (detailed)
            self.logger.error(f"[{label}] Batch {failing_batch or 'unknown'} failed: {exc}", exc_info=True)
            # re-raise so caller (work cycle) sees the full traceback
            raise

        finally:
            # Summary logging: timings and exceptions
            try:
                total_time = sum(t for _, t in batch_timings)
                avg_batch = (total_time / len(batch_timings)) if batch_timings else 0

                self.logger.info(f"[{label}] Run summary: {len(batch_timings)} batches completed, "
                                 f"total time {total_time:.2f}s, avg {avg_batch:.2f}s/batch, "
                                 f"items processed {items_processed}/{total}")
                if self.loki_url:
                    self.metrics_logger.info(json.dumps({
                        "type": "batch_statistics",
                        "batches_completed": len(batch_timings),
                        "total_time": total_time,
                        "avg_batch": avg_batch,
                        "items_processed": items_processed,
                        "total_items": total
                    }))
                if self.verbose:
                    for bnum, tsec in batch_timings:
                        self.logger.info(f"[{label}]   - Batch {bnum}: {tsec:.2f}s")

                if batch_exceptions:
                    self.logger.error(f"[{label}] {len(batch_exceptions)} batch exception(s) encountered:")
                    for bnum, exc, tb in batch_exceptions:
                        self.logger.error(f"[{label}]   - Batch {bnum or 'unknown'} exception: {exc}\n{tb}")
                else:
                    self.logger.info(f"[{label}] No batch exceptions.")
            except Exception:
                # Ensure summary itself never masks original exception
                self.logger.exception(f"[{label}] Error while writing summary", exc_info=True)

        # Finished successfully (no exception raised)
        return

    async def start(self):
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self._run())
        await self._shutdown_event.wait()

    @staticmethod
    def _process_bootstrap(worker_cls, vhost_uuid, name, interval, loki_url, parent_queue=None):
        import os, sys, django, asyncio, logging

        # Setup Django inside child
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "athena.settings")
        django.setup()

        # Create the worker instance inside child
        worker = worker_cls(
            vhost=vhost_uuid,
            name=name,
            interval=interval,
            run_in_process=False,  # we are already in child
            loki_url=loki_url,
            control_queue=None  # we'll handle this below
        )
        worker.pid = os.getpid()

        # Logging setup
        root = logging.getLogger()
        root.handlers.clear()
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter("[%(asctime)s] [%(levelname)s] %(name)s: %(message)s"))
        root.addHandler(handler)
        root.setLevel(logging.INFO)

        worker.logger = logging.getLogger(worker.name)
        worker.logger.propagate = True

        from parameters.models import VHost
        worker.vhost = VHost.objects.get(uuid=vhost_uuid)
        # Control queue
        if parent_queue:
            from multiprocessing import get_context
            ctx = get_context()
            worker.control_queue = ctx.Queue()
        else:
            worker.control_queue = None

        # Initialize child-specific stuff
        worker._child_init()
        worker._running = True
        # Run the async loop
        asyncio.run(worker._run())


    async def stop(self):
        self._exit = True
        self._running = False
        self._shutdown_event.set()

        if self.process and self.process.is_alive():
            self.process.terminate()
            self.process.join()

    # ──────────────────────────────────────────────
    # Core loop
    # ──────────────────────────────────────────────
    async def _run(self):
        if self.loki_url:
            await self.loki_logger_start()

        last_metrics = 0
        METRICS_INTERVAL = 10  # seconds

        try:
            while self._running and not self._exit:
                try:
                    await self._work_cycle()
                except asyncio.CancelledError:
                    raise
                except Exception as e:
                    self.logger.error(
                        f"🔥 Exception in _work_cycle — continuing loop",
                        exc_info=True,
                    )
                    self.logger.error(e)
                    traceback.print_exc()
                # ---- LOCAL METRICS POLL ----
                now_ts = time.monotonic()
                if self.loki_url and (now_ts - last_metrics) >= METRICS_INTERVAL:
                    asyncio.create_task(
                        sync_to_async(self.emit_metrics, thread_sensitive=False)()
                    )
                    last_metrics = now_ts

                # await sync_to_async(lambda:close_old_connections(),thread_sensitive=False)()
                await asyncio.sleep(self.interval)

        except Exception:
            self.logger.exception("Worker crashed")
        finally:
            await self._cleanup()

    @abstractmethod
    async def _work_cycle(self):
        ...

    async def _cleanup(self):
        self.logger.info(f"{self.name} cleanup complete")

    async def _object_setattrs(self, obj, entry, **kwargs):
        # Normalize entry → dict
        if isinstance(entry, dict):
            data = entry
        else:
            data = vars(entry)

        rows = set(kwargs.get("rows", []))

        # Concrete model fields (attname → field)
        field_map = {
            f.attname: f
            for f in obj._meta.concrete_fields
        }

        # Map field.name → field (needed for FK detection)
        name_map = {
            f.name: f
            for f in obj._meta.concrete_fields
        }

        for key, value in data.items():
            target_key = key

            # ─────────────────────────────
            # 🔥 FK payload handling
            # ─────────────────────────────
            if isinstance(value, dict) and "value" in value:
                field = name_map.get(key)

                if isinstance(field, ForeignKey):
                    # FK must be assigned via <field>_id
                    target_key = field.attname
                    value = value["value"]
                else:
                    # Non-FK structured payload
                    value = value["value"]

            if target_key not in field_map:
                continue
            if rows and target_key not in rows:
                continue

            field = field_map[target_key]

            # ─────────────────────────────
            # FileField / ImageField handling
            # ─────────────────────────────
            if isinstance(field, (FileField, ImageField)):
                if not value:
                    continue

                if isinstance(value, dict) and value.get("error"):
                    continue

                if isinstance(value, dict) and value.get("encoding") == "base64":
                    raw = base64.b64decode(value["data"])
                    filename = value["name"].split("/")[-1]

                    content = ContentFile(raw, name=filename)
                    getattr(obj, target_key).save(
                        filename,
                        content,
                        save=False,
                    )

                continue

            # ─────────────────────────────
            # Normal field assignment
            # ─────────────────────────────
            setattr(obj, target_key, value)

        # Persist once
        await sync_to_async(obj.save, thread_sensitive=False)()

    # ──────────────────────────────────────────────
    # Single-object find/create
    # ──────────────────────────────────────────────

    async def find_sync_object(self, sync_type, object_type, object_uuid, system_obj=False):
        model_cls = self.SYNC_TYPE_TABLE[sync_type]
        related_field = SYNC_RELATED_FIELD_MAP[sync_type]

        def query():
            qs = model_cls.objects.using("default").filter(
                driver_object_type=object_type
            )
            if system_obj:
                qs = qs.filter(**{related_field: system_obj})
            else:
                qs = model_cls.objects.using("default").filter(
                    driver_object_uuid=object_uuid,
                )
            objs = list(qs)
            return objs

        objs = await sync_to_async(query, thread_sensitive=False)()
        return objs[0] if objs else None

    async def create_sync_object(self, sync_type, system_object, driver_object_type, driver_object_uuid):
        model_cls = self.SYNC_TYPE_TABLE[sync_type]
        related_field = SYNC_RELATED_FIELD_MAP[sync_type]

        qkwargs = {
            related_field: system_object,
            "driver_object_uuid": driver_object_uuid,
            "driver_object_type": driver_object_type,
            "system_object_type": system_object._meta.model_name,
            "system_object_uuid": getattr(system_object, "uuid", None),
        }

        def create_or_get():
            obj, _ = model_cls.objects.using("default").get_or_create(**qkwargs)
            return obj

        return await sync_to_async(create_or_get, thread_sensitive=False)()

    async def find_sync_objects(self, sync_type, object_type, object_uuid, system_obj=False):
        model_cls = self.SYNC_TYPE_TABLE[sync_type]
        related_field = SYNC_RELATED_FIELD_MAP[sync_type]

        def query():
            qs = model_cls.objects.filter(
                driver_object_type=object_type
            )
            if system_obj:
                qs = qs.filter(**{related_field: system_obj})
            else:
                qs = model_cls.objects.using("default").filter(
                    driver_object_uuid=object_uuid,
                )
            objs = list(qs)
            return objs

        objs = await sync_to_async(query, thread_sensitive=False)()
        return objs

    async def _create_outcome(self, fixture, driver):
        # await sync_to_async(lambda:outcomes.save(),thread_sensitive=True)()
        try:
                outcomeObj, cc = await sync_to_async(lambda: self.Outcome.objects.using("default").get_or_create(vhost=self.vhost, match=fixture,
                                                                                           driver=driver),thread_sensitive=False)()
                if cc:
                    await sync_to_async(lambda: outcomeObj.save, thread_sensitive=False)()
        except self.Outcome.MultipleObjectsReturned:
            outcomeObj = await sync_to_async(
                lambda: self.Outcome.objects.using("default").filter(vhost=self.vhost, match=fixture,
                                               driver=driver).first(),
                thread_sensitive=False)()

        return outcomeObj

    async def _create_outcome_team(self, outcomeObj, teamObj, driver):
        try:
            outcomeObj, cc = await sync_to_async(
                lambda: self.OutcomeTeams.objects.using("default").get_or_create(vhost=self.vhost, outcome=outcomeObj,
                                                           team=teamObj, driver=driver), thread_sensitive=False)()
            if cc:
                await sync_to_async(lambda: outcomeObj.save, thread_sensitive=False)()
        except self.OutcomeTeams.MultipleObjectsReturned:
            outcomeObj = await sync_to_async(
                lambda: self.OutcomeTeams.objects.using("default").filter(vhost=self.vhost, outcome=outcomeObj,
                                                    team=teamObj, driver=driver).first(), thread_sensitive=False)()
        return outcomeObj

    async def _create_outcome_segment(self, outcomeObj, teamObj, segment, driver):
        try:
            outcomeObj, cc = await sync_to_async(
                lambda: self.OutcomeSegmentScore.objects.using("default").get_or_create(vhost=self.vhost, outcome=outcomeObj, segment=segment,
                                                                  team=teamObj, driver=driver),
                thread_sensitive=False)()
            if cc:
                await sync_to_async(lambda: outcomeObj.save, thread_sensitive=False)()
        except self.OutcomeSegmentScore.MultipleObjectsReturned:
            outcomeObj = await sync_to_async(
                lambda: self.OutcomeSegmentScore.objects.using("default").filter(vhost=self.vhost, outcome=outcomeObj, segment=segment,
                                                           team=teamObj, driver=driver).first(),
                thread_sensitive=False)()
        return outcomeObj
    # ──────────────────────────────────────────────
    # BULK-OPTIMIZED OPERATIONS
    # ──────────────────────────────────────────────

    async def bulk_find_sync_objects(self, sync_type, driver_object_type, object_uuids, system_obj=None):
        """
        Fetches all sync objects of a given type in one DB query.
        Returns {uuid: sync_obj}.
        """
        if not object_uuids:
            return {}

        model_cls = self.SYNC_TYPE_TABLE[sync_type]
        related_field = SYNC_RELATED_FIELD_MAP[sync_type]

        def query():
            qs = model_cls.objects.using("default").filter(
                driver_object_type=driver_object_type,
                driver_object_uuid__in=object_uuids,
            )
            if system_obj:
                qs = qs.filter(**{related_field: system_obj})
            return {obj.driver_object_uuid: obj for obj in qs}

        return await sync_to_async(query, thread_sensitive=False)()

    async def ensure_sync_batch(self, sync_type, records):
        """
        Ensures a batch of sync mappings exist.
        Each record = (system_object, driver_object_type, driver_object_uuid)
        Creates only missing ones, in bulk.
        Returns {uuid: sync_object}.
        """
        if not records:
            return {}

        model_cls = self.SYNC_TYPE_TABLE[sync_type]
        related_field = SYNC_RELATED_FIELD_MAP[sync_type]

        existing = await self.bulk_find_sync_objects(
            sync_type,
            driver_object_type=records[0][1],
            object_uuids=[r[2] for r in records],
        )

        missing = [
            {
                related_field: sys_obj,
                "driver_object_type": drv_type,
                "driver_object_uuid": drv_uuid,
                "system_object_type": sys_obj._meta.model_name,
                "system_object_uuid": getattr(sys_obj, "uuid", None),
            }
            for sys_obj, drv_type, drv_uuid in records
            if drv_uuid not in existing
        ]

        if not missing:
            return existing

        def bulk_create():
            objs = [model_cls(**data) for data in missing]
            created = model_cls.objects.bulk_create(objs, ignore_conflicts=True)
            out = {o.driver_object_uuid: o for o in created}
            out.update(existing)
            return out

        return await sync_to_async(bulk_create, thread_sensitive=False)()

    async def retry_wrapper(self, func, item, retries=3, label="task"):
        """
        Retries the provided coroutine `func(item)` up to `retries` times with exponential backoff.
        On the final failed attempt the exception is raised (not returned).
        """
        delay = 0.25
        for attempt in range(1, retries + 1):
            try:
                return await func(item)
            except Exception as e:
                # log full exception context for debugging
                self.logger.error(f"[{label}] error on attempt {attempt}/{retries}: {e}", exc_info=True)
                if attempt == retries:
                    # final attempt -> raise so caller sees the real error (fail-fast)
                    raise
                await asyncio.sleep(delay)
                delay *= 2

    def emit_metrics(self):
        """
        Emit a metrics frame from inside the worker process.
        Safe: no IPC, no asyncio crossing, no multiprocessing primitives.
        """
        if not self.loki_url:
            return

        try:
            proc = psutil.Process(os.getpid())
            t = proc.cpu_times()

            self.metrics_logger.info(json.dumps({
                "type": "worker_metrics",
                "pid": proc.pid,
                "cpu_time_sec": t.user + t.system,
                "memory_mb": proc.memory_info().rss / 1024 ** 2,
                "open_files": len(proc.open_files()),
            }))
        except Exception:
            self.logger.exception("Failed to emit metrics")