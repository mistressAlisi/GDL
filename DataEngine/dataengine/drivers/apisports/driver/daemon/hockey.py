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



class APISportsHockeyAsync(AsyncWorkerABC):
    url_root = "https://v1.hockey.api-sports.io/"
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
        from dataengine.drivers.apisports.models import Team, League, TeamLeagues, HOCKGame, HOCKGameScore, \
            HOCKGameScoreSummary
        from dataengine.models import MatchSyncStatus
        from dataengine.drivers.apisports.driver.toolkit import get_api_sports_session, getLogger, \
            get_league_active_season, \
            aget_league_active_season
        self.get_api_sports_session = get_api_sports_session
        self.getLogger = getLogger
        self.get_league_active_season = get_league_active_season
        self.aget_league_active_season = aget_league_active_season
        from parameters.models import Timezone, VHostParameterRegistry
        self.last_timestamp = localtime()
        self.models = SimpleNamespace(
            Team=Team,
            HOCKGame=HOCKGame,
            HOCKGameScore=HOCKGameScore,
            League=League,
            TeamLeagues=TeamLeagues,
            HOCKGameScoreSummary=HOCKGameScoreSummary,
            Timezone=Timezone,
            VHostParameterRegistry=VHostParameterRegistry,
            MatchSyncStatus=MatchSyncStatus

        )

    async def get_leagues(self,arg=False):
        # Step one: Seasons:
        self.logger.info(f"Getting seasons from API Sports.")
        url = f"{self.url_root}leagues"
        response = await self._fetch_with_retry(url)
        if not response: return False
        if response.status_code == 200:
            data = response.json()
            for league in data["response"]:
                # print(league)
                leagueObj,_ = await sync_to_async(lambda:self.models.League.objects.using("default").get_or_create(id=league["id"], sport_mask="hock",vhost=self.vhost),thread_sensitive=False)()
                leagueObj.name = league["name"]
                leagueObj.logo = league["logo"]
                leagueObj.sport_mask = "hock"
                leagueObj.country_name = league["country"]["name"]
                if league["country"]["code"] != None:
                    leagueObj.country_code = league["country"]["code"]
                else:
                    leagueObj.country_code = league["country"]["id"]
                # leagueObj.flag = league["country"]["flag"]
                leagueObj.seasons = league["seasons"]
                await sync_to_async(lambda:leagueObj.save(),thread_sensitive=False)()
                self.logger.info(f"Created/updated League {leagueObj.name}... (Currently inactive)")


    async def _create_team(self,team, leagueObj):
        if "id" and "name" in team:
            teamObj, created = await sync_to_async(lambda:self.models.Team.objects.using("default").get_or_create(id=team["id"], sport_mask="hock",vhost=self.vhost),thread_sensitive=False)()
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
            if "arena" in team:
                teamObj.stadium = team["arena"]
            await sync_to_async(lambda:teamObj.save(),thread_sensitive=False)()
            self.logger.info(f"Created/updated Team {teamObj.name}")
            teamLeagueObj, cc = await sync_to_async(lambda:self.models.TeamLeagues.objects.using("default").get_or_create(league=leagueObj, team=teamObj, sport_mask="hock",vhost=self.vhost),thread_sensitive=False)()
            await sync_to_async(lambda:teamLeagueObj.save(),thread_sensitive=False)()

    async def get_teams(self, team_id=False, league_id=False):
        # Step one: Seasons:
        self.logger.info(f"Getting Teams from API Sports.")
        if not league_id:
            _leagueObj = self.models.League.objects.using("default").filter(active=True, sport_mask="hock", vhost=self.vhost).order_by("-id")
        else:
            _leagueObj = self.models.League.objects.using("default").filter(active=True, sport_mask="hock", id=league_id, vhost=self.vhost).order_by(
                "-id")
        if await sync_to_async(lambda:_leagueObj.count(),thread_sensitive=False)() < 1:
            self.logger.warning(
                "There are no Active League objects with a HOCK sports mask. Not fetching anything. This is probably -not- what you wanted.")
            return False
        _leagueObj = await sync_to_async(list,thread_sensitive=False)(_leagueObj)
        for leagueObj in _leagueObj:
            self.logger.info(f"Processing League: {leagueObj.id}/{leagueObj.name}")
            seasons = await sync_to_async(lambda:leagueObj.seasons,thread_sensitive=False)()
            if leagueObj.season_override:
                seasonStr = leagueObj.season_override
                seasonObj, cc = await sync_to_async(
                    lambda: self.models.Season.objects.using("default").get_or_create(vhost=self.vhost,
                                                                                      season_key=seasonStr),
                    thread_sensitive=False)()
                if cc:
                    await sync_to_async(lambda: seasonObj.save(), thread_sensitive=False)()

            else:
                season, seasonObj = await self.aget_league_active_season(leagueObj.seasons, self.vhost)

                if not season:
                    self.logger.warning(f"League {leagueObj.name} has no active season: Not continuing.")
                    return False
                if leagueObj.needs_plusone:
                    seasonStr = seasonObj.get_season_key_full()
                else:
                    seasonStr = seasonObj.season_key
            url = f"{self.url_root}teams?league={leagueObj.id}&season={seasonStr}"
            if team_id:
                url += f"&id={team_id}"
            # self.logger.info(url)
            response = await self._fetch_with_retry(url)
            if not response: return False
            if response.status_code == 200:
                data = response.json()
                # print(data)
                for team in data["response"]:
                    # print(team)
                    await self._create_team(team, leagueObj)

    async def get_games_worker(self, date, league_id, match_id=False):
        if not match_id:
            if not date: date = datetime.now()
            self.logger.info(f"Games Worker for {league_id}/{date}")
        else:
            self.logger.info(f"Games Worker for Match {match_id}")
        # Step one: Seasons:
        self.logger.info(f"Getting Games from API.")
        leagueObj = await sync_to_async(lambda:self.models.League.objects.using("default").get(id=league_id, sport_mask="hock", vhost=self.vhost),thread_sensitive=False)()
        seasons = await sync_to_async(lambda:leagueObj.seasons,thread_sensitive=False)()
        season, seasonObj = await self.aget_league_active_season(seasons, self.vhost)
        if not season:
            self.logger.warning(f"League {leagueObj.name} has no active season: Not continuing.")
        else:
            self.logger.warning(f"Processing League {leagueObj.name}")

            if leagueObj.needs_plusone:
                ssr = seasonObj.get_season_key_full()
            else:
                ssr = seasonObj.season_key
            if not match_id:
                url = f"{self.url_root}games?league={leagueObj.id}&season={ssr}&date={date}&timezone={settings.TIME_ZONE}"


            else:
                url = f"{self.url_root}/games?id={match_id}"
            response = await self._fetch_with_retry(url)
            if not response: return False
            if response.status_code == 200:
                data = response.json()
                # print(url)
                # print(data)
                for game in data["response"]:
                    # print(game)
                    try:
                        home_team = await sync_to_async(lambda:self.models.Team.objects.using("default").get(id=game["teams"]["home"]["id"], sport_mask="hock",
                                                     vhost=self.vhost),thread_sensitive=False)()
                    except self.models.Team.DoesNotExist:
                        self.logger.warning(
                            f'Team not found: HT: {game["teams"]["home"]["id"]}/{game["teams"]["home"]["name"]} - Creating!')
                        home_team = await self.get_teams(game["teams"]["home"]["id"], league_id)
                        #home_team = await sync_to_async(lambda:Team.objects.using("default").get(id=game["teams"]["home"]["id"], sport_mask="hock",
                        #                             vhost=self.vhost),thread_sensitive=False)()
                    try:
                        away_team = await sync_to_async(lambda:self.models.Team.objects.using("default").get(id=game["teams"]["away"]["id"], sport_mask="hock",
                                                     vhost=self.vhost),thread_sensitive=False)()
                    except self.models.Team.DoesNotExist:
                        self.logger.warning(
                            f'Team not found: AT: {game["teams"]["away"]["id"]}/{game["teams"]["away"]["name"]} - Creating!')
                        away_team = await self.get_teams(game["teams"]["away"]["id"], league_id)
                        # away_team = await sync_to_async(lambda:Team.objects.using("default").get(id=game["teams"]["away"]["id"], sport_mask="hock",
                        #                             vhost=self.vhost),thread_sensitive=False)()

                    if home_team and away_team:
                        home_score_sum = 0
                        away_score_sum = 0
                        if not match_id:
                            HOCKGameObj,cc = await sync_to_async(lambda:self.models.HOCKGame.objects.using("default").get_or_create(id=game["id"], season=seasonObj,vhost=self.vhost),thread_sensitive=False)()
                        else:
                            HOCKGameObj = await sync_to_async(lambda:self.models.HOCKGame.objects.using("default").get(id=match_id),thread_sensitive=False)()

                        data_map = {
                            # "stage": game["stage"],
                            "week": game["week"],
                            "commence_time": datetime.fromisoformat(game["date"]),
                            # "venue": game["venue"],
                            # "city": game["venue"]["city"],
                            "status_short": game["status"]["short"],
                            "status_long": game["status"]["long"],
                            # "status_timer": game["time"],
                            "home_team": home_team,
                            "away_team": away_team,
                            "league": leagueObj,
                        }
                        if "time" in game["status"]:
                            data_map["status_timer"] = game["status"]["time"]
                        for k, v in data_map.items():
                            setattr(HOCKGameObj, k, v)
                        await sync_to_async(lambda:HOCKGameObj.save(),thread_sensitive=False)()
                        if game["periods"]["first"]:
                            period_1 = game["periods"]["first"].split("-")
                        else:
                            period_1 = [0, 0]
                        if game["periods"]["second"]:
                            period_2 = game["periods"]["second"].split("-")
                        else:
                            period_2 = [0, 0]
                        if game["periods"]["third"]:
                            period_3 = game["periods"]["third"].split("-")
                        else:
                            period_3 = [0, 0]
                        if game["periods"]["overtime"]:
                            overtime = game["periods"]["overtime"].split("-")
                        else:
                            overtime = [0, 0]
                        if game['periods']['penalties']:
                            penalties = game['periods']['penalties'].split("-")
                        else:
                            penalties = [0, 0]
                        try:
                            HOCKGameHomeScoreObj = await sync_to_async(lambda:self.models.HOCKGameScore.objects.using("default").get(match=HOCKGameObj, team=home_team,
                                                                             vhost=self.vhost),thread_sensitive=False)()
                        except self.models.HOCKGameScore.DoesNotExist:
                            HOCKGameHomeScoreObj = self.models.HOCKGameScore(match=HOCKGameObj, team=home_team, vhost=self.vhost)
                        data_map = {
                            "first": int(period_1[0]),
                            "second": int(period_2[0]),
                            "third": int(period_3[0]),
                            "overtime": int(overtime[0]),
                            "penalties": int(penalties[0]),
                            "total": int(period_1[0]) + int(period_2[0]) + int(period_3[0]) + int(overtime[0]),

                        }
                        for k, v in data_map.items():
                            setattr(HOCKGameHomeScoreObj, k, v)
                        try:
                            HOCKGameAwayScoreObj = await sync_to_async(lambda:self.models.HOCKGameScore.objects.using("default").get(match=HOCKGameObj, team=away_team,
                                                                             vhost=self.vhost),thread_sensitive=False)()
                        except self.models.HOCKGameScore.DoesNotExist:
                            HOCKGameAwayScoreObj = self.models.HOCKGameScore(match=HOCKGameObj, team=away_team, vhost=self.vhost)
                        data_map = {
                            "first": int(period_1[1]),
                            "second": int(period_2[1]),
                            "third": int(period_3[1]),
                            "overtime": int(overtime[1]),
                            "penalties": int(penalties[1]),
                            "total": int(period_1[1]) + int(period_2[1]) + int(period_3[1]) + int(overtime[1]),

                        }
                        for k, v in data_map.items():
                            setattr(HOCKGameAwayScoreObj, k, v)
                        sys_event = False
                        sys_link = False
                        await sync_to_async(lambda:HOCKGameAwayScoreObj.save(),thread_sensitive=False)()
                        await sync_to_async(lambda:HOCKGameHomeScoreObj.save(),thread_sensitive=False)()
                        if home_score_sum != 0 or away_score_sum != 0:
                            hsObj, _ = await sync_to_async(
                                lambda: self.models.HOCKGameScoreSummary.objects.using("default").get_or_create(vhost=self.vhost,
                                                                                    match=HOCKGameObj,
                                                                                    team=HOCKGameObj.home_team),
                                thread_sensitive=False)()
                            hsObj.score = home_score_sum
                            await sync_to_async(lambda: hsObj.save(), thread_sensitive=False)()
                            asObj, _ = await sync_to_async(
                                lambda: self.models.HOCKGameScoreSummary.objects.using("default").get_or_create(vhost=self.vhost,
                                                                                    match=HOCKGameObj,
                                                                                    team=HOCKGameObj.away_team),
                                thread_sensitive=False)()
                            asObj.score = away_score_sum
                            await sync_to_async(lambda: asObj.save(), thread_sensitive=False)()
                        self.logger.info(f"HOCKEY fixture update complete")

    async def get_games(self, **kwargs):
        self.logger.warning("Getting Games from API.")
        date = datetime.now().strftime("%Y-%m-%d")

        # load HOCK leagues
        _leagueObj = self.models.League.objects.using("default").filter(
            active=True, sport_mask="hock", vhost=self.vhost
        )

        count = await sync_to_async(lambda: _leagueObj.count(), thread_sensitive=False)()
        if count < 1:
            self.logger.warning(
                "There are no Active League objects with a HOCK sports mask. "
                "Not fetching anything. This is probably -not- what you wanted."
            )
            return False

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
        # Per-item handler
        # ------------------------------------------------
        async def fetch_handler(item):
            date_str, league_id = item
            await asyncio.sleep(1)
            return await self.get_games_worker(date_str, league_id)

        # ------------------------------------------------
        # Execute batches with 20-worker concurrency
        # ------------------------------------------------
        self.MAX_WORKERS = 20

        await self.run_in_batches(
            tasks,
            handler=fetch_handler,
            batch_size=20,
            label="get_games_hock"
        )
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

    async def _midnight_loop(self):
        """Independent loop waiting until midnight."""
        while not self._shutdown_event.is_set():
            wait_seconds = await self._seconds_until_midnight()
            self.logger.info(f"[Midnight Loop] Sleeping {wait_seconds:.2f}s until midnight...")
            try:
                await asyncio.wait_for(self._shutdown_event.wait(), timeout=wait_seconds)
                if self._shutdown_event.is_set():
                    break
            except asyncio.TimeoutError:
                pass

            try:
                await self._do_midnight_work()
            except Exception as e:
                self.logger.exception(f"[Midnight Loop] Error in midnight job: {e}")


    async def _do_midnight_work(self):
        self.logger.info("[Midnight Loop]: Updating leagues...")
        await self.get_leagues()


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
        #await sync_to_async(lambda:close_old_connections(),thread_sensitive=True)()
        self.logger.info(f"APISPorts/Hockey Worker Tick!")

    async def _run(self):
        self.setup_loop()
        await AsyncWorkerABC._run(self)

    async def start(self):
        apiSettings, created = await  sync_to_async(lambda:self.models.VHostParameterRegistry.objects.using("default").get_or_create(vhost=self.vhost, application=self.regappid,
                                                                            name="api_key_str"),thread_sensitive=False)()
        headers = {"x-rapidapi-key": f"{apiSettings.value_text}"}
        self.client = httpx.AsyncClient(headers=headers,limits=self.httpx_limits,timeout=self.httpx_timeout)
        await AsyncWorkerABC.start(self)