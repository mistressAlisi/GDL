import asyncio
from datetime import timedelta
from types import SimpleNamespace
from typing import Optional

from asgiref.sync import sync_to_async
from django.conf import settings
from django.db import IntegrityError
from django.utils.timezone import now

from asynctools.abc import AsyncWorkerABC
from dataengine.consumer.modelclient import DataEngineModelClient



class DataEngineConsumerHTTPd(AsyncWorkerABC):

    def __init__(
        self,
        vhost=object,
        logger=object,
        name="DataEngineConsumerD",
        interval=60,
        run_in_process=False,
        loki_url=None,
        api_key=None,
        remote_host_url=None,
        verbose=True,
    ):
        self.verbose = verbose

        if api_key:
            self.api_key = api_key
        else:
            self.api_key = settings.DATAENGINE_HTTPD_APIKEY

        if remote_host_url:
            self.remote_host_url = remote_host_url.rstrip("/")
        else:
            self.remote_host_url = settings.DATAENGINE_HTTPD_URL.rstrip("/")

        super().__init__(
            vhost=vhost,
            logger=logger,
            name=name or self.name,
            interval=interval,
            run_in_process=run_in_process,
            loki_url=loki_url,
        )

        # For normal workloop:

        # model_name -> DataEngineModelClient
        self._model_clients = {}

        # model_name -> coroutine handler
        self._model_handlers = {}

        # For hourly workloop:

        # model_name -> DataEngineModelClient
        self._hourly_model_clients = {}

        # model_name -> coroutine handler
        self._hourly_model_handlers = {}

        # Now set the timestamp
        self.last_timestamp = now() - timedelta(days=2)
        self._child_init()

    def _child_init(self):
        """
        Runs inside the forked child *after* django.setup().
        Safe place for model imports.
        """
        super()._child_init()
        from matches.models import Match
        from odds.models import MatchOddsSummary
        from outcomes.models import Outcome, OutcomeTeams, OutcomeFinalMatchScores
        from sports.models import Group, Sport, Country, Season
        from teams.models import Team, TeamSport

        self.models = SimpleNamespace(
            Match=Match,
            MatchOddsSummary=MatchOddsSummary,
            Outcome=Outcome,
            OutcomeTeams=OutcomeTeams,
            OutcomeFinalMatchScores=OutcomeFinalMatchScores,
            Group=Group,
            Sport=Sport,
            Country=Country,
            Season=Season,
            Team=Team,
            TeamSport=TeamSport,
        )
        self._hourly_task = False
        self._first_run = True
    # --------------------------------------------------
    # Register model client
    # --------------------------------------------------
    def register_model(
        self,
        *,
        name: str,
        endpoint: str,
        update_field_name: Optional[str] = None,
        handler=None,
        hourly=False
    ):
        client = DataEngineModelClient(
            parent=self,
            name=name,
            update_field_name=update_field_name,
            endpoint=endpoint,
        )
        if not hourly:
            self._model_clients[name] = client
            if handler:
                self._model_handlers[name] = handler
        else:
            self._hourly_model_clients[name] = client
            if handler:
                self._hourly_model_handlers[name] = handler
        return client

    # --------------------------------------------------
    # Generic sync implementation
    # --------------------------------------------------
    async def sync_objects(
            self,
            *,
            client,
            model,
            task_name,
            batch_size=50,
    ):
        batch = []

        async def handle_object(data):
            # print(data)
            duuid = data["uuid"]
            modelObj, _ = await sync_to_async(
                model.objects.get_or_create,
                thread_sensitive=False,
            )(
                uuid=duuid,
                vhost=self.vhost,
            )

            # Never overwrite identity fields
            data.pop("uuid", None)
            data.pop("__pk", None)
            data.pop("vhost", None)
            try:
                await self._object_setattrs(modelObj, data)
            except IntegrityError as e:
                self.logger.info(f"For the object {duuid} - the following Exception occurred: {e}")
            return True

        async for obj in client.iter_all():
            batch.append(obj)

            if len(batch) >= batch_size:
                await self.run_in_batches(
                    items=batch,
                    handler=handle_object,
                    batch_size=batch_size,
                    label=task_name,
                )
                batch.clear()

        # Flush remainder
        if batch:
            await self.run_in_batches(
                items=batch,
                handler=handle_object,
                batch_size=batch_size,
                label=task_name,
            )

    # --------------------------------------------------
    # Match Team Helper
    # --------------------------------------------------
    async def _match_team_helper(self,htuuid,atuuid):
        for team in [htuuid,atuuid]:
            try:
                tObj = await sync_to_async(lambda: self.models.Team.objects.get(uuid=team, vhost=self.vhost), thread_sensitive=False)()
            except self.models.Team.DoesNotExist:
                resp = await self._fetch_with_retry(f"{self.remote_host_url}/api/v1/get/teams",
                                                    params={"apikey": self.api_key,"uuid":team})
                if not resp:
                    raise ValueError(f"No Team found for {team}")
                team_data = resp.json()
                tObj,c = await sync_to_async(lambda: self.models.Team.objects.get_or_create(uuid=team, vhost=self.vhost), thread_sensitive=False)()
                if c: await sync_to_async(lambda:tObj.save(),thread_sensitive=False)()
                team_data.pop("uuid", None)
                team_data.pop("__pk", None)
                team_data.pop("vhost", None)
                await self._object_setattrs(tObj, team_data)
                await sync_to_async(lambda: tObj.save(), thread_sensitive=False)()


    async def _match_helper(self,match_uuid):
        try:
            matchObj = await sync_to_async(lambda: self.models.Match.objects.get(uuid=match_uuid, vhost=self.vhost),
                                           thread_sensitive=False)()
        except self.models.Match.DoesNotExist:
            resp = await self._fetch_with_retry(f"{self.remote_host_url}/api/v1/get/matches",
                                                params={"apikey": self.api_key, "uuid": match_uuid})
            if not resp:
                raise ValueError(f"No match found for {match_uuid}")
            match_data = resp.json()
            if (("home_team" in match_data) and ("away_team" in match_data)):
                await self._match_team_helper(match_data["home_team"]["value"], match_data["away_team"]["value"])
                match_data.pop("uuid", None)
                match_data.pop("__pk", None)
                match_data.pop("vhost", None)
                matchObj = await sync_to_async(lambda: self.models.Match(uuid=match_uuid, vhost=self.vhost), thread_sensitive=False)()
                await self._object_setattrs(matchObj, match_data)
                await sync_to_async(lambda: matchObj.save(), thread_sensitive=False)()
            else:
                if self.verbose:
                    self.logger.info(f"Match data does not contain home team and away team for: {match_uuid}  - Match Data: {match_data}")
    # --------------------------------------------------
    # Market-Odds / Outcomes Data Specific Sync
    # --------------------------------------------------
    async def sync_odds_objects(
            self,
            *,
            client,
            model,
            task_name,
            batch_size=50,
    ):
        batch = []

        async def handle_object(data):
            # print(data)
            duuid = data["uuid"]
            match_uuid = data["match"]["value"]
            await self._match_helper(match_uuid)
            modelObj, _ = await sync_to_async(
                model.objects.get_or_create,
                thread_sensitive=False,
            )(
                uuid=duuid,
                vhost=self.vhost,
            )

            # Never overwrite identity fields
            data.pop("uuid", None)
            data.pop("__pk", None)
            data.pop("vhost", None)
            try:
                await self._object_setattrs(modelObj, data)
            except IntegrityError as e:
                self.logger.info(f"For the object {duuid} - the following Exception occurred: {e}")
            return True

        async for obj in client.iter_all():
            batch.append(obj)

            if len(batch) >= batch_size:
                await self.run_in_batches(
                    items=batch,
                    handler=handle_object,
                    batch_size=batch_size,
                    label=task_name,
                )
                batch.clear()

        # Flush remainder
        if batch:
            await self.run_in_batches(
                items=batch,
                handler=handle_object,
                batch_size=batch_size,
                label=task_name,
            )

    # --------------------------------------------------
    # Match-Odds Data Specific Sync
    # --------------------------------------------------
    async def sync_match_objects(
            self,
            *,
            client,
            model,
            task_name,
            batch_size=50,
    ):
        batch = []

        async def handle_object(data):
            duuid = data["uuid"]
            await self._match_team_helper(data["home_team"]["value"], data["away_team"]["value"])
            modelObj, _ = await sync_to_async(
                model.objects.get_or_create,
                thread_sensitive=False,
            )(
                uuid=duuid,
                vhost=self.vhost,
            )

            # Never overwrite identity fields
            data.pop("uuid", None)
            data.pop("__pk", None)
            data.pop("vhost", None)
            try:
                await self._object_setattrs(modelObj, data)
            except IntegrityError as e:
                self.logger.info(f"For the object {duuid} - the following Exception occurred: {e}")
            return True

        async for obj in client.iter_all():
            batch.append(obj)

            if len(batch) >= batch_size:
                await self.run_in_batches(
                    items=batch,
                    handler=handle_object,
                    batch_size=batch_size,
                    label=task_name,
                )
                batch.clear()

        # Flush remainder
        if batch:
            await self.run_in_batches(
                items=batch,
                handler=handle_object,
                batch_size=batch_size,
                label=task_name,
            )


    # --------------------------------------------------
    # Model-specific thin handlers
    # --------------------------------------------------
    async def sync_country(self, client):
        await self.sync_objects(
            client=client,
            model=self.models.Country,
            task_name="country-sync",
            batch_size=50,
        )

    async def sync_groups(self, client):
        await self.sync_objects(
            client=client,
            model=self.models.Group,
            task_name="groups-sync",
            batch_size=50,
        )

    async def sync_sports(self, client):
        await self.sync_objects(
            client=client,
            model=self.models.Sport,
            task_name="sports-sync",
            batch_size=50,
        )

    async def sync_seasons(self, client):
        await self.sync_objects(
            client=client,
            model=self.models.Season,
            task_name="season-sync",
            batch_size=50,
        )

    async def sync_teams(self, client):
        await self.sync_objects(
            client=client,
            model=self.models.Team,
            task_name="team-sync",
            batch_size=50,
        )

    async def sync_teamsports(self, client):
        await self.sync_objects(
            client=client,
            model=self.models.TeamSport,
            task_name="team-sport-sync",
            batch_size=50,
        )

    async def sync_matches(self, client):
        await self.sync_match_objects(
            client=client,
            model=self.models.Match,
            task_name="match-sync",
            batch_size=50,
        )

    async def sync_outcomes(self, client):
        await self.sync_odds_objects(
            client=client,
            model=self.models.Outcome,
            task_name="outcomes-sync",
            batch_size=50,
        )

    async def sync_outcome_teams(self, client):
        await self.sync_objects(
            client=client,
            model=self.models.OutcomeTeams,
            task_name="outcomes-teams-sync",
            batch_size=50,
        )

    async def sync_outcome_final(self, client):
        await self.sync_objects(
            client=client,
            model=self.models.OutcomeFinalMatchScores,
            task_name="outcomes-final-sync",
            batch_size=50,
        )

    async def sync_match_odds(self,client):
        await self.sync_odds_objects(
           client=client,
           model=self.models.MatchOddsSummary,
           task_name="match-odds-sync",
           batch_size=50,
        )
    # --------------------------------------------------
    # Worker lifecycle
    # --------------------------------------------------
    async def _run(self):

        self.register_model(
            name="country",
            endpoint="/api/v1/get/country",
            handler=self.sync_country,
            hourly=True
        )
        self.register_model(
            name="groups",
            endpoint="/api/v1/get/groups",
            handler=self.sync_groups,
            hourly=True
        )

        self.register_model(
            name="sports",
            endpoint="/api/v1/get/sports",
            handler=self.sync_sports,
            hourly=True
        )

        self.register_model(
            name="seasons",
            endpoint="/api/v1/get/seasons",
            handler=self.sync_seasons,
            hourly=True
        )

        self.register_model(
            name="teams",
            endpoint="/api/v1/get/teams",
            handler=self.sync_teams,
            hourly=True
        )

        self.register_model(
            name="team-sports",
            endpoint="/api/v1/get/team/sports",
            handler=self.sync_teamsports,
            hourly=True
        )

        self.register_model(
            name="matches",
            endpoint="/api/v1/get/matches",
            handler=self.sync_matches,
            update_field_name="updated"
        )

        self.register_model(
            name="match_odds",
            endpoint="/api/v1/get/match/odds/summary",
            handler=self.sync_match_odds,
            update_field_name="last_update",
        )

        self.register_model(
            name="outcomes",
            endpoint="/api/v1/get/outcomes",
            handler=self.sync_outcomes,
            update_field_name="updated_on",
        )

        self.register_model(
            name="outcome_teams",
            endpoint="/api/v1/get/outcomes/teams",
            handler=self.sync_outcome_teams,
            update_field_name="updated_at",
        )

        self.register_model(
            name="outcome_final",
            endpoint="/api/v1/get/outcomes/final",
            handler=self.sync_outcome_final,
            update_field_name="updated_at",
        )

        self.setup_hourly()
        await AsyncWorkerABC._run(self)

    async def _hourly_work_cycle(self):
        for name, client in self._hourly_model_clients.items():
            self.logger.info(f"Executing Hourly Handler {name}...")
            handler = self._hourly_model_handlers.get(name)

            if not handler:
                continue

            try:
                await handler(client)
                client.last_timestamp = now()
            except Exception:
                self.logger.exception(
                    f"Handler failed for model '{name}'"
                )
        self.last_timestamp = now()
        self.logger.info(f"{self.name} tick...")


    async def _work_cycle(self):
        cycle_ts = now()

        # 🔒 freeze all client cursors
        for client in self._model_clients.values():
            client.last_timestamp = self.last_timestamp

        for name, client in self._model_clients.items():
            handler = self._model_handlers.get(name)
            if not handler:
                continue
            await handler(client)

        # ✅ advance parent cursor only once
        self.last_timestamp = cycle_ts
        self.logger.info(f"{self.name} tick...")


    async def _hourly_loop(self):
        """Independent loop waiting until midnight."""
        while not self._shutdown_event.is_set():
            if self._first_run:
                wait_seconds = 10
                self._first_run = False
            else:
                wait_seconds = 3600
            self.logger.info(f"[Hourly Loop] Sleeping {wait_seconds:.2f}s until next run...")
            try:
                await asyncio.wait_for(self._shutdown_event.wait(), timeout=wait_seconds)
                if self._shutdown_event.is_set():
                    break
            except asyncio.TimeoutError:
                pass

            try:
                await self._hourly_work_cycle()
            except Exception as e:
                self.logger.exception(f"[Hourly Loop] Error in job: {e}")


    def setup_hourly(self):
        """
        Called once before the main loop begins.
        Starts the midnight loop in the background so it doesn't block continuous work.
        """

        loop_fn = type(self)._hourly_loop  # ← unbound function
        self._hourly_task = asyncio.create_task(loop_fn(self))

        self.logger.info("Hourly loop started in background.")