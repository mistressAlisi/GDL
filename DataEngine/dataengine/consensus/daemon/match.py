
from datetime import timedelta
from types import SimpleNamespace
from asgiref.sync import sync_to_async, async_to_sync

from django.db.models import Q, Exists, OuterRef, Func, Value, F

from django.utils.timezone import localtime, localdate, now


from asynctools.abc import AsyncWorkerABC


APISPORTS_GAMETYPE_MAP = {
    "BK": "bab",
    "BB": "base",
    "IH": "hock",
    "AF": "amf",
    "SC": "fball",
}

GOALSERVE_GAMETYPE_MAP = {
    "BK": "basketballfixture",
    "BB": "baseballfixture",
    "IH": "hockgame",
    "AF": "amfgame",
    "SC": "soccerfixture",
    "TN":"TennisFixture"
}

class AsyncMatchLinkDaemon(AsyncWorkerABC):
    verbose = False
    verbose_tn = False
    def __init__(self, vhost=None, logger=None, name: str = "MatchLinkD", interval: float = 120,
                 run_in_process: bool = True,loki_url=None,):
        AsyncWorkerABC.__init__(self, vhost, logger, name, interval, run_in_process, loki_url)
    def _child_init(self):
        """
        Runs inside the forked child *after* django.setup().
        Safe place for model imports.
        """
        super()._child_init()
        from dataengine.drivers.kiblio.models import Fixture
        from dataengine.models import MatchSyncStatus, TeamSyncStatus
        from matches.models import Match
        from dataengine.drivers.apitennis.models.fixtures import Fixture as APITennisFixture
        from dataengine.drivers.apisports.models.basketball import BABGame as APISportsBABGame
        from dataengine.drivers.apisports.models.baseball import BASEGame as APISportsBASEGame
        from dataengine.drivers.apisports.models.hockey import HOCKGame as APISportsHOCKGame
        from dataengine.drivers.apisports.models.football import FBALLGame as APISportsFBALLGame
        from dataengine.drivers.apisports.models.american_football import AMFGame as APISportsAMFGame
        from dataengine.drivers.goalserve.models.tennis import TennisFixture as GoalServeTennisFixture
        from dataengine.drivers.goalserve.models.basketball import BasketBallFixture as GoalServeBasketBallFixture
        from dataengine.drivers.goalserve.models.baseball import BaseBallFixture as GoalServeBaseballFixture
        from dataengine.drivers.goalserve.models.hockey import HockeyFixture as GoalServeHockeyFixture
        from dataengine.drivers.goalserve.models.soccer import SoccerFixture as GoalServeSoccerFixture
        from dataengine.drivers.goalserve.models.american import AmericanFBallFixture as GoalServeAmericanFBallFixture

        self.last_timestamp = localtime()
        self.models = SimpleNamespace(
            Fixture=Fixture,
            MatchSyncStatus=MatchSyncStatus,
            TeamSyncStatus=TeamSyncStatus,
            Match=Match,
            APITennisFixture=APITennisFixture,
            APISportsBABGame=APISportsBABGame,
            APISportsBASEGame=APISportsBASEGame,
            APISportsHOCKGame=APISportsHOCKGame,
            APISportsFBALLGame=APISportsFBALLGame,
            APISportsAMFGame=APISportsAMFGame,
            GoalServeTennisFixture=GoalServeTennisFixture,
            GoalServeBasketBallFixture=GoalServeBasketBallFixture,
            GoalServeBaseballFixture=GoalServeBaseballFixture,
            GoalServeHockeyFixture=GoalServeHockeyFixture,
            GoalServeSoccerFixture=GoalServeSoccerFixture,
            GoalServeAmericanFBallFixture=GoalServeAmericanFBallFixture,

        )
        self.APISPORTS_MAP = {
            "BK": APISportsBABGame,
            "BB": APISportsBASEGame,
            "IH": APISportsHOCKGame,
            "AF": APISportsAMFGame,
            "SC": APISportsFBALLGame,
        }
        self.GOALSERVE_MAP = {
        "BK":GoalServeBasketBallFixture,
        "BB":GoalServeBaseballFixture,
        "IH":GoalServeHockeyFixture,
        "AF":GoalServeAmericanFBallFixture,
        "SC":GoalServeSoccerFixture,
        "TN":GoalServeTennisFixture
        }
    async def _get_team_links(self,matchObj,type,return_teams=False):
        home_team = await sync_to_async(lambda:matchObj.home_team,thread_sensitive=False)()
        away_team = await sync_to_async(lambda:matchObj.away_team,thread_sensitive=False)()
        home_links = []
        away_links = []
        home_team_links = await sync_to_async(lambda:list(self.models.TeamSyncStatus.objects.using("default").filter(team=home_team,driver_object_type=type)),thread_sensitive=False)()
        away_team_links = await sync_to_async(lambda:list(self.models.TeamSyncStatus.objects.using("default").filter(team=away_team,driver_object_type=type)),thread_sensitive=False)()
        for ht in home_team_links:
            home_links.append(ht.driver_object_uuid)
        for at in away_team_links:
            away_links.append(at.driver_object_uuid)
        if self.verbose:
            self.logger.info(f"For Match {matchObj.uuid}: Home Team is: {home_team.name} [{home_team.uuid}] / {away_team.name} [{away_team.uuid}]")
            self.logger.info(f"Driver Object Type: {type}")
            self.logger.info(f"Home Links: {home_team.name} [{home_team.uuid}]--->{home_links}")
            self.logger.info(f"Away Links: {away_team.name} [{away_team.uuid}]--->{away_links}")
        if not return_teams:
            return home_links, away_links
        else:
            return home_links, away_links, home_team, away_team

    async def _get_match_times(self,matchObj):
        if not matchObj.commence_time: return False,False,False
        lts = (matchObj.commence_time - timedelta(hours=1))
        hts = (matchObj.commence_time + timedelta(hours=1))
        return matchObj.commence_time, lts, hts

    async def match_link_sources(self,matchObj,**kwargs):
        sport_slug = await sync_to_async(lambda:matchObj.sport.group.slug,thread_sensitive=False)()
        # First, KIBL check:
        if matchObj.id:
            if not await self.find_sync_object("match","kiblio.fixture.Fixture",False,system_obj=matchObj):
                try:
                    kiblFixture = await sync_to_async(lambda: self.models.Fixture.objects.using("default").get(vhost=self.vhost,fixture_id=matchObj.id), thread_sensitive=False)()
                    await self.create_sync_object("match",matchObj,"kiblio.fixture.Fixture",kiblFixture.uuid)
                    if self.verbose:
                        self.logger.info(f"Fixture {matchObj.uuid} Linked to KIBL {matchObj.id}")
                except self.models.Fixture.DoesNotExist:
                    self.logger.warning(f"Fixture {matchObj.uuid} No KIBL data found.")
        # Depending on sport type, Link up:
        if sport_slug in self.APISPORTS_MAP:
            if not await self.find_sync_object("match", f"apisports.match.{APISPORTS_GAMETYPE_MAP[sport_slug]}game", False, system_obj=matchObj):
                if self.verbose:
                    self.logger.info(f"Linking {sport_slug} Match {matchObj.uuid} to APISports")
                home_team_links, away_team_links = await self._get_team_links(matchObj,'apisports.team.Team')
                commence_time,low_time,high_time = await self._get_match_times(matchObj)
                gameObjects = self.APISPORTS_MAP[sport_slug].objects.using("default").filter(vhost=self.vhost,commence_time__gte=low_time,commence_time__lte=high_time).filter(
                    Q(Q(home_team__uuid__in=home_team_links)&Q(away_team__uuid__in=away_team_links))|
                    Q(Q(away_team__uuid__in=home_team_links) & Q(home_team__uuid__in=away_team_links))
                )
                if await sync_to_async(gameObjects.count, thread_sensitive=False)() >= 1:
                    api_fix = await sync_to_async(gameObjects.first, thread_sensitive=False)()
                    await self.create_sync_object("match", matchObj, f"apisports.match.{APISPORTS_GAMETYPE_MAP[sport_slug]}game", api_fix.uuid)
                    if self.verbose:
                        self.logger.info(f"{sport_slug} APISPORTS Linker SUCCESS: {matchObj.uuid}")
        if sport_slug in self.GOALSERVE_MAP:
            if not await self.find_sync_object("match",f"goalserve.match{GOALSERVE_GAMETYPE_MAP[sport_slug]}", False, system_obj=matchObj):
                if self.verbose:
                    self.logger.info(f"Linking {sport_slug} Match {matchObj.uuid} to Goalserve")
                home_team_links, away_team_links = await self._get_team_links(matchObj, 'goalserve.team.Team')
                commence_time, low_time, high_time = await self._get_match_times(matchObj)
                # Tennis special dispensation for times:
                if sport_slug == "TN":
                    low_time = matchObj.commence_time - timedelta(hours=24)
                    high_time = matchObj.commence_time + timedelta(hours=48)
                gameObjects = self.GOALSERVE_MAP[sport_slug].objects.using("default").filter(vhost=self.vhost, commence_time__gte=low_time,
                                                                       commence_time__lte=high_time).filter(
                    Q(Q(home_team__uuid__in=home_team_links) & Q(away_team__uuid__in=away_team_links)) |
                    Q(Q(away_team__uuid__in=home_team_links) & Q(home_team__uuid__in=away_team_links))
                )
                if await sync_to_async(gameObjects.count, thread_sensitive=False)() >= 1:
                    if sport_slug == "TN":

                        _api_fix = await sync_to_async(lambda:list(gameObjects), thread_sensitive=False)()
                        for api_fix in _api_fix:
                            await self.create_sync_object("match", matchObj,
                                                          f"goalserve.match.{GOALSERVE_GAMETYPE_MAP[sport_slug]}",
                                                          api_fix.uuid)
                    else:
                        api_fix = await sync_to_async(gameObjects.first, thread_sensitive=False)()
                        await self.create_sync_object("match", matchObj,
                                                      f"goalserve.match.{GOALSERVE_GAMETYPE_MAP[sport_slug]}", api_fix.uuid)
                    if self.verbose:
                        self.logger.info(f"{sport_slug} GOALServe Linker SUCCESS: {matchObj.uuid}")
        # Finally; special dispensation for APITennis:
        if sport_slug == "TN":
            if not await self.find_sync_object("match", "apitennis.fixture.Fixture", False, system_obj=matchObj):
                if self.verbose_tn:
                    self.logger.info(f"APITennis Linker for {matchObj.uuid}")
                home_team_links = await sync_to_async(lambda:list(self.models.TeamSyncStatus.objects.filter(team=matchObj.home_team,
                                                                driver_object_type="apitennis.players.Players")),thread_sensitive=False)()
                away_team_links = await sync_to_async(lambda:list(self.models.TeamSyncStatus.objects.filter(team=matchObj.away_team,
                                                                driver_object_type="apitennis.players.Players")),thread_sensitive=False)()
                home_team_uuids = []
                away_team_uuids = []
                # print(home_team_links)
                # print(away_team_links)
                for home_team in home_team_links:
                    home_team_uuids.append(home_team.driver_object_uuid)
                for away_team in away_team_links:
                    away_team_uuids.append(away_team.driver_object_uuid)
                commence_low = matchObj.commence_time - timedelta(hours=24)
                commence_high = matchObj.commence_time + timedelta(hours=48)
                low_date = commence_low.date()
                low_time = commence_low.time()
                high_date = commence_high.date()
                high_time = commence_high.time()
                fixtureObj = self.models.APITennisFixture.objects.using("default").filter(
                     vhost=self.vhost
                ).filter(
                    Q(
                        # same day as lower bound
                        Q(event_date=low_date, event_time__gte=low_time)
                    ) |
                    Q(
                        # same day as upper bound
                        Q(event_date=high_date, event_time__lte=high_time)
                    ) |
                    Q(
                        # days strictly between
                        Q(event_date__gt=low_date, event_date__lt=high_date)
                    )
                ).filter(
                    Q(
                        Q(event_first_player__uuid__in=home_team_uuids) &
                        Q(event_second_player__uuid__in=away_team_uuids)
                    ) |
                    Q(
                        Q(event_second_player__uuid__in=home_team_uuids) &
                        Q(event_first_player__uuid__in=away_team_uuids)
                    )
                )
                # await sync_to_async(lambda:print(fixtureObj), thread_sensitive=False)()
                if await sync_to_async(fixtureObj.count, thread_sensitive=False)() >= 1:
                    fixtures = await sync_to_async(lambda:list(fixtureObj), thread_sensitive=False)()
                    for api_fix in fixtures:
                        await self.create_sync_object("match", matchObj,
                                                      f"apitennis.fixture.Fixture",
                                                      api_fix.uuid)
                    if self.verbose_tn:
                        self.logger.info(f"{sport_slug} APITennis Linker SUCCESS: {matchObj.uuid}")
                else:
                    if self.verbose_tn:
                        self.logger.info(f"{sport_slug} APITennis Linker Fail: {matchObj.uuid} CT: {commence_time},"
                                         f" Low Date: {low_date}, High Date: {high_date},"
                                         f" Low Time: {low_time}, High Time: {high_time},"
                                         f" Home Links: {home_team_links}, Away Links: {away_team_links}")
            else:
                if self.verbose_tn:
                    self.logger.info(f"{sport_slug} APITennis Linker : {matchObj.uuid} Is already linked.")
                        # self.logger.info(f"Home IDs: {home_team_links}")
                        # self.logger.info(f"Away IDs: {away_team_links}")


    async def _work_cycle(self):
        cutoff = now() - timedelta(days=10)
        cutoff_fut = now() + timedelta(days=3)
        matches = self.models.Match.objects.using("default").filter(vhost=self.vhost,  commence_time__gte=cutoff, commence_time__lte=cutoff_fut)
        matchObjects = await sync_to_async(list, thread_sensitive=False)(matches)

        # Link sources
        await self.run_in_batches(
            matchObjects,
            self.match_link_sources,
            batch_size=50,
            label="match_link_sources"
        )
        self.logger.info(f"{self.name} tick...")
