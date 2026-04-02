import asyncio
from datetime import datetime, timedelta
from time import localtime
from types import SimpleNamespace
from unittest.util import three_way_cmp

import httpx
import pytz
from asgiref.sync import sync_to_async
from django.conf import settings
from django.db import IntegrityError, connections, close_old_connections
from django.utils import timezone
from django.utils.timezone import localdate, now

from asynctools.abc import AsyncWorkerABC



class APISportsBasketballAsync(AsyncWorkerABC):
    url_root = "https://v1.basketball.api-sports.io/"
    regappid = "dataengine.drivers.apisports"
    last_timestamp = False
    _midnight_task = False
    def __init__(self, vhost = object ,logger = object, name: str = "worker", interval: float = 180,run_in_process: bool = False,loki_url=None,):
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
            TeamLeagues, PlayerStats,  BABGame, BABGamePlayerStats, BABGameScore, \
            BABGameScoreSummary
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
            Season=Season,
            Player=Player,
            League=League,
            TeamLeagues=TeamLeagues,
            PlayerStats=PlayerStats,
            BABGameScore=BABGameScore,
            BABGame=BABGame,
            BABGamePlayerStats=BABGamePlayerStats,
            BABGameScoreSummary=BABGameScoreSummary,
            Timezone=Timezone,
            VHostParameterRegistry=VHostParameterRegistry,

        )
    async def _create_team(self,team, leagueObj):
        if "id" and "name" in team:
            teamObj, created = await sync_to_async(lambda:self.models.Team.objects.using("default").get_or_create(id=team["id"], sport_mask="bab",vhost=self.vhost),thread_sensitive=False)()
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
            self.logger.info(f"Created/updated Team {teamObj.name}... Adding to system")
            teamLeagueObj, cc = await sync_to_async(lambda:self.models.TeamLeagues.objects.using("default").get_or_create(league=leagueObj, team=teamObj, sport_mask="bab",vhost=self.vhost),thread_sensitive=False)()
            await sync_to_async(lambda:teamLeagueObj.save(),thread_sensitive=False)()


    async def get_games_stats_worker(self,bab_id):
        self.logger.info(f"Game Stats Worker for {bab_id}")
        babObj = await sync_to_async(lambda:self.models.BABGame.objects.using("default").get(id=bab_id),thread_sensitive=False)()
        count = 0
        url = f"{self.url_root}/games/statistics/players?id={babObj.id}&timezone={settings.TIME_ZONE}"
        response = await self._fetch_with_retry(url)
        if not response: return False
        season, seasonObj = await self.aget_league_active_season(babObj.league.seasons,self.vhost)
        if response.status_code == 200:
            data = response.json()
            # print(data)
            for game in data["response"]:
                try:
                    team = await sync_to_async(lambda:self.models.Team.objects.using("default").get(id=game["team"]["id"], sport_mask="bab",vhost=self.vhost),thread_sensitive=False)()
                except self.models.Team.MultipleObjectsReturned:
                    team = await sync_to_async(lambda:self.models.Team.objects.using("default").filter(id=game["team"]["id"], sport_mask="bab",vhost=self.vhost).first(),thread_sensitive=False)()
                    self.logger.warning(f"Multiple objects returned for Team {game['team']['id']}: Picking 1st one: {team}")
                if "groups" in game:
                    for group in game["groups"]:
                        group_name = group["name"]
                        for player in group["players"]:
                            if player["player"]["id"] != "":
                                try:
                                    playerObj = await sync_to_async(lambda:self.models.Player.objects.using("default").get(id=int(player["player"]["id"])),thread_sensitive=False)()
                                except self.models.Player.DoesNotExist:
                                    playerObj = self.models.Player(id=int(player["player"]["id"]), name=player['player']["name"],
                                                       image=player['player']["image"], team=team, season=seasonObj,
                                                       group=group_name,vhost=self.vhost)
                                    await sync_to_async(lambda:playerObj.save(),thread_sensitive=False)()
                                except IntegrityError as e:
                                    self.logger.error(
                                        f"Integrity Error inside get_game_stats_worker: {e}. Player Name={player['player']['name']}, ID={player['player']['id']}")
                                    playerObj = False
                                if playerObj:
                                    for stat in player["statistics"]:
                                        statObj,cc = sync_to_async(lambda:self.models.BABGamePlayerStats.objects.using("default").get_or_create(player=playerObj, season=seasonObj,
                                                                                 group=group_name, name=stat["name"],
                                                                                 bab_game=babObj,vhost=self.vhost),thread_sensitive=False)()
                                        statObj.value = stat["value"]
                                        await sync_to_async(lambda:statObj.save(),thread_sensitive=False)()

    async def get_games_worker(self,date, league_id, match_id=False, bkg=False):
        if not match_id:
            if not date: date = datetime.now()
            self.logger.info(f"Games Worker for {league_id}/{date}")
        else:
            self.logger.info(f"Games Worker for Match {match_id}")
        # Step one: Seasons:
        self.logger.info(f"Getting Games from API.")
        leagueObj = await sync_to_async(lambda:self.models.League.objects.using("default").get(id=league_id, sport_mask="bab",vhost=self.vhost),thread_sensitive=False)()
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
        response = await self._fetch_with_retry(url)
        if not response: return False
        if response.status_code == 200:
            data = response.json()
            # print(url)
            # print(data)
            self.logger.info(f"Got {len(data)} games from API.")
            for game in data["response"]:
                try:
                    home_team = await sync_to_async(lambda:self.models.Team.objects.using("default").get(id=game["teams"]["home"]["id"], sport_mask="bab",vhost=self.vhost),thread_sensitive=False)()
                except self.models.Team.DoesNotExist:
                    self.logger.warning(
                        f'Team not found: HT: {game["teams"]["home"]["id"]}/{game["teams"]["home"]["name"]} - Creating!')
                    home_team = await self.get_teams(game["teams"]["home"]["id"], leagueObj.id)
                     # await sync_to_async(lambda:Team.objects.using("default").get(id=game["teams"]["home"]["id"], sport_mask="bab",vhost=self.vhost),thread_sensitive=False)()
                try:
                    away_team = await sync_to_async(lambda:self.models.Team.objects.using("default").get(id=game["teams"]["away"]["id"], sport_mask="bab",vhost=self.vhost),thread_sensitive=False)()
                except self.models.Team.DoesNotExist:
                    self.logger.warning(
                        f'Team not found: AT: {game["teams"]["away"]["id"]}/{game["teams"]["away"]["name"]} - Creating!')
                    away_team = await self.get_teams(game["teams"]["away"]["id"], leagueObj.id)
                     # await sync_to_async(lambda:Team.objects.using("default").get(id=game["teams"]["away"]["id"], sport_mask="bab",vhost=self.vhost),thread_sensitive=False)()

                if home_team and away_team:
                    home_score_sum = 0
                    away_score_sum = 0
                    if not match_id:
                        BABGameObj,_ = await sync_to_async(lambda:self.models.BABGame.objects.using("default").get_or_create(id=game["id"], league=leagueObj, season=seasonObj,vhost=self.vhost),thread_sensitive=False)()
                    else:
                        BABGameObj = await sync_to_async(lambda:self.models.BABGame.objects.using("default").get(id=match_id,vhost=self.vhost),thread_sensitive=False)()

                    data_map = {"stage": game["stage"],
                                "week": game["week"],
                                "commence_time": datetime.fromisoformat(game["date"]),
                                # "venue": game["venue"],
                                # "city": game["venue"]["city"],
                                "status_short": game["status"]["short"],
                                "status_long": game["status"]["long"],
                                # "status_timer": game["status"]["timer"],
                                "home_team": home_team,
                                "away_team": away_team, }
                    if "timer" in game["status"]:
                        data_map["status_timer"] = game["status"]["timer"]
                    for k, v in data_map.items():
                        setattr(BABGameObj, k, v)

                    await sync_to_async(lambda:BABGameObj.save(),thread_sensitive=False)()
                    try:
                        BABGameHomeScoreObj = await sync_to_async(lambda:self.models.BABGameScore.objects.using("default").get(match=BABGameObj, team=home_team,vhost=self.vhost),thread_sensitive=False)()
                    except self.models.BABGameScore.DoesNotExist:
                        BABGameHomeScoreObj = self.models.BABGameScore(match=BABGameObj, team=home_team,vhost=self.vhost)
                    data_map = {
                        "quarter_1": game["scores"]["home"]["quarter_1"],
                        "quarter_2": game["scores"]["home"]["quarter_2"],
                        "quarter_3": game["scores"]["home"]["quarter_3"],
                        "quarter_4": game["scores"]["home"]["quarter_4"],
                        "overtime": game["scores"]["home"]["over_time"],
                        "total": game["scores"]["home"]["total"]
                    }
                    home_score_sum = game["scores"]["home"]["total"]
                    for k, v in data_map.items():
                        setattr(BABGameHomeScoreObj, k, v)
                    try:
                        BABGameAwayScoreObj = await sync_to_async(lambda:self.models.BABGameScore.objects.using("default").get(match=BABGameObj, team=away_team,vhost=self.vhost),thread_sensitive=False)()
                    except self.models.BABGameScore.DoesNotExist:
                        BABGameAwayScoreObj = self.models.BABGameScore(match=BABGameObj, team=away_team,vhost=self.vhost)
                    data_map = {
                        "quarter_1": game["scores"]["away"]["quarter_1"],
                        "quarter_2": game["scores"]["away"]["quarter_2"],
                        "quarter_3": game["scores"]["away"]["quarter_3"],
                        "quarter_4": game["scores"]["away"]["quarter_4"],
                        "overtime": game["scores"]["away"]["over_time"],
                        "total": game["scores"]["away"]["total"]
                    }
                    away_score_sum = game["scores"]["away"]["total"]
                    for k, v in data_map.items():
                        setattr(BABGameAwayScoreObj, k, v)
                    buuid = await sync_to_async(lambda:BABGameObj.uuid,thread_sensitive=False)()

                    await sync_to_async(lambda:BABGameAwayScoreObj.save(),thread_sensitive=False)()
                    await sync_to_async(lambda:BABGameHomeScoreObj.save(),thread_sensitive=False)()
                    # print(f"Updated Scores {home_score_sum}/{away_score_sum} {game["scores"]["home"]["total"]}/{game["scores"]["away"]["total"]}")
                    if home_score_sum != 0 or away_score_sum != 0:
                        self.logger.info(f"BAB Fixture Summaries: Home Score: {home_score_sum}, Away Score: {away_score_sum}")
                        hsObj,_ = await sync_to_async(lambda:self.models.BABGameScoreSummary.objects.using("default").get_or_create(vhost=self.vhost,match=BABGameObj,team=BABGameObj.home_team),thread_sensitive=False)()
                        hsObj.score = home_score_sum
                        await sync_to_async(lambda:hsObj.save(),thread_sensitive=False)()
                        asObj,_ = await sync_to_async(lambda:self.models.BABGameScoreSummary.objects.using("default").get_or_create(vhost=self.vhost,match=BABGameObj,team=BABGameObj.away_team),thread_sensitive=False)()
                        asObj.score = away_score_sum
                        await sync_to_async(lambda:asObj.save(),thread_sensitive=False)()
                    self.logger.info(f"Finished updating BAB Fixture: {buuid}")
            self.logger.warning(f"League {leagueObj.name} was updated!")

    async def get_player_worker(self,team_id):
        teamObj = await sync_to_async(lambda:self.models.Team.objects.using("default").get(id=team_id,sport_mask="bab",vhost=self.vhost),thread_sensitive=False)()
        teamLeagueObj = await sync_to_async(lambda:self.models.TeamLeagues.objects.using("default").filter(team=teamObj,vhost=self.vhost).first(),thread_sensitive=False)()
        seasons = await sync_to_async(lambda:teamLeagueObj.league.seasons,thread_sensitive=False)()
        season, seasonObj = await self.aget_league_active_season(seasons,self.vhost)
        if not season: return False
        url = f"{self.url_root}players?team={teamObj.id}&season={seasonObj.season_key}"
        response = await self._fetch_with_retry(url)
        if not response: return False
        if response.status_code == 200:
            data = response.json()
            for player in data["response"]:
                if "id" and "name" in player:
                    try:
                        playerObj = await sync_to_async(lambda:self.models.Player.objects.using("default").get(id=player["id"],vhost=self.vhost),thread_sensitive=False)()
                    except self.models.Player.DoesNotExist:
                        playerObj = self.models.Player(id=player["id"], team=teamObj, season=seasonObj,vhost=self.vhost)
                        await sync_to_async(lambda:playerObj.save(),thread_sensitive=False)()
                    for k in player:
                        setattr(playerObj, k, player[k])
                    await sync_to_async(lambda:playerObj.save(),thread_sensitive=False)()
                    self.logger.info(f"Created/updated Player {playerObj.name}...")
            teamObj.need_sync_players = False
            await sync_to_async(lambda:teamObj.save(),thread_sensitive=False)()

    async def get_player_stats_worker(self,player_id, season_key):
        # Step one: Seasons:
        seasonObj = await sync_to_async(lambda:self.models.Season.objects.using("default").get(season_key=season_key,vhost=self.vhost),thread_sensitive=False)()
        playerObj = await sync_to_async(lambda:self.models.Player.objects.using("default").get(id=player_id,vhost=self.vhost),thread_sensitive=False)()
        count = 0
        url = f"{self.url_root}players/statistics?id={playerObj.id}&season={seasonObj.season_key}&timezone={settings.TIME_ZONE}"
        response = await self._fetch_with_retry(url)
        if not response: return False
        if response.status_code == 200:
            _data = response.json()
            for data in _data["response"]:
                for team in data["teams"]:
                    group_data = team["groups"][0]
                    # print(group_data)
                    for stat in group_data["statistics"]:
                        # print(stat)
                        try:
                            playerStatsObj = await sync_to_async(lambda:self.models.PlayerStats.objects.using("default").get(player=playerObj, season=seasonObj,vhost=self.vhost,
                                                                     group=group_data["name"], name=stat["name"]),thread_sensitive=False)()
                        except self.models.PlayerStats.DoesNotExist:
                            playerStatsObj = self.models.PlayerStats(player=playerObj, season=seasonObj, group=group_data["name"],
                                                         name=stat["name"],vhost=self.vhost)
                        playerStatsObj.value = stat["value"]
                        await sync_to_async(lambda:playerStatsObj.save(),thread_sensitive=False)()
                        count += 1
            playerObj.need_sync_player_stats = False
            await sync_to_async(lambda:playerObj.save(),thread_sensitive=False)()
            self.logger.info(f"Created/updated Player {playerObj.name}: {count} stats.")

    async def get_teams(self,team_id=False, league_id=False):
        # Step one: Seasons:
        last_team = None
        self.logger.info(f"Getting Teams from API Sports.")
        if not league_id:
            _leagueObj = self.models.League.objects.using("default").filter(active=True, sport_mask="bab",vhost=self.vhost).order_by("-id")
        else:
            _leagueObj = self.models.League.objects.using("default").filter(active=True, sport_mask="bab", id=league_id,vhost=self.vhost).order_by("-id")

        if (await sync_to_async(lambda:_leagueObj.count(),thread_sensitive=False)() < 1):
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
                    last_team = await self._create_team(team, leagueObj)
        if team_id:
            return last_team


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
                leagueObj,_ = await sync_to_async(lambda:self.models.League.objects.using("default").get_or_create(id=league["id"],sport_mask="bab",vhost=self.vhost),thread_sensitive=False)()
                leagueObj.name = league["name"]
                leagueObj.logo = league["logo"]
                leagueObj.sport_mask = "bab"
                leagueObj.country_name = league["country"]["name"]
                if league["country"]["code"] != None:
                    leagueObj.country_code = league["country"]["code"]
                else:
                    leagueObj.country_code = league["country"]["id"]
                leagueObj.flag = league["country"]["flag"]
                leagueObj.seasons = league["seasons"]
                await sync_to_async(lambda:leagueObj.save(),thread_sensitive=False)()
                self.logger.info(f"Created/updated League {leagueObj.name}... (Currently inactive)")

    async def get_players(self,team_id=False):
        if team_id:
            teams = self.models.Team.objects.using("default").filter(id=team_id, sport_mask="bab",vhost=self.vhost)
        else:
            teams = self.models.Team.objects.using("default").filter(sport_mask="bab",vhost=self.vhost)
        teams = await sync_to_async(list,thread_sensitive=False)(teams)
        for team in teams:
            await self.get_player_worker(team.id)

    async def get_games(self, **kwargs):
        self.logger.warning("Getting Games from API.")
        date = datetime.now().strftime("%Y-%m-%d")

        # load leagues
        _leagueObj = self.models.League.objects.using("default").filter(
            active=True, sport_mask="bab", vhost=self.vhost
        )

        count = await sync_to_async(lambda: _leagueObj.count(), thread_sensitive=False)()
        if count < 1:
            self.logger.warning(
                "There are no Active League objects with a BAB sports mask. "
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
        # Handler invoked by batching system
        # ------------------------------------------------
        async def fetch_handler(item):
            date_str, league_id = item
            await asyncio.sleep(1)
            return await self.get_games_worker(date_str, league_id)

        # ------------------------------------------------
        # Run with batching — using 20 threads
        # ------------------------------------------------
        # override concurrency for this run
        self.MAX_WORKERS = 20

        await self.run_in_batches(
            tasks,
            handler=fetch_handler,
            batch_size=15,  # can adjust if needed
            label="get_games"
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
            try:
                await self._do_midnight_work()
            except Exception as e:
                self.logger.exception(f"[Midnight Loop] Error in midnight job: {e}")
            wait_seconds = await self._seconds_until_midnight()
            self.logger.info(f"[Midnight Loop] Sleeping {wait_seconds:.2f}s until midnight...")
            try:
                await asyncio.wait_for(self._shutdown_event.wait(), timeout=wait_seconds)
                if self._shutdown_event.is_set():
                    break
            except asyncio.TimeoutError:
                pass



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
        self.logger.info(f"APISPorts/Basketball Worker Tick!")

    async def _run(self):
        self.setup_loop()
        await AsyncWorkerABC._run(self)

    async def start(self):
        apiSettings, created = await  sync_to_async(lambda:self.models.VHostParameterRegistry.objects.using("default").get_or_create(vhost=self.vhost, application=self.regappid,
                                                                            name="api_key_str"),thread_sensitive=False)()
        headers = {"x-rapidapi-key": f"{apiSettings.value_text}"}
        self.client = httpx.AsyncClient(headers=headers,limits=self.httpx_limits,timeout=self.httpx_timeout)
        await AsyncWorkerABC.start(self)