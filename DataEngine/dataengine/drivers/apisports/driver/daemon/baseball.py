import asyncio
from datetime import datetime, timedelta
from time import localtime
from types import SimpleNamespace

import httpx
import pytz
from asgiref.sync import sync_to_async
from django.conf import settings
from django.db import IntegrityError, connections, close_old_connections
from django.utils import timezone
from django.utils.timezone import localdate, now

from asynctools.abc import AsyncWorkerABC



class APISportsBaseballAsync(AsyncWorkerABC):
    url_root = "https://v1.baseball.api-sports.io/"
    regappid = "dataengine.drivers.apisports"
    last_timestamp = False
    _midnight_task = False
    def __init__(self, vhost = object ,logger = object, name: str = "worker", interval: float = 120,run_in_process: bool = False,loki_url=None,):
        AsyncWorkerABC.__init__(self,vhost, logger, name, interval,run_in_process,loki_url)
        if not self.run_in_process:
            self._child_init()
    def _child_init(self):
        """
        Runs inside the forked child *after* django.setup().
        Safe place for model imports.
        """
        super()._child_init()
        from dataengine.drivers.apisports.models import Season, Team, Player, League, \
            TeamLeagues,  PlayerStats, BASEGameScore, BASEGame, BASEGameScoreSummary
        from parameters.models import Timezone, VHostParameterRegistry
        from dataengine.drivers.apisports.driver.toolkit import get_api_sports_session, getLogger, \
            get_league_active_season, \
            aget_league_active_season
        self.get_api_sports_session = get_api_sports_session
        self.getLogger = getLogger
        self.get_league_active_season = get_league_active_season
        self.aget_league_active_season = aget_league_active_season
        self.last_timestamp = localtime()
        self.models = SimpleNamespace(
            Team=Team,
            Season=Season,
            Player=Player,
            League=League,
            TeamLeagues=TeamLeagues,
            PlayerStats=PlayerStats,
            BASEGameScore=BASEGameScore,
            BASEGame=BASEGame,
            BASEGameScoreSummary=BASEGameScoreSummary,
            Timezone=Timezone,
            VHostParameterRegistry=VHostParameterRegistry,

        )
    async def _create_team(self, team, leagueObj):
        if "id" and "name" in team:
            teamObj, created = await sync_to_async(lambda:self.models.Team.objects.using("default").get_or_create(id=team["id"], sport_mask="base", vhost=self.vhost),thread_sensitive=False)()
            if created:
                await sync_to_async(lambda:teamObj.save(),thread_sensitive=False)()
            teamObj.name = team["name"]
            teamObj.logo = team["logo"]
            teamObj.country_name = team["country"]["name"]
            teamObj.country_code = team["country"]["code"]
            teamObj.flag = team["country"]["flag"]
            if "city" in team:
                teamObj.city = team["city"]
            if "owner" in team:
                teamObj.owner = team["owner"]
            if "established" in team:
                teamObj.established = team["established"]
            if "stadium" in team:
                teamObj.stadium = team["stadium"]
            await sync_to_async(lambda:teamObj.save(),thread_sensitive=False)()
            self.logger.info(f"Created/updated Team {teamObj.name}...")
            teamLeagueObj, cc = await sync_to_async(lambda:self.models.TeamLeagues.objects.using("default").get_or_create(league=leagueObj, team=teamObj, sport_mask="base",
                                                                  vhost=self.vhost),thread_sensitive=False)()
            await sync_to_async(lambda:teamLeagueObj.save(),thread_sensitive=False)()

    async def get_games_worker(self, date, league_id, match_id=False):
        if not match_id:
            if not date: date = datetime.now()
            self.logger.info(f"Games Worker for {league_id}/{date}")
        else:
            self.logger.info(f"Games Worker for Match {match_id}")
        # Step one: Seasons:
        self.logger.info(f"Getting Games from API.")
        leagueObj = await sync_to_async(lambda:self.models.League.objects.using("default").get(id=league_id, sport_mask="base", vhost=self.vhost),thread_sensitive=False)()
        if leagueObj.season_override:
            seasonStr = leagueObj.season_override
            seasonObj,cc = await sync_to_async(lambda:self.models.Season.objects.using("default").get_or_create(vhost=self.vhost,season_key=seasonStr),thread_sensitive=False)()
            if cc:
                await sync_to_async(lambda:seasonObj.save(),thread_sensitive=False)()

        else:
            season, seasonObj = await self.aget_league_active_season(leagueObj.seasons, self.vhost)

            if not season:
                self.logger.warning(f"League {leagueObj.name} has no active season: Not continuing.")
                return False
            if leagueObj.needs_plusone:
                seasonStr = seasonObj.get_season_key_full()
            else:
                seasonStr = seasonObj.season_key
        if not match_id:
            url = f"{self.url_root}games?league={leagueObj.id}&season={seasonStr}&date={date}&timezone={settings.TIME_ZONE}"
        else:
            url = f"{self.url_root}games?id={match_id}&timezone={settings.TIME_ZONE}"
        self.logger.info(url)
        # print(url)
        response = await self._fetch_with_retry(url)
        if not response: return False
        if response.status_code == 200:
            data = response.json()
            # print(url)
            # print(data)
            for game in data["response"]:
                # print(game)
                try:
                    home_team = await sync_to_async(lambda:self.models.Team.objects.using("default").get(id=game["teams"]["home"]["id"], sport_mask="base",
                                                 vhost=self.vhost),thread_sensitive=False)()
                except self.models.Team.DoesNotExist:
                    self.logger.warning(
                        f'Team not found: HT: {game["teams"]["home"]["id"]}/{game["teams"]["home"]["name"]} - Creating!')
                    home_team, cc = await sync_to_async(lambda:self.models.Team.objects.using("default").get_or_create(id=game["teams"]["home"]["id"], sport_mask="base",
                                                               vhost=self.vhost),thread_sensitive=False)()
                    home_team.name = game["teams"]["home"]["name"]
                    await sync_to_async(lambda:home_team.save(),thread_sensitive=False)()
                    await self.get_teams(game["teams"]["home"]["id"], leagueObj.id)
                    tcc, cc = await sync_to_async(lambda:self.models.TeamLeagues.objects.using("default").get_or_create(team=home_team, league=leagueObj, vhost=self.vhost),thread_sensitive=False)()
                    await sync_to_async(lambda:tcc.save(),thread_sensitive=False)()
                try:
                    away_team = await sync_to_async(lambda:self.models.Team.objects.using("default").get(id=game["teams"]["away"]["id"], sport_mask="base",
                                                 vhost=self.vhost),thread_sensitive=False)()
                except self.models.Team.DoesNotExist:
                    away_team, cc = await sync_to_async(lambda:self.models.Team.objects.using("default").get_or_create(id=game["teams"]["away"]["id"], sport_mask="base",
                                                               vhost=self.vhost),thread_sensitive=False)()
                    away_team.name = game["teams"]["away"]["name"]
                    await sync_to_async(lambda:away_team.save(),thread_sensitive=False)()
                    await self.get_teams(game["teams"]["away"]["id"], leagueObj.id)
                    tcc, cc = await sync_to_async(lambda:self.models.TeamLeagues.objects.using("default").get_or_create(team=away_team, league=leagueObj, vhost=self.vhost),thread_sensitive=False)()
                    await sync_to_async(lambda:tcc.save(),thread_sensitive=False)()

                if home_team and away_team:
                    home_score_sum = 0
                    away_score_sum = 0
                    if not match_id:
                        BASEGameObj,cc = await sync_to_async(lambda:self.models.BASEGame.objects.using("default").get_or_create(id=game["id"], league=leagueObj, season=seasonObj,
                                                           vhost=self.vhost),thread_sensitive=False)()
                        if cc:
                            await sync_to_async(lambda:BASEGameObj.save(),thread_sensitive=False)()
                    else:
                        BASEGameObj = await sync_to_async(lambda:self.models.BASEGame.objects.using("default").get(id=match_id, vhost=self.vhost),thread_sensitive=False)()
                    # print(game)

                    data_map = {
                        # "stage": game["stage"],
                        "week": game["week"],
                        "commence_time": datetime.fromisoformat(game["date"]),
                        # "venue": game["venue"],
                        # "city": game["venue"]["city"],
                        "status_short": game["status"]["short"],
                        "status_long": game["status"]["long"],
                        # "status_timer": game["status"]["timer"],
                        "home_team": home_team,
                        "away_team": away_team,
                        "league": leagueObj, }
                    if "timer" in game["status"]:
                        data_map["status_timer"] = game["status"]["timer"]
                    for k, v in data_map.items():
                        setattr(BASEGameObj, k, v)
                    await sync_to_async(lambda:BASEGameObj.save(),thread_sensitive=False)()
                    try:
                        BASEGameHomeScoreObj = await sync_to_async(lambda:self.models.BASEGameScore.objects.using("default").get(match=BASEGameObj, team=home_team,
                                                                         vhost=self.vhost),thread_sensitive=False)()
                    except self.models.BASEGameScore.DoesNotExist:
                        BASEGameHomeScoreObj = self.models.BASEGameScore(match=BASEGameObj, team=home_team, vhost=self.vhost)
                    inning_keys = range(1, 10)
                    ht = 0
                    at = 0
                    for ik in inning_keys:
                        ht += game["scores"]["home"]["innings"].get(str(ik), 0) or 0
                        at += game["scores"]["away"]["innings"].get(str(ik), 0) or 0
                    data_map = {
                        "inning_1": game["scores"]["home"]["innings"]["1"],
                        "inning_2": game["scores"]["home"]["innings"]["2"],
                        "inning_3": game["scores"]["home"]["innings"]["3"],
                        "inning_4": game["scores"]["home"]["innings"]["4"],
                        "inning_5": game["scores"]["home"]["innings"]["5"],
                        "inning_6": game["scores"]["home"]["innings"]["6"],
                        "inning_7": game["scores"]["home"]["innings"]["7"],
                        "inning_8": game["scores"]["home"]["innings"]["8"],
                        "inning_9": game["scores"]["home"]["innings"]["9"],
                        "extra": game["scores"]["home"]["innings"]["extra"],
                        "hits": game["scores"]["home"]["hits"],
                        "errors": game["scores"]["home"]["errors"],
                        "total": ht,

                    }
                    home_score_sum = ht
                    for k, v in data_map.items():
                        setattr(BASEGameHomeScoreObj, k, v)
                    try:
                        BASEGameAwayScoreObj = await sync_to_async(lambda:self.models.BASEGameScore.objects.using("default").get(match=BASEGameObj, team=away_team,
                                                                         vhost=self.vhost),thread_sensitive=False)()
                    except self.models.BASEGameScore.DoesNotExist:
                        BASEGameAwayScoreObj = self.models.BASEGameScore(match=BASEGameObj, team=away_team, vhost=self.vhost)
                    data_map = {
                        "inning_1": game["scores"]["away"]["innings"]["1"],
                        "inning_2": game["scores"]["away"]["innings"]["2"],
                        "inning_3": game["scores"]["away"]["innings"]["3"],
                        "inning_4": game["scores"]["away"]["innings"]["4"],
                        "inning_5": game["scores"]["away"]["innings"]["5"],
                        "inning_6": game["scores"]["away"]["innings"]["6"],
                        "inning_7": game["scores"]["away"]["innings"]["7"],
                        "inning_8": game["scores"]["away"]["innings"]["8"],
                        "inning_9": game["scores"]["away"]["innings"]["9"],
                        "extra": game["scores"]["away"]["innings"]["extra"],
                        "hits": game["scores"]["away"]["hits"],
                        "errors": game["scores"]["away"]["errors"],
                        "total": at,

                    }
                    away_score_sum = at
                    for k, v in data_map.items():
                        setattr(BASEGameAwayScoreObj, k, v)
                    sys_event = False
                    sys_link = False
                    await sync_to_async(lambda:BASEGameAwayScoreObj.save(),thread_sensitive=False)()
                    await sync_to_async(lambda:BASEGameHomeScoreObj.save(),thread_sensitive=False)()
                    if home_score_sum != 0 or away_score_sum != 0:
                        hsObj, _ = await sync_to_async(
                            lambda: self.models.BASEGameScoreSummary.objects.using("default").get_or_create(vhost=self.vhost,
                                                                                match=BASEGameObj,
                                                                                team=BASEGameObj.home_team),
                            thread_sensitive=False)()
                        hsObj.score = home_score_sum
                        await sync_to_async(lambda: hsObj.save(), thread_sensitive=False)()
                        asObj, _ = await sync_to_async(
                            lambda: self.models.BASEGameScoreSummary.objects.using("default").get_or_create(vhost=self.vhost,
                                                                                match=BASEGameObj,
                                                                                team=BASEGameObj.away_team),
                            thread_sensitive=False)()
                        asObj.score = away_score_sum
                        await sync_to_async(lambda: asObj.save(), thread_sensitive=False)()

    async def get_teams(self,team_id=False, league_id=False):
        # Step one: Seasons:
        self.logger.info(f"Getting Teams from API Sports.")
        if not league_id:
            _leagueObj = self.models.League.objects.using("default").filter(active=True, sport_mask="bab",vhost=self.vhost).order_by("-id")
        else:
            _leagueObj = self.models.League.objects.using("default").filter(active=True, sport_mask="bab", id=league_id,vhost=self.vhost).order_by("-id")
        acount = await sync_to_async(lambda:_leagueObj.acount(),thread_sensitive=False)()
        if acount < 1:
            self.logger.warning(
                "There are no Active League objects with a BAB sports mask. Not fetching anything. This is probably -not- what you wanted.")
        _leagueObj = await sync_to_async(list,thread_sensitive=False)(_leagueObj)
        for leagueObj in _leagueObj:
            # print(leagueObj)
            # print(leagueObj.seasons)
            season, seasonObj = await self.aget_league_active_season(leagueObj.seasons,self.vhost)
            if not season:
                self.logger.warning(f"League {leagueObj.name} has no active season: Not continuing.")
                # return False
                continue
            if leagueObj.needs_plusone:
                season_key = seasonObj.get_season_key_full()
            else:
                season_key = seasonObj.season_key
            url = f"{self.url_root}teams?league={leagueObj.id}&season={season_key}"
            if team_id:
                url += f"&id={team_id}"
            self.logger.info(url)
            response = await self._fetch_with_retry(url)
            if not response: return False
            if response.status_code == 200:
                data = response.json()
                for team in data["response"]:
                    # print(team)
                    await self._create_team(team, leagueObj)


    async def get_leagues(self,arg=False):
        # Step one: Seasons:
        self.logger.info(f"Getting seasons from API Sports.")
        url = f"{self.url_root}/leagues"
        response = await self._fetch_with_retry(url)
        if not response: return False
        if response.status_code == 200:

            data = response.json()
            for league in data["response"]:
                # print(league)
                leagueObj,cc = await sync_to_async(lambda:self.models.League.objects.using("default").get_or_create(id=league["id"],sport_mask="base",vhost=self.vhost),thread_sensitive=False)()
                if cc:
                    await sync_to_async(lambda:leagueObj.save(),thread_sensitive=False)()
                leagueObj.name = league["name"]
                leagueObj.logo = league["logo"]
                leagueObj.sport_mask = "base"
                leagueObj.country_name = league["country"]["name"]
                if league["country"]["code"] != None:
                    leagueObj.country_code = league["country"]["code"]
                else:
                    leagueObj.country_code = league["country"]["id"]
                leagueObj.flag = league["country"]["flag"]
                leagueObj.seasons = league["seasons"]
                await sync_to_async(lambda:leagueObj.save(),thread_sensitive=False)()
                self.logger.info(f"Created/updated League {leagueObj.name}... (Currently inactive)")

    async def get_games(self, **kwargs):
        self.logger.warning("Getting Games from API.")
        date = datetime.now().strftime("%Y-%m-%d")

        # load BASE leagues
        _leagueObj = self.models.League.objects.using("default").filter(
            active=True, sport_mask="base", vhost=self.vhost
        )

        count = await sync_to_async(lambda: _leagueObj.count(), thread_sensitive=False)()
        if count < 1:
            self.logger.warning(
                "There are no Active League objects with a BASE sports mask. "
                "Not fetching anything. This is probably -not- what you wanted."
            )

        _leagueObj = await sync_to_async(list, thread_sensitive=False)(_leagueObj)

        # ------------------------------------------------
        # Build list of (date_str, league_id) tasks
        # ------------------------------------------------
        tasks = []

        for leagueObj in _leagueObj:
            if "date_start" not in kwargs:
                # single-day mode
                date_str = datetime.now().strftime("%Y-%m-%d")
                tasks.append((date_str, leagueObj.id))
            else:
                # multi-day mode
                date_start = datetime.strptime(kwargs["date_start"], "%Y-%m-%d")
                date_end = datetime.strptime(kwargs["date_stop"], "%Y-%m-%d")

                current_date = date_start
                while current_date < date_end:
                    tasks.append((current_date.strftime("%Y-%m-%d"), leagueObj.id))
                    current_date += timedelta(days=1)

        # ------------------------------------------------
        # Handler for each (date, league) item
        # ------------------------------------------------
        async def fetch_handler(item):
            date_str, league_id = item
            await asyncio.sleep(1)
            return await self.get_games_worker(date_str, league_id)

        # ------------------------------------------------
        # Run with batching — force 20-thread concurrency
        # ------------------------------------------------
        self.MAX_WORKERS = 20

        await self.run_in_batches(
            tasks,
            handler=fetch_handler,
            batch_size=20,
            label="get_games_base"
        )

    async def _midnight_loop(self):
        """Independent loop waiting until midnight."""
        while not self._shutdown_event.is_set():
            wait_seconds = await self._seconds_until_midnight()
            self.logger.info(f"Sleeping {wait_seconds:.2f}s until midnight...")
            try:
                await asyncio.wait_for(self._shutdown_event.wait(), timeout=wait_seconds)
                if self._shutdown_event.is_set():
                    break
            except asyncio.TimeoutError:
                pass

            try:
                await self.get_leagues()
            except Exception as e:
                self.logger.exception(f"Error in midnight job: {e}")



    def setup_loop(self):
        """
        Called once before the main loop begins.
        Starts the midnight loop in the background so it doesn't block continuous work.
        """
        if getattr(self, "_midnight_task", None) is not None:
            return

        loop_fn = type(self)._midnight_loop  # ← unbound function
        self._midnight_task = asyncio.create_task(loop_fn(self))

        self.logger.info("Midnight loop started in background.")

    async def _do_midnight_work(self):
        self.logger.info("[Midnight Loop]: Updating leagues...")
        await self.get_leagues()

    async def setup(self):
        if not self._midnight_task or self._midnight_task.done():
            self._midnight_task = asyncio.create_task(self._midnight_loop())
            self.logger.info("Midnight loop started in background.")



    async def _cleanup(self):
        """Ensure midnight loop stops gracefully on shutdown."""
        if self._midnight_task and not self._midnight_task.done():
            self._midnight_task.cancel()
            try:
                await self._midnight_task
            except asyncio.CancelledError:
                pass
        await super()._cleanup()



    async def _work_cycle(self):
        if not self.last_timestamp:
            self.last_timestamp = localtime()
        yesterday = now() - timedelta(days=1)
        tomorrow = now() + timedelta(days=1)
        start = yesterday.strftime("%Y-%m-%d")
        stop = tomorrow.strftime("%Y-%m-%d")
        await asyncio.gather(
            self.get_games(date_start=start, date_stop=stop),
            return_exceptions=True
        )
        self.last_timestamp = localtime()
        self.logger.info(f"APISPorts/Base Worker Tick!")
        #await sync_to_async(lambda:close_old_connections(),thread_sensitive=True)()

    async def _run(self):
        self.setup_loop()
        await AsyncWorkerABC._run(self)

    async def start(self):
        apiSettings, created = await sync_to_async(lambda:self.models.VHostParameterRegistry.objects.using("default").get_or_create(vhost=self.vhost, application=self.regappid,
                                                                            name="api_key_str"),thread_sensitive=False)()
        headers = {"x-rapidapi-key": f"{apiSettings.value_text}"}
        self.client = httpx.AsyncClient(headers=headers,limits=self.httpx_limits,timeout=self.httpx_timeout)
        await AsyncWorkerABC.start(self)