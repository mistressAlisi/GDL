import asyncio
import datetime
import logging
import re
import unicodedata
from decimal import Decimal

from types import SimpleNamespace

from asgiref.sync import sync_to_async
from celery.fixups.django import fixup
from django.db.models import OuterRef, Exists
from django.utils.timezone import localdate, now, localtime

from pydantic import ValidationError
from rapidfuzz import fuzz

from asynctools.abc import AsyncWorkerABC


SOCCER_DRIVER_STR = "goalserve.match.soccerfixture"
AMF_DRIVER_STR = "goalserve.match.amfgame"
BASE_DRIVER_STR = "goalserve.match.baseballfixture"
BBL_DRIVER_STR = "goalserve.match.basketballfixture"
HOCK_DRIVER_STR = "goalserve.match.hockgame"
TEN_DRIVER_STR = "goalserve.match.TennisFixture"
TEAM_DRIVER_STR = "goalserve.team.Team"
class GoalServeScoreD(AsyncWorkerABC):
    url_root = "https://www.goalserve.com/getfeed/8015a863314c4c5ff1b808de315f0ca1"
    regappid = "dataengine.drivers.goalserve"
    last_timestamp = now() - datetime.timedelta(days=7)
    # debug = True
    def __init__(self, vhost = object ,logger = object, name: str = "worker", interval: float = 60,run_in_process: bool = True,loki_url=None):
        if logger is None or not isinstance(logger, logging.Logger):
            logger = logging.getLogger(name)
            logger.setLevel(logging.INFO)
        AsyncWorkerABC.__init__(self,vhost, logger, name, interval,run_in_process,loki_url)
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
    def _child_init(self):
        """
        Runs inside the forked child *after* django.setup().
        Safe place for model imports.
        """
        super()._child_init()
        from dataengine.drivers.goalserve.models import SportCategory, SoccerFixture, Team, SoccerFixtureScore, \
            SoccerEvent, \
            BasketBallFixture, BasketBallScore, TennisFixture, TennisScore, HockeyFixture, HockeyEvent, \
            HockeyFixtureScore, \
            AmericanFBallFixture, AmericanFBallScore
        from dataengine.drivers.goalserve.models.baseball import BaseBallScore, BaseBallFixture
        from dataengine.models import MatchSyncStatus
        # from outcomes.engine import OutcomesEngine
        from outcomes.models import Outcome, OutcomeTeams, OutcomeSegmentScore
        self.last_timestamp = localtime()
        self.models = SimpleNamespace(
            SportCategory=SportCategory,
            SoccerFixture=SoccerFixture,
            Team=Team,
            SoccerFixtureScore=SoccerFixtureScore,
            SoccerEvent=SoccerEvent,
            BasketBallFixture=BasketBallFixture,
            BasketBallScore=BasketBallScore,
            TennisFixture=TennisFixture,
            TennisScore=TennisScore,
            HockeyFixture=HockeyFixture,
            HockeyEvent=HockeyEvent,
            HockeyFixtureScore=HockeyFixtureScore,
            AmericanFBallFixture=AmericanFBallFixture,
            AmericanFBallScore=AmericanFBallScore,
            BaseBallScore=BaseBallScore,
            BaseBallFixture=BaseBallFixture,
            MatchSyncStatus=MatchSyncStatus,
            Outcome=Outcome,
            OutcomeTeams=OutcomeTeams,
            OutcomeSegmentScore=OutcomeSegmentScore,


        )

    #-----------------------------------
    # Soccer
    #-----------------------------------
    async def process_soccer_fixture_score(self,fixture):
        sysLink = await self.find_sync_object("match",SOCCER_DRIVER_STR,fixture.uuid)
        if sysLink:
            if self.verbose:
                self.logger.info(f"Processing Soccer Fixture {fixture.uuid} Scores...")
            home_team = await sync_to_async(lambda: fixture.home_team, thread_sensitive=False)()
            away_team = await sync_to_async(lambda: fixture.away_team, thread_sensitive=False)()
            sys_home_team = await sync_to_async(lambda: sysLink.match.home_team, thread_sensitive=False)()
            sys_away_team = await sync_to_async(lambda: sysLink.match.away_team, thread_sensitive=False)()
            scores = self.models.SoccerFixtureScore.objects.using("default").filter(vhost=self.vhost,fixture=fixture)
            home_score = await sync_to_async(lambda:scores.filter(team = home_team).first(),thread_sensitive=False)()
            away_score = await sync_to_async(lambda:scores.filter(team = away_team).first(),thread_sensitive=False)()
            outcomeObj = await self._create_outcome(sysLink.match, SOCCER_DRIVER_STR)
            outcomeObj.is_current = True
            finished = False
            if fixture.status in ["FT","AET","Pen.","Canc."]:
                finished = True
            outcomeObj.is_end_game = finished
            outcomeObj.status_short = fixture.status
            outcomeObj.status_long = fixture.status
            await sync_to_async(lambda: outcomeObj.save(), thread_sensitive=False)()
            if home_score and away_score:
                outcomeHomeTeamObj = await self._create_outcome_team(outcomeObj,sys_home_team,SOCCER_DRIVER_STR)
                outcomeAwayTeamObj = await self._create_outcome_team(outcomeObj, sys_away_team, SOCCER_DRIVER_STR)
                outcomeHomeTeamObj.score = home_score.score
                outcomeAwayTeamObj.score = away_score.score
                outcomeObj.last_home_score = home_score.score
                outcomeObj.last_away_score = away_score.score
                await sync_to_async(lambda: outcomeObj.save(), thread_sensitive=False)()
                await sync_to_async(lambda:outcomeHomeTeamObj.save(),thread_sensitive=False)()
                await sync_to_async(lambda:outcomeAwayTeamObj.save(),thread_sensitive=False)()
        # else:
        #     print(f"Nolink {fixture.uuid} fixture not found")

    async def process_soccer_fixtures(self):
        matchSyncQuery = self.models.MatchSyncStatus.objects.using("default").filter(
            driver_object_uuid=OuterRef("pk"),
            driver_object_type=SOCCER_DRIVER_STR
        )
        fixtures = (self.models.SoccerFixture.objects.using("default").annotate(has_sync=Exists(matchSyncQuery))
                    .filter(vhost=self.vhost,updated_at__gte=self.last_timestamp,has_sync=True))
        fixtureList = await sync_to_async(lambda:list(fixtures),thread_sensitive=False)()
        await self.run_in_batches(fixtureList,self.process_soccer_fixture_score,self.max_workers,"soccer_fixtures_score")


    #-----------------------------------
    # American Football
    #-----------------------------------
    async def process_american_fixture_score(self,fixture):
        sysLink = await self.find_sync_object("match",AMF_DRIVER_STR,fixture.uuid)
        if sysLink:
            if self.verbose:
                self.logger.info(f"Processing American Football Fixture {fixture.uuid} Scores...")
            home_team = await sync_to_async(lambda: fixture.home_team, thread_sensitive=False)()
            away_team = await sync_to_async(lambda: fixture.away_team, thread_sensitive=False)()
            sys_home_team = await sync_to_async(lambda: sysLink.match.home_team, thread_sensitive=False)()
            sys_away_team = await sync_to_async(lambda: sysLink.match.away_team, thread_sensitive=False)()
            scores = self.models.AmericanFBallScore.objects.using("default").filter(vhost=self.vhost,fixture=fixture)
            home_score = await sync_to_async(lambda:scores.filter(team = home_team).first(),thread_sensitive=False)()
            away_score = await sync_to_async(lambda:scores.filter(team = away_team).first(),thread_sensitive=False)()
            finished = False
            outcomeObj = await self._create_outcome(sysLink.match,AMF_DRIVER_STR)
            outcomeObj.is_current = True
            if fixture.status in ["Final","After Over Time"]:
                finished = True
            outcomeObj.is_end_game = finished
            outcomeObj.status_short = fixture.status
            outcomeObj.status_long = fixture.status
            await sync_to_async(lambda: outcomeObj.save(), thread_sensitive=False)()
            if home_score and away_score:

                outcomeHomeTeamObj = await self._create_outcome_team(outcomeObj,sys_home_team,AMF_DRIVER_STR)
                outcomeAwayTeamObj = await self._create_outcome_team(outcomeObj, sys_away_team, AMF_DRIVER_STR)
                outcomeHomeTeamObj.score = home_score.score
                outcomeAwayTeamObj.score = away_score.score
                outcomeObj.last_home_score = home_score.score
                outcomeObj.last_away_score = away_score.score
                await sync_to_async(lambda: outcomeObj.save(), thread_sensitive=False)()
                await sync_to_async(lambda:outcomeHomeTeamObj.save(),thread_sensitive=False)()
                await sync_to_async(lambda:outcomeAwayTeamObj.save(),thread_sensitive=False)()
                for i in ["q1","q2","q3","q4","ot"]:
                    segScoreObj = await self._create_outcome_segment(outcomeObj,sys_home_team,i,AMF_DRIVER_STR)
                    segScoreObj.score = getattr(home_score,i)
                    await sync_to_async(lambda:segScoreObj.save(),thread_sensitive=False)()
                    segScoreObj = await self._create_outcome_segment(outcomeObj,sys_away_team,i,AMF_DRIVER_STR)
                    segScoreObj.score = getattr(away_score,i)
                    await sync_to_async(lambda:segScoreObj.save(),thread_sensitive=False)()
        # else:
        #     print(f"Nolink {fixture.uuid} fixture not found")

    async def process_american_fixtures(self):
        matchSyncQuery = self.models.MatchSyncStatus.objects.using("default").filter(
            driver_object_uuid=OuterRef("pk"),
            driver_object_type=AMF_DRIVER_STR
        )
        fixtures = (self.models.AmericanFBallFixture.objects.using("default").annotate(has_sync=Exists(matchSyncQuery))
                    .filter(vhost=self.vhost,updated_at__gte=self.last_timestamp,has_sync=True))
        fixtureList = await sync_to_async(lambda:list(fixtures),thread_sensitive=False)()
        await self.run_in_batches(fixtureList,self.process_american_fixture_score,self.max_workers,"american_fixtures_score")



    #-----------------------------------
    # Baseball
    #-----------------------------------
    async def process_baseball_fixture_score(self,fixture):
        sysLink = await self.find_sync_object("match",BASE_DRIVER_STR,fixture.uuid)
        if sysLink:
            if self.verbose:
                self.logger.info(f"Processing Baseball Fixture {fixture.uuid} Scores...")
            home_team = await sync_to_async(lambda: fixture.home_team, thread_sensitive=False)()
            away_team = await sync_to_async(lambda: fixture.away_team, thread_sensitive=False)()
            sys_home_team = await sync_to_async(lambda: sysLink.match.home_team, thread_sensitive=False)()
            sys_away_team = await sync_to_async(lambda: sysLink.match.away_team, thread_sensitive=False)()
            scores = self.models.BaseBallScore.objects.using("default").filter(vhost=self.vhost,fixture=fixture)
            home_score = await sync_to_async(lambda:scores.filter(team = home_team).first(),thread_sensitive=False)()
            away_score = await sync_to_async(lambda:scores.filter(team = away_team).first(),thread_sensitive=False)()
            outcomeObj = await self._create_outcome(sysLink.match,BASE_DRIVER_STR)
            outcomeObj.is_current = True
            finished = False
            if fixture.status in ["Finished","Postponed"]:
                finished = True
            outcomeObj.is_end_game = finished
            outcomeObj.status_short = fixture.status
            outcomeObj.status_long = fixture.status
            await sync_to_async(lambda: outcomeObj.save(), thread_sensitive=False)()
            if home_score and away_score:
                outcomeHomeTeamObj = await self._create_outcome_team(outcomeObj,sys_home_team,BASE_DRIVER_STR)
                outcomeAwayTeamObj = await self._create_outcome_team(outcomeObj, sys_away_team, BASE_DRIVER_STR)
                outcomeHomeTeamObj.score = home_score.score
                outcomeAwayTeamObj.score = away_score.score
                outcomeObj.last_home_score = home_score.score
                outcomeObj.last_away_score = away_score.score
                await sync_to_async(lambda: outcomeObj.save(), thread_sensitive=False)()
                await sync_to_async(lambda:outcomeHomeTeamObj.save(),thread_sensitive=False)()
                await sync_to_async(lambda:outcomeAwayTeamObj.save(),thread_sensitive=False)()
                for i in ["in1","in2","in3","in4","in5","in6","in7","in8","in9","extra","hits","errors"]:
                    segScoreObj = await self._create_outcome_segment(outcomeObj,sys_home_team,i,BASE_DRIVER_STR)
                    segScoreObj.score = getattr(home_score,i)
                    await sync_to_async(lambda:segScoreObj.save(),thread_sensitive=False)()
                    segScoreObj = await self._create_outcome_segment(outcomeObj,sys_away_team,i,BASE_DRIVER_STR)
                    segScoreObj.score = getattr(away_score,i)
                    await sync_to_async(lambda:segScoreObj.save(),thread_sensitive=False)()
        # else:
        #     print(f"Nolink {fixture.uuid} fixture not found")

    async def process_baseball_fixtures(self):
        matchSyncQuery = self.models.MatchSyncStatus.objects.using("default").filter(
            driver_object_uuid=OuterRef("pk"),
            driver_object_type=BASE_DRIVER_STR
        )
        fixtures = (self.models.BaseBallFixture.objects.using("default").annotate(has_sync=Exists(matchSyncQuery))
                    .filter(vhost=self.vhost,updated_at__gte=self.last_timestamp,has_sync=True))
        fixtureList = await sync_to_async(lambda:list(fixtures),thread_sensitive=False)()
        await self.run_in_batches(fixtureList,self.process_baseball_fixture_score,self.max_workers,"baseball_fixtures_score")



    #-----------------------------------
    # Basketball
    #-----------------------------------
    async def process_basketball_fixture_score(self,fixture):
        sysLink = await self.find_sync_object("match",BBL_DRIVER_STR,fixture.uuid)
        if sysLink:
            if self.verbose:
                self.logger.info(f"Processing Basketball Fixture {fixture.uuid} Scores...")
            home_team = await sync_to_async(lambda: fixture.home_team, thread_sensitive=False)()
            away_team = await sync_to_async(lambda: fixture.away_team, thread_sensitive=False)()
            sys_home_team = await sync_to_async(lambda: sysLink.match.home_team, thread_sensitive=False)()
            sys_away_team = await sync_to_async(lambda: sysLink.match.away_team, thread_sensitive=False)()
            scores = self.models.BasketBallScore.objects.using("default").filter(vhost=self.vhost,fixture=fixture)
            home_score = await sync_to_async(lambda:scores.filter(team = home_team).first(),thread_sensitive=False)()
            away_score = await sync_to_async(lambda:scores.filter(team = away_team).first(),thread_sensitive=False)()
            outcomeObj = await self._create_outcome(sysLink.match,BBL_DRIVER_STR)
            outcomeObj.is_current = True
            finished = False
            if fixture.status in ["Finished","Postponed","After Over Time"]:
                finished = True
            outcomeObj.is_end_game = finished
            outcomeObj.status_short = fixture.status
            outcomeObj.status_long = fixture.status
            await sync_to_async(lambda: outcomeObj.save(), thread_sensitive=False)()
            if home_score and away_score:
                outcomeHomeTeamObj = await self._create_outcome_team(outcomeObj,sys_home_team,BBL_DRIVER_STR)
                outcomeAwayTeamObj = await self._create_outcome_team(outcomeObj, sys_away_team, BBL_DRIVER_STR)
                outcomeHomeTeamObj.score = home_score.score
                outcomeAwayTeamObj.score = away_score.score
                outcomeObj.last_home_score = home_score.score
                outcomeObj.last_away_score = away_score.score
                await sync_to_async(lambda: outcomeObj.save(), thread_sensitive=False)()
                await sync_to_async(lambda:outcomeHomeTeamObj.save(),thread_sensitive=False)()
                await sync_to_async(lambda:outcomeAwayTeamObj.save(),thread_sensitive=False)()
                for i in ["q1","q2","q3","q4","ot"]:
                    segScoreObj = await self._create_outcome_segment(outcomeObj,sys_home_team,i,BBL_DRIVER_STR)
                    segScoreObj.score = getattr(home_score,i)
                    await sync_to_async(lambda:segScoreObj.save(),thread_sensitive=False)()
                    segScoreObj = await self._create_outcome_segment(outcomeObj,sys_away_team,i,BBL_DRIVER_STR)
                    segScoreObj.score = getattr(away_score,i)
                    await sync_to_async(lambda:segScoreObj.save(),thread_sensitive=False)()
        # else:
        #     print(f"Nolink {fixture.uuid} fixture not found")

    async def process_basketball_fixtures(self):
        matchSyncQuery = self.models.MatchSyncStatus.objects.using("default").filter(
            driver_object_uuid=OuterRef("pk"),
            driver_object_type=BBL_DRIVER_STR
        )
        fixtures = (self.models.BasketBallFixture.objects.using("default").annotate(has_sync=Exists(matchSyncQuery))
                    .filter(vhost=self.vhost,updated_at__gte=self.last_timestamp,has_sync=True))
        fixtureList = await sync_to_async(lambda:list(fixtures),thread_sensitive=False)()
        await self.run_in_batches(fixtureList,self.process_basketball_fixture_score,self.max_workers,"basketball_fixtures_score")

    #-----------------------------------
    # Hockey
    #-----------------------------------
    async def process_hockey_fixture_score(self,fixture):
        sysLink = await self.find_sync_object("match",HOCK_DRIVER_STR,fixture.uuid)
        if sysLink:
            if self.verbose:
                self.logger.info(f"Processing Hockey Fixture {fixture.uuid} Scores...")
            home_team = await sync_to_async(lambda: fixture.home_team, thread_sensitive=False)()
            away_team = await sync_to_async(lambda: fixture.away_team, thread_sensitive=False)()
            sys_home_team = await sync_to_async(lambda: sysLink.match.home_team, thread_sensitive=False)()
            sys_away_team = await sync_to_async(lambda: sysLink.match.away_team, thread_sensitive=False)()
            scores = self.models.HockeyFixtureScore.objects.using("default").filter(vhost=self.vhost,fixture=fixture)
            home_score = await sync_to_async(lambda:scores.filter(team = home_team).first(),thread_sensitive=False)()
            away_score = await sync_to_async(lambda:scores.filter(team = away_team).first(),thread_sensitive=False)()
            outcomeObj = await self._create_outcome(sysLink.match,HOCK_DRIVER_STR)
            outcomeObj.is_current = True
            finished = True
            if fixture.status in ["Finished","Postponed","After Over Time","After Penalties","Not Started"]:
                finished = True
            outcomeObj.is_end_game = finished
            outcomeObj.status_short = fixture.status
            outcomeObj.status_long = fixture.status
            # await sync_to_async(lambda:print(outcomeObj.status_long,outcomeObj.is_end_game),thread_sensitive=False)()
            await sync_to_async(lambda: outcomeObj.save(), thread_sensitive=False)()
            if home_score and away_score:
                outcomeHomeTeamObj = await self._create_outcome_team(outcomeObj,sys_home_team,HOCK_DRIVER_STR)
                outcomeAwayTeamObj = await self._create_outcome_team(outcomeObj, sys_away_team, HOCK_DRIVER_STR)
                outcomeHomeTeamObj.score = home_score.score
                outcomeAwayTeamObj.score = away_score.score
                outcomeObj.last_home_score = home_score.score
                outcomeObj.last_away_score = away_score.score
                await sync_to_async(lambda: outcomeObj.save(), thread_sensitive=False)()
                await sync_to_async(lambda:outcomeHomeTeamObj.save(),thread_sensitive=False)()
                await sync_to_async(lambda:outcomeAwayTeamObj.save(),thread_sensitive=False)()
        # else:
        #     print(f"Nolink {fixture.uuid} fixture not found")

    async def process_hockey_fixtures(self):
        matchSyncQuery = self.models.MatchSyncStatus.objects.using("default").filter(
            driver_object_uuid=OuterRef("pk"),
            driver_object_type=HOCK_DRIVER_STR
        )
        fixtures = (self.models.HockeyFixture.objects.using("default").annotate(has_sync=Exists(matchSyncQuery))
                    .filter(vhost=self.vhost,updated_at__gte=self.last_timestamp,has_sync=True))
        fixtureList = await sync_to_async(lambda:list(fixtures),thread_sensitive=False)()
        await self.run_in_batches(fixtureList,self.process_hockey_fixture_score,self.max_workers,"hockey_fixtures_score")


    #-----------------------------------
    # Tennis
    #-----------------------------------
    async def process_tennis_fixture_score(self, fixture):
        sysLink = await self.find_sync_object("match", TEN_DRIVER_STR, fixture.uuid)
        if not sysLink:
            if self.verbose:
                self.logger.warning(f"Fixture {fixture.uuid} not linked to a system match.")
            return None

        if self.verbose:
            self.logger.info(f"Processing Tennis Fixture {fixture.uuid} Scores...")

        # GoalServe "Teams"
        home_team = await sync_to_async(lambda: fixture.home_team, thread_sensitive=False)()
        away_team = await sync_to_async(lambda: fixture.away_team, thread_sensitive=False)()

        # System teams
        sys_home_team = await sync_to_async(lambda: sysLink.match.home_team, thread_sensitive=False)()
        sys_away_team = await sync_to_async(lambda: sysLink.match.away_team, thread_sensitive=False)()

        # Driver links
        sys_home_team_link = await self.find_sync_object("team", TEAM_DRIVER_STR, False, system_obj=sys_home_team)
        sys_away_team_link = await self.find_sync_object("team", TEAM_DRIVER_STR, False, system_obj=sys_away_team)
        manual_override = False
        flipped = None

        if sys_home_team_link and getattr(sys_home_team_link, "manual_entry", False):
            manual_override = True
            flipped = False  # sys_home == GoalServe home_team

        if sys_away_team_link and getattr(sys_away_team_link, "manual_entry", False):
            manual_override = True
            flipped = True  # sys_away == GoalServe home_team
        if not sys_home_team_link or not sys_away_team_link:
            if self.verbose:
                self.logger.warning(f"Fixture {fixture.uuid}: team links not found.")
            return None

        # --- Normalize names for matching ---
        sys_home_name = await sync_to_async(lambda: self._normalize_name(getattr(sys_home_team, "name", "")),
                                            thread_sensitive=False)()
        sys_away_name = await sync_to_async(lambda: self._normalize_name(getattr(sys_away_team, "name", "")),
                                            thread_sensitive=False)()
        home_name = await sync_to_async(lambda: self._normalize_name(getattr(home_team, "name", "")),
                                        thread_sensitive=False)()
        away_name = await sync_to_async(lambda: self._normalize_name(getattr(away_team, "name", "")),
                                        thread_sensitive=False)()

        # --- DEBUG logging ---
        if self.verbose:
            self.logger.info(
                f"[DEBUG] Fixture {fixture.uuid} name mapping:"
                f"\n  home_team: {home_name}"
                f"\n  away_team: {away_name}"
                f"\n  sys_home_team: {sys_home_name}"
                f"\n  sys_away_team: {sys_away_name}"
            )
        if (
                sys_home_team_link and sys_away_team_link and
                sys_home_team_link.manual_entry and sys_away_team_link.manual_entry
        ):
            self.logger.warning(
                f"[GOALSERVE-TENNIS-DUAL-MANUAL] Fixture {fixture.uuid}"
            )
        if manual_override:
            home_team_canonical = sys_home_team if not flipped else sys_away_team
            away_team_canonical = sys_away_team if not flipped else sys_home_team

            if self.verbose:
                self.logger.info(
                    f"[GOALSERVE-TENNIS-MANUAL] Fixture {fixture.uuid} "
                    f"home={home_team_canonical.uuid} "
                    f"away={away_team_canonical.uuid} "
                    f"flipped={flipped}"
                )

        else:
            # --- RapidFuzz two-way matching ---
            sim_home_home = fuzz.partial_ratio(sys_home_name, home_name)
            sim_home_away = fuzz.partial_ratio(sys_home_name, away_name)
            sim_away_home = fuzz.partial_ratio(sys_away_name, home_name)
            sim_away_away = fuzz.partial_ratio(sys_away_name, away_name)

            mappingA_score = sim_home_home + sim_away_away
            mappingB_score = sim_home_away + sim_away_home

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

                self.logger.warning(
                    f"[GOALSERVE-TENNIS-FUZZY-AMBIGUOUS] Fixture {fixture.uuid}"
                )

        if self.verbose:
            self.logger.info(
                f"[DEBUG] Fixture {fixture.uuid} canonical mapping:"
                f"\n  home_team_canonical: {home_team_canonical.uuid}"
                f"\n  away_team_canonical: {away_team_canonical.uuid}"
                f"\n  flipped: {flipped}"
                f"\n  sim_scores: HH:{sim_home_home}, HA:{sim_home_away} AH:{sim_away_home}, AA:{sim_away_away}"
                f"\n  mapping_scores: A:{mappingA_score}, B:{mappingB_score}"
            )

        # --- Scores ---
        scores = self.models.TennisScore.objects.using("default").filter(vhost=self.vhost, fixture=fixture)
        home_score = await sync_to_async(lambda: scores.filter(team=home_team).first(), thread_sensitive=False)()
        away_score = await sync_to_async(lambda: scores.filter(team=away_team).first(), thread_sensitive=False)()

        outcomeObj = await self._create_outcome(sysLink.match, TEN_DRIVER_STR)
        outcomeObj.is_current = True
        finished = fixture.status in ["Finished", "Cancelled", "Retired", "Not Started", "Walk Over"]
        outcomeObj.is_end_game = finished
        outcomeObj.status_short = fixture.status
        outcomeObj.status_long = fixture.status
        await sync_to_async(lambda: outcomeObj.save(), thread_sensitive=False)()

        if home_score and away_score:
            outcomeHomeTeamObj = await self._create_outcome_team(outcomeObj, home_team_canonical, TEN_DRIVER_STR)
            outcomeAwayTeamObj = await self._create_outcome_team(outcomeObj, away_team_canonical, TEN_DRIVER_STR)

            if not flipped or flipped is None:
                outcomeHomeTeamObj.score = home_score.score
                outcomeAwayTeamObj.score = away_score.score
                outcomeObj.last_home_score = home_score.score
                outcomeObj.last_away_score = away_score.score
            else:
                outcomeHomeTeamObj.score = away_score.score
                outcomeAwayTeamObj.score = home_score.score
                outcomeObj.last_home_score = away_score.score
                outcomeObj.last_away_score = home_score.score

            await sync_to_async(lambda: outcomeHomeTeamObj.save(), thread_sensitive=False)()
            await sync_to_async(lambda: outcomeAwayTeamObj.save(), thread_sensitive=False)()
            await sync_to_async(lambda: outcomeObj.save(), thread_sensitive=False)()
            if self.debug:
                self.logger.info(
                    f"[DEBUG] Tennis Fixture {fixture.uuid} processed: "
                    f"first_score={home_score.score}, second_score={away_score.score}, finished={finished}"
                )
            # --- Per-segment scores ---
            for i in ["s1", "s2", "s3", "s4", "s5", "game_score", "serve", "winner"]:
                segHome = await self._create_outcome_segment(outcomeObj, home_team_canonical, i, TEN_DRIVER_STR)
                segAway = await self._create_outcome_segment(outcomeObj, away_team_canonical, i, TEN_DRIVER_STR)
                if not flipped or flipped is None:
                    segHome.score = getattr(home_score, i)
                    segAway.score = getattr(away_score, i)
                else:
                    segHome.score = getattr(away_score, i)
                    segAway.score = getattr(home_score, i)
                await sync_to_async(lambda: segHome.save(), thread_sensitive=False)()
                await sync_to_async(lambda: segAway.save(), thread_sensitive=False)()

    async def process_tennis_fixtures(self):
        matchSyncQuery = self.models.MatchSyncStatus.objects.using("default").filter(
            driver_object_uuid=OuterRef("pk"),
            driver_object_type=TEN_DRIVER_STR
        )
        fixtures = (self.models.TennisFixture.objects.using("default").annotate(has_sync=Exists(matchSyncQuery))
                    .filter(vhost=self.vhost,updated_at__gte=self.last_timestamp,has_sync=True))
        fixtureList = await sync_to_async(lambda:list(fixtures),thread_sensitive=False)()
        await self.run_in_batches(fixtureList,self.process_tennis_fixture_score,self.max_workers,"tennis_fixtures_score")



    async def _work_cycle(self):
        await asyncio.gather(
           self.process_soccer_fixtures(),
           self.process_american_fixtures(),
           self.process_baseball_fixtures(),
           self.process_basketball_fixtures(),
           self.process_hockey_fixtures(),
            self.process_tennis_fixtures(),
            return_exceptions=True
        )
        self.last_timestamp = now()

        # print("Eat at Joes!")
        self.logger.info(f"GoalServe ScoreD Worker Tick!")

