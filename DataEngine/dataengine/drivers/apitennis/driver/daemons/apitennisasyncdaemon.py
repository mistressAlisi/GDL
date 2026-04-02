import asyncio
import json
import os
import re
import unicodedata
from decimal import Decimal
from difflib import SequenceMatcher
from types import SimpleNamespace
from urllib.parse import urlencode
import traceback
import time
from zoneinfo import ZoneInfo

import httpcore
import httpx
from datetime import datetime, timedelta

import pytz
import websockets
from asgiref.sync import sync_to_async
from celery.fixups.django import fixup
from django.conf import settings
from django.contrib.postgres.search import TrigramSimilarity
from django.db import connections, close_old_connections
from django.db.models import Q, ExpressionWrapper, F, Func, DateTimeField, Value, FloatField, OuterRef, Exists, Subquery
from django.db.models.functions import Greatest
from django.forms import model_to_dict
from django.utils import timezone
from django.utils.timezone import now, localtime, localdate
from httpx import ReadTimeout
from rapidfuzz import fuzz
from websockets import ConnectionClosedError, ConnectionClosedOK



from asynctools.abc import AsyncWorkerABC

TENNIS_DRIVER_NAME = "apitennis.fixture.Fixture"
TENNIS_PLAYER_DRV_NAME = "apitennis.players.Players"


class APITennisAsyncDaemon(AsyncWorkerABC):
    """
    Forkserver-safe Async Tennis daemon.

    Django models are bound ONLY in child processes.
    """

    last_timestamp = None
    websocket = None
    api_key = None
    httpx = httpx.AsyncClient()
    regappid = "dataengine.drivers.apitennis"
    url_root = "https://api.api-tennis.com/tennis/?"
    wss_root = "wss://wss.api-tennis.com/live"
    # debug = True
    # verbose = True
    # ----------------------
    # Child bootstrap
    # ----------------------
    def _child_init(self):
        """
        Runs inside the forked child *after* django.setup().
        Safe place for model imports.
        """
        super()._child_init()
        from dataengine.models import MatchSyncStatus
        from matches.models import Match
        from dataengine.drivers.apitennis.models.fixtures import Fixture, FixtureView
        from dataengine.drivers.apitennis.models.players import Players
        from dataengine.drivers.apitennis.models.tournaments import EventType, Tournament
        from parameters.models import VHostParameterRegistry
        from outcomes.models import (
            OutcomeTeams as Sys_OutcomeTeams,
            Outcome as Sys_Outcome,
            OutcomeSegmentScore as Sys_OutcomeSegmentScore,
        )
        from django.utils.timezone import localtime
        from datetime import timedelta

        self.last_timestamp = localtime() - timedelta(days=2)
        self.models = SimpleNamespace(
            MatchSyncStatus=MatchSyncStatus,
            Match=Match,
            Fixture=Fixture,
            FixtureView=FixtureView,
            Players=Players,
            EventType=EventType,
            Tournament=Tournament,
            VHostParameterRegistry=VHostParameterRegistry,
            Sys_OutcomeTeams=Sys_OutcomeTeams,
            Sys_Outcome=Sys_Outcome,
            Sys_OutcomeSegmentScore=Sys_OutcomeSegmentScore,

        )

        self.logger.debug("APITennisAsyncDaemon: Django models bound in child")



    # ----------------------
    # API helpers
    # ----------------------
    async def get_api_tennis_key(self):
        if not self.api_key:
            VHostParameterRegistry = self.models.VHostParameterRegistry
            apiSettings, _ = await sync_to_async(
                lambda: VHostParameterRegistry.objects.get_or_create(
                    vhost=self.vhost,
                    application=self.regappid,
                    name="api_key_str",
                ),
                thread_sensitive=False,
            )()
            self.api_key = apiSettings.value_text
        return self.api_key

    # ----------------------
    # WebSocket
    # ----------------------
    async def connect_wss(self, retry_delay=5):
        key = await self.get_api_tennis_key()
        while True:
            try:
                self.logger.info(f"Connecting to {self.wss_root}")
                self.websocket = await websockets.connect(
                    f"{self.wss_root}?APIkey={key}"
                )
                asyncio.create_task(self._listen_wss())
                return
            except Exception:
                self.logger.exception("WSS connect failed")
                await asyncio.sleep(retry_delay)

    async def _listen_wss(self):
        while True:
            try:
                async for message in self.websocket:
                    data = json.loads(message)
                    for event in data:
                        if "event_key" in event:
                            await self.process_incoming_fixture(event)
            except Exception:
                self.logger.warning("WSS disconnected, reconnecting")
                await asyncio.sleep(5)
                await self.connect_wss()
                return

    # ----------------------
    # Fixture processing
    # ----------------------
    async def process_incoming_fixture(self, res):
        # if self.debug and self.verbose:
        #     self.logger.info(f"Incoming fixture to be processed, {res}")
        args = {"vhost": self.vhost}

        for key in ["event_type_type", "event_type_key"]:
            if key in res:
                args[key] = res[key]

        try:
            event_type, cc = await sync_to_async(lambda: self.models.EventType.objects.get_or_create(**args),
                                                 thread_sensitive=False)()
            if cc:
                await sync_to_async(lambda: event_type.save(), thread_sensitive=False)()
        except self.models.EventType.MultipleObjectsReturned:
            event_type = await sync_to_async(lambda: self.models.EventType.objects.filter(**args).first(), thread_sensitive=False)()

        tournamentObj = False
        try:
            tournamentObj = await sync_to_async(
                lambda: self.models.Tournament.objects.get(vhost=self.vhost, tournament_key=res["tournament_key"],
                                               event_type=event_type), thread_sensitive=False)()
        except self.models.Tournament.DoesNotExist:
            try:
                tournamentObj, cc = await sync_to_async(lambda: self.models.Tournament.objects.get_or_create(vhost=self.vhost,
                                                                                                 tournament_key=res[
                                                                                                     "tournament_key"],
                                                                                                 tournament_name=res[
                                                                                                     "tournament_name"],
                                                                                                 event_type=event_type),
                                                        thread_sensitive=False)()
                if cc:
                    await sync_to_async(lambda: tournamentObj.save(), thread_sensitive=False)()
            except self.models.Tournament.MultipleObjectsReturned:
                tournamentObj = await sync_to_async(
                    lambda: self.models.Tournament.objects.filter(vhost=self.vhost, tournament_key=res["tournament_key"],
                                                      tournament_name=res["tournament_name"],
                                                      event_type=event_type).first(), thread_sensitive=False)()
        except self.models.Tournament.MultipleObjectsReturned:
            tournamentObj = await sync_to_async(lambda: self.models.Tournament.objects.filter(vhost=self.vhost,
                                                                                  tournament_key=res["tournament_key"],
                                                                                  tournament_name=res[
                                                                                      "tournament_name"],
                                                                                  event_type=event_type).first(),
                                                thread_sensitive=False)()
        try:
            first_player, cc = await sync_to_async(
                lambda: self.models.Players.objects.get_or_create(vhost=self.vhost, player_name=res["event_first_player"],
                                                      player_key=res["first_player_key"]), thread_sensitive=False)()
            if cc: await sync_to_async(lambda: first_player.save(), thread_sensitive=False)()
        except self.models.Players.MultipleObjectsReturned:
            first_player = await sync_to_async(
                lambda: self.models.Players.objects.filter(vhost=self.vhost, player_name=res["event_first_player"],
                                               player_key=res["first_player_key"]).first(), thread_sensitive=False)()

        try:
            second_player, cc = await sync_to_async(lambda: self.models.Players.objects.get_or_create(vhost=self.vhost,
                                                                                          player_name=res[
                                                                                              "event_second_player"],
                                                                                          player_key=res[
                                                                                              "second_player_key"]),
                                                    thread_sensitive=False)()
            if cc: await sync_to_async(lambda: second_player.save(), thread_sensitive=False)()
        except self.models.Players.MultipleObjectsReturned:
            second_player = await sync_to_async(lambda: self.models.Players.objects.filter(vhost=self.vhost,
                                                                               player_name=res[
                                                                                   "event_second_player"],
                                                                               player_key=res[
                                                                                   "second_player_key"]).first(),
                                                thread_sensitive=False)()

        fixtureObj, _ = await sync_to_async(
            lambda: self.models.Fixture.objects.get_or_create(vhost=self.vhost, event_key=res["event_key"],
                                                  tournament=tournamentObj, event_first_player=first_player,
                                                  event_second_player=second_player, event_type=event_type),
            thread_sensitive=False)()
        fields = fixtureObj._meta.get_fields()

        for f in fields:
            if f.name in res and f.name not in ["event_first_player", "event_second_player", "event_type",
                                                "tournament", "event_winner"]:
                setattr(fixtureObj, f.name, res[f.name])

        fixtureObj.commence_time = pytz.timezone(settings.TIME_ZONE).localize(
            datetime.strptime(f"{fixtureObj.event_date} {fixtureObj.event_time}", "%Y-%m-%d %H:%M"))

        if "event_winner" in res:
            if res["event_winner"]:
                if res["event_winner"] == "First Player":
                    fixtureObj.event_winner = first_player
                elif res["event_winner"] == "Second Player":
                    fixtureObj.event_winner = second_player

        fixtureObj.updated_on = localtime()
        if self.debug:
            self.logger.info(f"Updated Incoming Fixture {fixtureObj.uuid}")
        await sync_to_async(lambda: fixtureObj.save(), thread_sensitive=False)()
        sysLink = await self.find_sync_object(
            "match",
            TENNIS_DRIVER_NAME,
            fixtureObj.uuid
        )

        if sysLink:
            self.logger.info(f"Updated Incoming Fixture {fixtureObj.uuid} has MatchSyncStatus - triggering update")
            # Fire-and-forget: do not block WSS listener
            asyncio.create_task(self._process_fixture(fixtureObj))
        else:
            if self.debug:
                self.logger.info(f"Updated Incoming Fixture {fixtureObj.uuid} does not have MatchSyncStatus")

    async def get_fixtures(self, **kwargs):
        label = "get_fixtures"
        payload = {"method": "get_fixtures", "APIkey": await self.get_api_tennis_key(), "timezone": settings.TIME_ZONE}
        if "livescore" in kwargs:
            payload["method"] = "get_livescore"
        else:
            if "date_start" not in kwargs:
                payload["date_start"] = (datetime.today() - timedelta(days=1)).strftime("%Y-%m-%d")
            else:
                payload["date_start"] = (datetime.today() + timedelta(days=1)).strftime("%Y-%m-%d")
            if "date_stop" not in kwargs:
                payload["date_stop"] = datetime.today().strftime("%Y-%m-%d")
            else:
                payload["date_stop"] = kwargs["date_stop"]

        for key in ["event_type_key", "tournament_key", "tournament_season", "match_key", "player_key"]:
            if key in kwargs:
                payload[key] = kwargs[key]

        data = await self._fetch_with_retry(self.url_root + urlencode(payload))
        if not data:
            return None

        if (data.status_code != 200):
            self.logger.warning("Error!", data.status_code, data.text)
            return False
        data = data.json()
        results = data.get("result", [])
        self.logger.info(f"Fixture Data Fetched: {len(results)} Fixtures fetched:")

        valid_results = []
        for res in results:
            if "event_type_key" not in res and "event_type_type" not in res:
                self.logger.warning(f"Warning: {res} had no event_type_key or event_type_type")
            else:
                valid_results.append(res)

        await self.run_in_batches(valid_results,self.process_incoming_fixture)


    def _normalize_name(self,name: str) -> str:
        """Normalize names for fuzzy matching."""
        if not name:
            return ""
        # Unicode normalize
        name = unicodedata.normalize("NFKD", name)
        # Lowercase
        name = name.lower()
        # Remove punctuation
        name = re.sub(r"[^\w\s]", "", name)
        # Collapse multiple spaces
        name = re.sub(r"\s+", " ", name).strip()
        return name

    async def _process_fixture(self, fixture):
        if getattr(fixture, "_being_processed", False):
            return

        fixture._being_processed = True
        sysLink = await self.find_sync_object("match", TENNIS_DRIVER_NAME, fixture.uuid)
        if not sysLink:
            if self.debug:
                self.logger.info(f"Fixture link/sync not found: {fixture.uuid}")
            return None

        matchObj = await sync_to_async(lambda: sysLink.match, thread_sensitive=False)()

        # Fetch fixture players
        home_player = await sync_to_async(lambda: fixture.event_first_player, thread_sensitive=False)()
        away_player = await sync_to_async(lambda: fixture.event_second_player, thread_sensitive=False)()

        # System teams
        sys_home_team = await sync_to_async(lambda: sysLink.match.home_team, thread_sensitive=False)()
        sys_away_team = await sync_to_async(lambda: sysLink.match.away_team, thread_sensitive=False)()

        # Driver object links
        sys_home_team_link = await self.find_sync_object("team", TENNIS_PLAYER_DRV_NAME, False,
                                                         system_obj=sys_home_team)
        sys_away_team_link = await self.find_sync_object("team", TENNIS_PLAYER_DRV_NAME, False,
                                                         system_obj=sys_away_team)
        manual_override = False
        flipped = None

        if sys_home_team_link and getattr(sys_home_team_link, "manual_entry", False):
            manual_override = True
            flipped = False  # system home == driver first player

        if sys_away_team_link and getattr(sys_away_team_link, "manual_entry", False):
            manual_override = True
            flipped = True  # system away == driver first player
        # Normalize all names to lowercase, stripped, simplified
        sys_home_team_name = await sync_to_async(lambda: self._normalize_name(getattr(sys_home_team, "name", "")),
                                                 thread_sensitive=False)()
        sys_away_team_name = await sync_to_async(lambda: self._normalize_name(getattr(sys_away_team, "name", "")),
                                                 thread_sensitive=False)()
        first_player_name = await sync_to_async(lambda: self._normalize_name(getattr(home_player, "player_name", "")),
                                                thread_sensitive=False)()
        second_player_name = await sync_to_async(lambda: self._normalize_name(getattr(away_player, "player_name", "")),
                                                 thread_sensitive=False)()
        # --- DEBUG logging ---
        if self.debug:
            self.logger.info(
                f"[DEBUG] Fixture {fixture.uuid} mapping:"
                f"\n  first_player: {getattr(home_player, 'uuid', None)} / {first_player_name}"
                f"\n  second_player: {getattr(away_player, 'uuid', None)} / {second_player_name}"
                f"\n  sys_home_team: {getattr(sys_home_team_link, 'driver_object_uuid', None)} / {sys_home_team_name}"
                f"\n  sys_away_team: {getattr(sys_away_team_link, 'driver_object_uuid', None)} / {sys_away_team_name}"
            )

        if manual_override:
            home_team_canonical = sys_home_team if not flipped else sys_away_team
            away_team_canonical = sys_away_team if not flipped else sys_home_team

            if self.debug:
                self.logger.info(
                    f"[MANUAL-TENNIS-MAP] Fixture {fixture.uuid} "
                    f"home={home_team_canonical.uuid} away={away_team_canonical.uuid} flipped={flipped}"
                )

        else:
            # --- Two-way RapidFuzz matching ---
            sim_home_first = fuzz.partial_ratio(sys_home_team_name, first_player_name)
            sim_home_second = fuzz.partial_ratio(sys_home_team_name, second_player_name)
            sim_away_first = fuzz.partial_ratio(sys_away_team_name, first_player_name)
            sim_away_second = fuzz.partial_ratio(sys_away_team_name, second_player_name)

            mappingA_score = sim_home_first + sim_away_second
            mappingB_score = sim_home_second + sim_away_first

            threshold = 60
            if mappingA_score >= mappingB_score and mappingA_score >= 2 * threshold:
                home_team_canonical = sys_home_team
                away_team_canonical = sys_away_team
                flipped = False
            elif mappingB_score > mappingA_score and mappingB_score >= 2 * threshold:
                home_team_canonical = sys_away_team
                away_team_canonical = sys_home_team
                flipped = True
            else:
                home_team_canonical = sys_home_team
                away_team_canonical = sys_away_team
                flipped = None

                if self.debug:
                    self.logger.warning(
                        f"[DEBUG] Fixture {fixture.uuid} mapping ambiguous, using system home/away"
                    )

            if self.debug:
                self.logger.info(
                    f"[DEBUG] Fixture {fixture.uuid} Scores and Mappings:"
                    f"\n  sim_scores: HS:{sim_home_first},{sim_home_second} AS:{sim_away_first},{sim_away_second}"
                    f"\n  mapping_scores: A:{mappingA_score} B:{mappingB_score}"
                )
        if self.debug:
            self.logger.info(
                f"[DEBUG] Fixture {fixture.uuid} canonical mapping:"
                f"\n  home_team_canonical: {home_team_canonical.uuid}"
                f"\n  away_team_canonical: {away_team_canonical.uuid}"
                f"\n  flipped: {flipped}"
            )

        # --- Score processing ---
        fw, sw = False, False
        first_score, second_score = 0, 0
        outcomeObj = await self._create_outcome(sysLink.match, TENNIS_DRIVER_NAME)

        for score in fixture.scores:
            set_name = f'Set {score["score_set"]}'
            first = Decimal(score["score_first"])
            second = Decimal(score["score_second"])
            if first == 0 and second == 0:
                continue

            if first > second:
                fw, sw = True, False
                first_score += 1
            else:
                fw, sw = False, True
                second_score += 1

            # --- Home segment ---
            segScoreObj = await self._create_outcome_segment(outcomeObj, home_team_canonical, set_name,
                                                             TENNIS_DRIVER_NAME)
            segScoreObj.score = first_score if not flipped else second_score
            segScoreObj.is_winner = fw if not flipped else sw
            await sync_to_async(lambda: segScoreObj.save(), thread_sensitive=False)()

            # --- Away segment ---
            segScoreObj = await self._create_outcome_segment(outcomeObj, away_team_canonical, set_name,
                                                             TENNIS_DRIVER_NAME)
            segScoreObj.score = second_score if not flipped else first_score
            segScoreObj.is_winner = sw if not flipped else fw
            await sync_to_async(lambda: segScoreObj.save(), thread_sensitive=False)()

        # --- End game / fixture status ---
        finished = fixture.event_status in ["Finished", "Cancelled", "Retired", "Not Started", "Walk Over"]
        #  NOTE: Warning. This might fix a problem we have with tennis.
        # if timezone.now() - matchObj.commence_time >= timedelta(hours=8):
        #     finished = True

        try:
            ctdt = datetime.strptime(f"{fixture.event_date}T{fixture.event_time}", "%Y-%m-%dT%H:%M:%S")
        except ValueError:
            ctdt = datetime.strptime(f"{fixture.event_date}T{fixture.event_time}", "%Y-%m-%dT%H:%M")
        if not ctdt:
            self.logger.warning(f"Fixture {fixture.uuid} has no event date we could parse: {fixture.event_date}T{fixture.event_time}")
        commence_time = timezone.make_aware(ctdt)

        # if commence_time >= timezone.now() + timedelta(hours=8):
        #     finished = True

        outcomeObj.is_end_game = finished
        outcomeObj.is_finished = finished
        outcomeObj.is_current = True
        outcomeObj.status_short = fixture.event_status
        outcomeObj.status_long = fixture.event_status
        await sync_to_async(lambda: outcomeObj.save(), thread_sensitive=False)()

        if self.debug:
            self.logger.info(
                f"[DEBUG] Fixture {fixture.uuid} processed: "
                f"first_score={first_score}, second_score={second_score}, finished={finished}"
            )

        # --- Outcome teams ---
        if first_score >= 0 or second_score >= 0:
            outcomeHomeTeamObj = await self._create_outcome_team(outcomeObj, home_team_canonical, TENNIS_DRIVER_NAME)
            outcomeAwayTeamObj = await self._create_outcome_team(outcomeObj, away_team_canonical, TENNIS_DRIVER_NAME)

            if flipped is False or flipped is None:
                outcomeHomeTeamObj.score = first_score
                outcomeAwayTeamObj.score = second_score
                outcomeObj.last_home_score = first_score
                outcomeObj.last_away_score = second_score
            else:
                outcomeHomeTeamObj.score = second_score
                outcomeAwayTeamObj.score = first_score
                outcomeObj.last_home_score = second_score
                outcomeObj.last_away_score = first_score
            await sync_to_async(lambda: outcomeHomeTeamObj.save(), thread_sensitive=False)()
            await sync_to_async(lambda: outcomeAwayTeamObj.save(), thread_sensitive=False)()
            await sync_to_async(lambda: outcomeObj.save(), thread_sensitive=False)()
            if self.debug:
                await sync_to_async(lambda:self.logger.info(
                    f"[DEBUG] Fixture {fixture.uuid} processed: "
                    f"Outcome UUID is {outcomeObj.uuid} LHS: { outcomeObj.last_home_score} [{first_score}], LAS: { outcomeObj.last_home_score} [{second_score}]"
                ),thread_sensitive=True)()
        else:
            if self.debug:
                self.logger.info(
                    f"[DEBUG] Fixture {fixture.uuid} not processed: First and second scores are < 0 or none.")
        fixture._being_processed = False
        await sync_to_async(lambda: fixture.save(), thread_sensitive=False)()

    def get_sync_fixtures(self, **kwargs):
        match_sync_exists = self.models.MatchSyncStatus.objects.filter(
            driver_object_uuid=OuterRef("uuid"),
            driver_object_type=TENNIS_DRIVER_NAME,
        )

        match_updated_recently = self.models.Match.objects.filter(
            uuid=Subquery(
                self.models.MatchSyncStatus.objects.filter(
                    driver_object_uuid=OuterRef("uuid"),
                    driver_object_type=TENNIS_DRIVER_NAME,
                ).values("system_object_uuid")[:1]
            ),
            updated__gte=self.last_timestamp,
        )

        match_sync_updated_recently = self.models.MatchSyncStatus.objects.filter(
            driver_object_uuid=OuterRef("uuid"),
            driver_object_type=TENNIS_DRIVER_NAME,
            updated__gte=self.last_timestamp,
        )

        fixtures_qs = (
            self.models.Fixture.objects
            .filter(vhost=self.vhost)
            .annotate(
                has_match_sync=Exists(match_sync_exists),
                match_updated=Exists(match_updated_recently),
                match_sync_updated=Exists(match_sync_updated_recently),
            )
            .filter(
                Q(updated_on__gte=self.last_timestamp)
                | Q(match_updated=True)
                | Q(match_sync_updated=True),
                has_match_sync=True,
            )
        )

        return fixtures_qs


    async def sync_fixtures(self, **kwargs):

        fixtures_qs = await sync_to_async(self.get_sync_fixtures)(**kwargs)
        # print("FS")
        fixtureList = await sync_to_async(
            lambda: list(fixtures_qs),
            thread_sensitive=False,
        )()
        # print(fixtureList)
        # print("Ayiee")

        await self.run_in_batches(fixtureList, self._process_fixture, self.max_workers,
                                  f"apitennis_fixtures_score")

    # ----------------------
    # Worker loop
    # ----------------------
    async def _run(self):

        await super()._run()
        await self.connect_wss()

    async def _work_cycle(self):
        # print("APITENNIS")
        await asyncio.gather(
            self.get_fixtures(),
            self.sync_fixtures(after_time=self.last_timestamp),
            return_exceptions=True
        )
        self.last_timestamp = localtime()
        self.logger.info("APITennis tick complete")
        #await sync_to_async(lambda:close_old_connections(),thread_sensitive=True)()
        # print("APITENNIS2")
