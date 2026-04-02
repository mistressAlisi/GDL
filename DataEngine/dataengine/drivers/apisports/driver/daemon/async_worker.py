import asyncio
import os
import re
from datetime import timedelta, datetime
from io import BytesIO
from types import SimpleNamespace

import PIL
from PIL import Image
from asgiref.sync import sync_to_async, async_to_sync
from django.contrib.postgres.search import TrigramSimilarity
from django.core.files.base import ContentFile
from django.db import close_old_connections
from django.db.models import Q, OuterRef, Exists
from django.utils.timezone import now, localtime, make_aware
from rapidfuzz import fuzz

from asynctools.abc import AsyncWorkerABC

APISPORTS_DRIVER_SPORT_MASK_MAP = {
    "apisports.match.babgame": "bab",
    "apisports.match.basegame": "base",
    "apisports.match.hockgame": "hock",
    "apisports.match.amfgame": "amf",
    "apisports.match.fballgame": "fball",
}
APISPORTS_DRIVER_PERIOD_MAP = {
    "apisports.match.babgame": ["quarter_1","quarter_2","quarter_3","quarter_4","overtime"],
    "apisports.match.basegame": ["inning_1","inning_2","inning_3","inning_4","inning_5","inning_6","inning_7","inning_8","inning_9","hits","errors","extra"],
    "apisports.match.hockgame": ["first","second","third","overtime","penalties"],
    "apisports.match.amfgame": ["quarter_1","quarter_2","quarter_3","quarter_4","overtime"],
    "apisports.match.fballgame": ["halftime","fulltime","extratime","penalty"],
}
class APISportsAsyncWorker(AsyncWorkerABC):

    verbose = False
    def _child_init(self):
        """
        Runs inside the forked child *after* django.setup().
        Safe place for model imports.
        """
        super()._child_init()
        from dataengine.drivers.apisports.models import FBALLGame, BABGame, AMFGame, HOCKGame, BASEGame, FBALLGameScore, \
            BABGameScore, AMFGameScore, HOCKGameScore, BASEGameScore, Team as APITeam
        from dataengine.models import MatchSyncStatus,TeamSyncStatus

        from parameters.models import Timezone, VHostParameterRegistry
        self.last_timestamp = localtime() -timedelta(days=7)
        self.models = SimpleNamespace(
            FBALLGame=FBALLGame,
            BABGame=BABGame,
            AMFGame=AMFGame,
            HOCKGame=HOCKGame,
            BASEGame=BASEGame,
            FBALLGameScore=FBALLGameScore,
            BABGameScore=BABGameScore,
            AMFGameScore=AMFGameScore,
            HOCKGameScore=HOCKGameScore,
            BASEGameScore=BASEGameScore,
            APITeam=APITeam,
            Timezone=Timezone,
            VHostParameterRegistry=VHostParameterRegistry,
            MatchSyncStatus=MatchSyncStatus,
            TeamSyncStatus=TeamSyncStatus,

        )
        self.APISPORTS_DRIVER_MAP = {
            "apisports.match.babgame": BABGame,
            "apisports.match.basegame": BASEGame,
            "apisports.match.hockgame": HOCKGame,
            "apisports.match.amfgame": AMFGame,
            "apisports.match.fballgame": FBALLGame,

        }
        self.APISPORTS_DRIVER_SCORE_MAP = {
            "apisports.match.babgame": BABGameScore,
            "apisports.match.basegame": BASEGameScore,
            "apisports.match.hockgame": HOCKGameScore,
            "apisports.match.amfgame": AMFGameScore,
            "apisports.match.fballgame": FBALLGameScore,

        }
        from dataengine.engine.teamscoreresolver import TeamScoreResolver
        self.resolver = TeamScoreResolver(logger=self.logger)

    async def _process_team_logo(self, teamObj):
        if self.verbose:
            self.logger.info(f"Processing Team Logo for {teamObj.uuid}")

        sys_teamSync = await self.find_sync_object(
            "team", "apisports.team.Team", teamObj.uuid
        )

        if not sys_teamSync:
            return

        team = await sync_to_async(
            lambda: sys_teamSync.team,
            thread_sensitive=False,
        )()

        if team.card_logo or not teamObj.logo:
            return

        logo_resp = await self._fetch_with_retry(teamObj.logo)
        if not logo_resp or not logo_resp.content:
            return

        # Open & normalize image
        img = Image.open(BytesIO(logo_resp.content))
        img = img.convert("RGBA")  # optional, but often wise

        buffer = BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)

        filename = f"teams/{team.uuid}.png"

        await sync_to_async(
            lambda: team.card_logo.save(
                filename,
                ContentFile(buffer.read()),
                save=False,
            ),
            thread_sensitive=False,
        )()

        await sync_to_async(team.save, thread_sensitive=False)()

        if self.verbose:
            self.logger.info(f"Team Logo updated for {teamObj.uuid}")

    async def _process_fixture_data(self, fixture, key):
        """
        Robust fixture score resolution:
          - UUID-linked candidates
          - Pairwise resolution
          - Fuzzy scoring as ranking only
        """

        # ------------------------------------------------------------
        # STEP 0: Resolve system match + teams
        # ------------------------------------------------------------
        sysLink = await self.find_sync_object("match", key, fixture.uuid)
        if not sysLink:
            return

        sys_match = await sync_to_async(lambda: sysLink.match, thread_sensitive=False)()
        sys_home =  await sync_to_async(lambda:sys_match.home_team, thread_sensitive=False)()
        sys_away =  await sync_to_async(lambda:sys_match.away_team, thread_sensitive=False)()

        ScoreModel = self.APISPORTS_DRIVER_SCORE_MAP[key]

        scores = ScoreModel.objects.using("default").filter(vhost=self.vhost, match=fixture).select_related("team")
        home_score_obj = await sync_to_async(lambda:scores.filter(team=fixture.home_team).first(),thread_sensitive=False)()
        away_score_obj = await sync_to_async(lambda:scores.filter(team=fixture.away_team).first(),thread_sensitive=False)()
        if not home_score_obj or not away_score_obj:
            if self.verbose:
                self.logger.info(
                    f"[SCORES-FAIL] {fixture.uuid} "
                    f"{sys_home.name} {home_score_obj} – "
                    f"{sys_away.name} {away_score_obj} "
                )
            return


        if self.verbose:
            self.logger.info(
                f"[SCORES-OK] {fixture.uuid} "
                f"{sys_home.name} {home_score_obj.score} – "
                f"{away_score_obj.score} {sys_away.name} "
            )
        # ------------------------------------------------------------
        # STEP 4: Create outcome + teams
        # ------------------------------------------------------------
        outcome = await self._create_outcome(sys_match, key)

        finished = fixture.status_short in {
            "FT", "AOT", "CANC", "POST", "AP", "PPD", "OT"
        } or fixture.status_long in {
                       "Overtime", "Finished", "Postponed",
                       "After Penalties", "Match Finished", "Cancelled"
        }

        outcome.is_end_game = finished
        outcome.is_current = True
        outcome.status_short = fixture.status_short
        outcome.status_long = fixture.status_long

        outcome.last_home_score = home_score_obj.score
        outcome.last_away_score = away_score_obj.score

        home_outcome_team = await self._create_outcome_team(outcome, sys_home, key)
        away_outcome_team = await self._create_outcome_team(outcome, sys_away, key)

        home_outcome_team.score = home_score_obj.score
        away_outcome_team.score = away_score_obj.score

        await sync_to_async(lambda:home_outcome_team.save(), thread_sensitive=False)()
        await sync_to_async(lambda:away_outcome_team.save(), thread_sensitive=False)()

        # ------------------------------------------------------------
        # STEP 5: Segment scores
        # ------------------------------------------------------------
        if not isinstance(home_score_obj.score, int):
            for segment in APISPORTS_DRIVER_PERIOD_MAP[key]:
                h_val =   await sync_to_async(lambda:getattr(home_score_obj, segment, None),thread_sensitive=False)()
                a_val =   await sync_to_async(lambda:getattr(away_score_obj, segment, None),thread_sensitive=False)()
                if h_val is not None:
                    seg = await self._create_outcome_segment(outcome, sys_home, segment, key)
                    seg.score = h_val
                    await sync_to_async(lambda:seg.save(), thread_sensitive=False)()

                if a_val is not None:
                    seg = await self._create_outcome_segment(outcome, sys_away, segment, key)
                    seg.score = a_val
                    await sync_to_async(lambda:seg.save(), thread_sensitive=False)()

        await sync_to_async(lambda:outcome.save(), thread_sensitive=False)()



    async def sync_matches(self):
        for key,object in self.APISPORTS_DRIVER_MAP.items():
            matchSyncQuery = self.models.MatchSyncStatus.objects.filter(
                driver_object_uuid=OuterRef("pk"),
                driver_object_type=key
            )
            fixtures = (object.objects.using("default").annotate(has_sync=Exists(matchSyncQuery))
                        .filter(vhost=self.vhost, updated_at__gte=self.last_timestamp,))
            fixtureList = await sync_to_async(lambda: list(fixtures), thread_sensitive=False)()
            async def handler(m):
                return await self._process_fixture_data(m,key)
            await self.run_in_batches(fixtureList, handler, self.max_workers,
                                      f"apisports_{key}_fixtures_score")

    async def get_missing_team_logos(self):
        teamsList = await sync_to_async(lambda: list(self.models.APITeam.objects.all()), thread_sensitive=False)()
        await self.run_in_batches(teamsList, self._process_team_logo, self.max_workers,
                                  f"apisports_team_logo_score")
    async def _work_cycle(self):
        await self.sync_matches()
        self.last_timestamp = localtime()
        #await sync_to_async(lambda:close_old_connections(),thread_sensitive=True)()
        self.logger.info(f"APISports Sync Complete!")