import asyncio
from asyncio import Queue as AsyncQueue
from types import SimpleNamespace

from django.utils.timezone import make_aware, is_naive, localtime
import datetime
import json
import logging
import os
from asyncio import Queue
from math import ceil
from typing import Optional

import psutil
from asgiref.sync import sync_to_async
from django.db.models.fields import Field, DateField, DateTimeField
from django.utils.dateparse import parse_datetime, parse_date
from django.utils.timezone import now, is_naive
from fastapi import FastAPI, Request, HTTPException
from uvicorn import Config, Server

from asynctools.loki import AsyncLokiHandler

from minerve.toolkit.serialisers import filtered_serialiser_many



class DataPublisherHTTPDaemon:
    def __init__(
        self,
        vhost: object,
        listen_host: str = "0.0.0.0",
        listen_port: int = 22000,
        loki_url: Optional[str] = None,
        logger: Optional[logging.Logger] = None,
        page_size: int = 100,
        verbose=True,
        run_in_process=False,
    ):

        self.vhost = vhost
        self.listen_host = listen_host
        self.listen_port = listen_port
        self.loki_url = loki_url

        self.logger = logger or logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.INFO)
        self.pid = os.getpid()
        self.metrics_logger = logging.getLogger("PublisherHTTPd.metrics")
        self.metrics_logger.setLevel(logging.INFO)
        self.PAGE_SIZE = page_size
        self.app = FastAPI(title="PublisherHTTPD")


        self.run_in_process = run_in_process
        self.verbose = verbose
        self._child_init()


    def _child_init(self):
        """
        Runs inside the forked child *after* django.setup().
        Safe place for model imports.
        """
        from dataengine.models import DataEngineAPIKey
        from matches.models import Match
        from odds.models import MatchOddsSummary
        from outcomes.models import Outcome, OutcomeTeams, OutcomeFinalMatchScores
        from parameters.models import VHost
        from sports.models import Group, Sport, Country, Season
        from teams.models import Team, TeamSport
        from parameters.models import Timezone, VHostParameterRegistry
        self.last_timestamp = localtime()
        self.models = SimpleNamespace(
            DataEngineAPIKey=DataEngineAPIKey,
            Match=Match,
            MatchOddsSummary=MatchOddsSummary,
            Outcome=Outcome,
            OutcomeTeams=OutcomeTeams,
            OutcomeFinalMatchScores=OutcomeFinalMatchScores,
            VHost=VHost,
            Group=Group,
            Sport=Sport,
            Country=Country,
            Season=Season,
            Team=Team,
            TeamSport=TeamSport,
            Timezone=Timezone,
            VHostParameterRegistry=VHostParameterRegistry
        )
        self._setup_routes()
    # ------------------------------------------------------------------
    # Logging
    # ------------------------------------------------------------------

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

    # ------------------------------------------------------------------
    # API Key validation
    # ------------------------------------------------------------------

    def _validate_apikey(self, apikey: Optional[str]):
        if not apikey:
            raise HTTPException(status_code=403, detail="No API key provided")

        try:
            return  self.models.DataEngineAPIKey.objects.get(
                vhost=self.vhost,
                apikey=apikey,
            )
        except self.models.DataEngineAPIKey.DoesNotExist:
            raise HTTPException(status_code=403, detail="API key is invalid")

    # ------------------------------------------------------------------
    # Generic queryset builder
    # ------------------------------------------------------------------

    def _build_queryset(self, model, params: dict, allowed_filters=None):
        qs = model.objects.filter(vhost=self.vhost)

        if not allowed_filters:
            return qs

        model_fields = {
            field.name: field
            for field in model._meta.get_fields()
            if hasattr(field, "name")
        }

        filters = {}

        for key in allowed_filters:
            if key not in params:
                continue

            field = model_fields.get(key)
            if not field:
                continue

            raw_value = params[key]

            # --------------------------------------------
            # Date / DateTime handling
            # --------------------------------------------
            if isinstance(field, DateTimeField):
                dt = parse_datetime(raw_value) or parse_date(raw_value)
                if dt is None:
                    continue

                if isinstance(dt, DateField):
                    # date → datetime at midnight
                    dt = datetime.datetime.combine(dt, datetime.time.min)

                if is_naive(dt):
                    dt = make_aware(dt)

                filters[f"{key}__gte"] = dt

            elif isinstance(field, DateField):
                d = parse_date(raw_value)
                if d is None:
                    continue
                filters[f"{key}__gte"] = d

            else:
                filters[key] = raw_value

        if filters:
            qs = qs.filter(**filters)
        if self.verbose:
            self.logger.debug("Applied filters: %s", filters)
        return qs

    # ------------------------------------------------------------------
    # Generic GET endpoint factory
    # ------------------------------------------------------------------

    def _make_get_endpoint(self, *, model, allowed_filters=None):

        async def endpoint(
                request: Request,
                apikey: Optional[str] = None,
        ):
            # --------------------------------------------------------------
            # API key validation
            # --------------------------------------------------------------
            await sync_to_async(
                self._validate_apikey,
                thread_sensitive=False
            )(apikey)

            params = dict(request.query_params)
            snapshot_raw = params.get("snapshot_ts")
            if snapshot_raw:
                snapshot_ts = parse_datetime(snapshot_raw) or parse_date(snapshot_raw)
                if snapshot_ts is None:
                    raise HTTPException(status_code=400, detail="Invalid snapshot_ts")
                if isinstance(snapshot_ts, DateField):
                    snapshot_ts = datetime.datetime.combine(snapshot_ts, datetime.time.max)
                if is_naive(snapshot_ts):
                    snapshot_ts = make_aware(snapshot_ts)
            else:
                snapshot_ts = now()
                self.metrics_logger.info(
                    "snapshot_started",
                    extra={"snapshot_ts": snapshot_ts.isoformat(), "model": model.__name__}
                )

            # --------------------------------------------------------------
            # Pagination
            # --------------------------------------------------------------
            try:
                current_page = int(params.get("page", 1))
                if current_page < 1:
                    current_page = 1
            except ValueError:
                current_page = 1

            page_size = self.PAGE_SIZE
            offset = (current_page - 1) * page_size
            limit = offset + page_size

            # --------------------------------------------------------------
            # Build base queryset
            # --------------------------------------------------------------
            queryset = await sync_to_async(lambda:self._build_queryset(
                model=model,
                params=params,
                allowed_filters=allowed_filters,
            ),thread_sensitive=False)()

            # --------------------------------------------------------------
            # 🔒 CRITICAL: deterministic ordering
            # --------------------------------------------------------------
            if hasattr(model, "updated_at"):
                queryset = queryset.order_by("updated_at", "pk")
            elif hasattr(model, "updated"):
                queryset = queryset.order_by("updated", "pk")
            else:
                queryset = queryset.order_by("pk")
            # --------------------------------------------------------------
            # 🔒 Snapshot freeze (CRITICAL)
            # --------------------------------------------------------------
            if hasattr(model, "updated_at"):
                queryset = queryset.filter(updated_at__lte=snapshot_ts)
            elif hasattr(model, "updated"):
                queryset = queryset.filter(updated__lte=snapshot_ts)
            # --------------------------------------------------------------
            # Count BEFORE slicing
            # --------------------------------------------------------------
            total_count = await sync_to_async(
                queryset.count,
                thread_sensitive=False
            )()

            max_pages = ceil(total_count / page_size) if total_count else 1

            # --------------------------------------------------------------
            # Apply pagination
            # --------------------------------------------------------------
            paged_queryset = queryset[offset:limit]

            # --------------------------------------------------------------
            # Field introspection
            # --------------------------------------------------------------
            def get_model_fields():
                fields = {}
                for field in model._meta.get_fields():
                    if field.auto_created and not field.concrete:
                        continue
                    if field.name == "vhost":
                        continue
                    fields[field.name] = True
                return fields

            field_dict = await sync_to_async(
                get_model_fields,
                thread_sensitive=False
            )()

            # --------------------------------------------------------------
            # Serialise
            # --------------------------------------------------------------
            rows, _, _ = await sync_to_async(
                filtered_serialiser_many,
                thread_sensitive=False,
            )(
                paged_queryset,
                fields=field_dict,
                include_files=True,
                render_false_as_dash=False,
                date_isoformat=True,
            )

            # --------------------------------------------------------------
            # Response
            # --------------------------------------------------------------
            return {
                "success": True,
                "request_date": now().isoformat(),
                "current_page": current_page,
                "max_pages": max_pages,
                "page_size": page_size,
                "total_count": total_count,
                "data": rows,
                "snapshot_ts": snapshot_ts.isoformat(),
            }


        return endpoint

    # ------------------------------------------------------------------
    # Route setup
    # ------------------------------------------------------------------

    def _setup_routes(self):

        # /v1/get/country
        self.app.get("/api/v1/get/country")(
            self._make_get_endpoint(
                model=self.models.Country,
                allowed_filters=["uuid"],
            )
        )
        # /v1/get/groups
        self.app.get("/api/v1/get/groups")(
            self._make_get_endpoint(
                model=self.models.Group,
                allowed_filters=["uuid"],
            )
        )
        # /v1/get/sports
        self.app.get("/api/v1/get/sports")(
            self._make_get_endpoint(
                model=self.models.Sport,
                allowed_filters=["uuid"],
            )
        )
        # /v1/get/seasons
        self.app.get("/api/v1/get/seasons")(
            self._make_get_endpoint(
                model=self.models.Season,
                allowed_filters=["uuid"],
            )
        )
        # /v1/get/teams
        self.app.get("/api/v1/get/teams")(
            self._make_get_endpoint(
                model=self.models.Team,
                allowed_filters=["uuid"],
            )
        )

        # /v1/get/teamsports
        self.app.get("/api/v1/get/team/sports")(
            self._make_get_endpoint(
                model=self.models.TeamSport,
                allowed_filters=["uuid","team"],
            )
        )

        # /v1/get/matches
        self.app.get("/api/v1/get/matches")(
            self._make_get_endpoint(
                model=self.models.Match,
                allowed_filters=["uuid", "sport","updated"],
            )
        )

        # /v1/get/outcomes
        self.app.get("/api/v1/get/outcomes")(
            self._make_get_endpoint(
                model=self.models.Outcome,
                allowed_filters=["uuid", "match","updated_on"],
            )
        )

        # /v1/get/outcome/teams
        self.app.get("/api/v1/get/outcomes/teams")(
            self._make_get_endpoint(
                model=self.models.OutcomeTeams,
                allowed_filters=["uuid", "match","updated_at"],
            )
        )

        # /v1/get/outcomes/final
        self.app.get("/api/v1/get/outcomes/final")(
            self._make_get_endpoint(
                model=self.models.OutcomeFinalMatchScores,
                allowed_filters=["uuid", "match","updated_at"],
            )
        )

        # /v1/get/match/odds/summary
        self.app.get("/api/v1/get/match/odds/summary")(
            self._make_get_endpoint(
                model=self.models.MatchOddsSummary,
                allowed_filters=["uuid", "match","updated_at","last_update"],
            )
        )
    # ------------------------------------------------------------------
    # Server start
    # ------------------------------------------------------------------

    async def start(self):
        if self.loki_url:
            await self.loki_logger_start()
        # asyncio.create_task(self._control_listener())
        self.logger.info(
            f"Starting DataEngine PublisherHTTPd on "
            f"{self.listen_host}:{self.listen_port}..."
        )

        config = Config(
            app=self.app,
            host=self.listen_host,
            port=self.listen_port,
            log_level="info",
            loop="asyncio",
        )
        server = Server(config)
        await server.serve()

