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




class APISportsAmericanFootballAsync(AsyncWorkerABC):
    url_root = "https://v1.american-football.api-sports.io/"
    regappid = "dataengine.drivers.apisports"
    last_timestamp = False
    _midnight_task = False
    def __init__(self, vhost = object ,logger = object, name: str = "worker", interval: float = 120,run_in_process: bool = False,loki_url=None):
        AsyncWorkerABC.__init__(self,vhost, logger, name, interval,run_in_process,loki_url)
        if not self.run_in_process:
            self._child_init()


    def _child_init(self):
        """
        Runs inside the forked child *after* django.setup().
        Safe place for model imports.
        """
        super()._child_init()
        from dataengine.drivers.apisports.models import Season, Team, Player, AMFGamePlayerStats, League, AMFGame, \
            AMFGameScore, \
            TeamLeagues, AMFGameEvent, PlayerStats, AMFGameScoreSummary
        from outcomes.models import OutcomeTeams
        from parameters.models import Timezone, VHostParameterRegistry
        from dataengine.drivers.apisports.driver.toolkit import get_api_sports_session, getLogger, \
            get_league_active_season, \
            aget_league_active_season
        self.last_timestamp = localtime()
        self.models = SimpleNamespace(
            Season=Season,
            Team=Team,
            Player=Player,
            AMFGamePlayerStats=AMFGamePlayerStats,
            League=League,
            AMFGame=AMFGame,
            AMFGameScore=AMFGameScore,
            TeamLeagues=TeamLeagues,
            AMFGameEvent=AMFGameEvent,
            PlayerStats=PlayerStats,
            AMFGameScoreSummary=AMFGameScoreSummary,
            OutcomeTeams=OutcomeTeams,
            Timezone=Timezone,
            VHostParameterRegistry=VHostParameterRegistry,
        )
        self.get_api_sports_session = get_api_sports_session
        self.getLogger = getLogger
        self.get_league_active_season = get_league_active_season
        self.aget_league_active_season = aget_league_active_season
    async def get_games_stats_worker(self,amf_id):
        r_url = f"{self.url_root}games/statistics/players?id={amf_id}&timezone={settings.TIME_ZONE}"
        data = await self._fetch_with_retry(r_url)
        if data:
            seasonObj = await sync_to_async(lambda:self.models.Season.objects.using("default").get(active=True),thread_sensitive=False)()
            amfObj = await sync_to_async(lambda:self.models.AMFGame.objects.using("default").get(active=True),thread_sensitive=False)()
            for game in data["response"]:
                team = await sync_to_async(lambda:self.models.Team.objects.using("default").filter(id=game["team"]["id"]).first(),thread_sensitive=False)()
                for group in game["groups"]:
                    group_name = group["name"]
                    for player in game["players"]:
                        if player["player"]["id"] != "":
                            try:
                                playerObj = await sync_to_async(lambda:self.models.Player.objects.using("default").get(id=int(player["player"]["id"]),vhost=self.vhost),thread_sensitive=False)()
                            except self.models.Player.DoesNotExist:
                                playerObj = self.models.Player(id=int(player["player"]["id"]), name=player['player']["name"],
                                                   image=player['player']["image"], team=team, season=seasonObj,
                                                   group=group_name, vhost=self.vhost)
                                await sync_to_async(lambda:playerObj.save(),thread_sensitive=False)()
                            except IntegrityError as e:
                                self.logger.error(f"Integrity Error inside get_game_stats_worker: {e}. Player Name={player['player']['name']}, ID={player['player']['id']}")
                                return False
                            for stat in player["statistics"]:
                                statObj,_ = await sync_to_async(lambda:self.models.AMFGamePlayerStats.objects.using("default").get_or_create(player=playerObj, season=seasonObj,
                                                                                   group=group_name, name=stat["name"],
                                                                                   amf_game=amfObj, vhost=self.vhost),thread_sensitive=False)()
                                statObj.value = stat["value"]
                                await sync_to_async(lambda:statObj.save(),thread_sensitive=False)()


    async def get_teams(self,team_id=None,league_id=None):
        self.logger.info(f"Getting Teams from API Sports.")
        if not league_id:
            _leagueObj = self.models.League.objects.using("default").filter(active=True, sport_mask="amf",vhost=self.vhost)
        else:
            _leagueObj = self.models.League.objects.using("default").filter(active=True, sport_mask="amf", id=league_id,vhost=self.vhost)
        if await _leagueObj.acount() < 1:
            self.logger.warning(
                "There are no Active League objects with an AMF sports mask. Not fetching anything. This is probably -not- what you wanted.")
            return False
        leagues = await sync_to_async(lambda: list(_leagueObj),thread_sensitive=False)()
        for leagueObj in leagues:
            seasons = await sync_to_async(lambda: list(leagueObj.seasons),thread_sensitive=False)()
            season,seasonObj = await self.aget_league_active_season(seasons,self.vhost)
            if not season:
                self.logger.warning(f"League {leagueObj.name} has no active season: Not continuing.")
                return False
            url = f"{self.url_root}teams?league={leagueObj.id}&season={seasonObj.season_key}"
            if team_id:
                url += f"&id={team_id}"
            response = await self._fetch_with_retry(url)
            if not response:
                return False
            data = response.json()

            for team in data['response']:
                teamObj, created = await sync_to_async(lambda:self.models.Team.objects.using("default").get_or_create(id=team["id"], sport_mask="amf", vhost=self.vhost),thread_sensitive=False)()
                if created:
                    await sync_to_async(lambda:teamObj.save(),thread_sensitive=False)()
                teamObj.name = team["name"]
                teamObj.logo = team["logo"]
                teamObj.country_name = team["country"]["name"]
                teamObj.country_code = team["country"]["code"]
                teamObj.flag = team["country"]["flag"]
                teamObj.city = team["city"]
                teamObj.owner = team["owner"]
                teamObj.established = team["established"]
                teamObj.stadium = team["stadium"]
                await sync_to_async(lambda:teamObj.save(),thread_sensitive=False)()
                self.logger.info(f"Created/updated Team {teamObj.name}... Adding to System (if necessary):")
                teamLeagueObj, cc = await sync_to_async(lambda:self.models.TeamLeagues.objects.using("default").get_or_create(league=leagueObj, team=teamObj,
                                                                      sport_mask="amf", vhost=self.vhost),thread_sensitive=False)()
                await sync_to_async(lambda:teamLeagueObj.save(),thread_sensitive=False)()

    async def get_leagues(self,arg=False):
        # Step one: Seasons:
        self.logger.info(f"Getting seasons from API Sports.")
        url = f"{self.url_root}leagues"
        response = await self._fetch_with_retry(url)
        if not response:
            return False
        data = response.json()
        if data:
            for league in data["response"]:
                leagueObj,_ = await sync_to_async(lambda:self.models.League.objects.using("default").get_or_create(id=league["league"]["id"], sport_mask="amf",vhost=self.vhost),thread_sensitive=False)()
                leagueObj.name = league["league"]["name"]
                leagueObj.logo = league["league"]["logo"]
                leagueObj.country_name = league["country"]["name"]
                leagueObj.country_code = league["country"]["code"]
                leagueObj.flag = league["country"]["flag"]
                leagueObj.seasons = league["seasons"]
                leagueObj.sport_mask = "amf"
                await sync_to_async(lambda:leagueObj.save(),thread_sensitive=False)()
                self.logger.info(f"Created/updated League {leagueObj.name}...")


    async def get_games_worker(self,date, league_id, match_id=False):
        if not match_id:
            if not date: date = datetime.now()
            self.logger.info(f"Games Worker for {league_id}/{date}")
        else:
            self.logger.info(f"Games Worker for Match {match_id}")
        # Step one: Seasons:
        self.logger.info(f"Getting Games from API.")

        try:
            leagueObj = await sync_to_async(lambda:self.models.League.objects.using("default").get(id=league_id, sport_mask="amf",vhost=self.vhost),thread_sensitive=False)()
        except self.models.League.DoesNotExist as e:
            self.logger.error(f"League ID {league_id} does not exist / Not found. Sport mask: AMF ")
            self.logger.error(f"This is Match ID {match_id}")
            raise e
        if leagueObj.season_override:
            seasonStr = leagueObj.season_override
            seasonObj,cc = await sync_to_async(lambda:self.models.Season.objects.using("default").get_or_create(vhost=self.vhost,season_key=seasonStr),thread_sensitive=False)()
            if cc:
                await sync_to_async(lambda:seasonObj.save(),thread_sensitive=False)()

        else:
            season, seasonObj = await self.aget_league_active_season(leagueObj.seasons,self.vhost)

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
        data = await self._fetch_with_retry(url)
        if not data:
            return False
        # print("A")
        # print(data.json())
        data = data.json()
        for game in data["response"]:
            # print(game)
            try:
                home_team = await sync_to_async(lambda:self.models.Team.objects.using("default").get(id=game["teams"]["home"]["id"], sport_mask="amf", vhost=self.vhost),thread_sensitive=False)()
            except self.models.Team.DoesNotExist:
                self.logger.warning(
                    f'Team not found: HT: {game["teams"]["home"]["id"]}/{game["teams"]["home"]["name"]} - Creating in Place')
                await self.get_teams(game["teams"]["home"]["id"], leagueObj.id)
                home_team = await sync_to_async(lambda:self.models.Team.objects.using("default").get(id=game["teams"]["home"]["id"], sport_mask="amf", vhost=self.vhost),thread_sensitive=False)()
            except self.models.Team.MultipleObjectsReturned as e:
                home_team  = await sync_to_async(lambda:self.models.Team.objects.using("default").filter(team__id=game["teams"]["home"]["id"], sport_mask="amf",
                                                            vhost=self.vhost).first(),thread_sensitive=False)()
                self.logger.warning(
                    f"Warning! HT: {game['teams']['home']['id']}/{game['teams']['home']['name']}: Returned more than one team, selecting: {home_team.uuid}")

            try:
                away_team = await sync_to_async(lambda:self.models.Team.objects.using("default").get(id=game["teams"]["away"]["id"], sport_mask="amf", vhost=self.vhost),thread_sensitive=False)()
            except self.models.Team.DoesNotExist:
                self.logger.warning(
                    f'Team not found: AT: {game["teams"]["away"]["id"]}/{game["teams"]["away"]["name"]}  - Creating in Place')
                await self.get_teams(game["teams"]["away"]["id"], leagueObj.id)
                away_team = await sync_to_async(lambda:self.models.Team.objects.using("default").get(id=game["teams"]["away"]["id"], sport_mask="amf", vhost=self.vhost),thread_sensitive=False)()
            except self.models.Team.MultipleObjectsReturned as e:
                away_team = await sync_to_async(lambda:self.models.Team.objects.using("default").filter(id=game["teams"]["away"]["id"], sport_mask="amf", vhost=self.vhost).first(),thread_sensitive=False)()
                self.logger.warning(
                    f"Warning! AT: {game['teams']['away']['id']}/{game['teams']['away']['name']}: Returned more than one team, selecting: {away_team.uuid}")
            if home_team and away_team:
                total_score_sum = 0
                away_score_sum = 0
                if not match_id:
                    amfGameObj, _ = await sync_to_async(lambda:self.models.AMFGame.objects.using("default").get_or_create(id=game["game"]["id"], season=seasonObj,
                                                                  vhost=self.vhost,
                                                                  league=leagueObj),thread_sensitive=False)()
                else:
                    amfGameObj = await sync_to_async(lambda:self.models.AMFGame.objects.using("default").get(id=match_id, vhost=self.vhost),thread_sensitive=False)()
                gtz = datetime.fromtimestamp(int(game["game"]["date"]["timestamp"]),
                                             tz=pytz.timezone(settings.TIME_ZONE))
                # print(gtz)
                # print(game)
                data_map = {"stage": game["game"]["stage"],
                            "week": game["game"]["week"],
                            "commence_time": gtz,
                            "venue": game["game"]["venue"]["name"],
                            "city": game["game"]["venue"]["city"],
                            "status_short": game["game"]["status"]["short"],
                            "status_long": game["game"]["status"]["long"],
                            # "status_timer": game["status"]["timer"],
                            "home_team": home_team,
                            "away_team": away_team, }
                if "time" in game:
                    data_map["time"] = game["time"]
                if "status" in game:
                    if "timer" in game["status"]:
                        data_map["status_timer"] = game["status"]["timer"]
                for k, v in data_map.items():
                    setattr(amfGameObj, k, v)
                await sync_to_async(lambda:amfGameObj.save(),thread_sensitive=False)()
                try:
                    amfGameHomeScoreObj = await sync_to_async(lambda:self.models.AMFGameScore.objects.using("default").get(match=amfGameObj, team=home_team, vhost=self.vhost),thread_sensitive=False)()
                except self.models.AMFGameScore.DoesNotExist:
                    amfGameHomeScoreObj = await sync_to_async(lambda:self.models.AMFGameScore(match=amfGameObj, team=home_team, vhost=self.vhost),thread_sensitive=False)()
                data_map = {
                    "quarter_1": game["scores"]["home"]["quarter_1"],
                    "quarter_2": game["scores"]["home"]["quarter_2"],
                    "quarter_3": game["scores"]["home"]["quarter_3"],
                    "quarter_4": game["scores"]["home"]["quarter_4"],
                    "overtime": game["scores"]["home"]["overtime"],
                    "total": game["scores"]["home"]["total"]
                }
                home_score_sum = game["scores"]["home"]["total"]
                for k, v in data_map.items():
                    setattr(amfGameHomeScoreObj, k, v)
                await sync_to_async(lambda:amfGameHomeScoreObj.save(),thread_sensitive=False)()
                try:
                    amfGameAwayScoreObj = await sync_to_async(lambda:self.models.AMFGameScore.objects.using("default").get(match=amfGameObj, team=away_team, vhost=self.vhost),thread_sensitive=False)()
                except self.models.AMFGameScore.DoesNotExist:
                    amfGameAwayScoreObj = self.models.AMFGameScore(match=amfGameObj, team=away_team, vhost=self.vhost)
                data_map = {
                    "quarter_1": game["scores"]["away"]["quarter_1"],
                    "quarter_2": game["scores"]["away"]["quarter_2"],
                    "quarter_3": game["scores"]["away"]["quarter_3"],
                    "quarter_4": game["scores"]["away"]["quarter_4"],
                    "overtime": game["scores"]["away"]["overtime"],
                    "total": game["scores"]["away"]["total"]
                }
                away_score_sum = game["scores"]["away"]["total"]
                for k, v in data_map.items():
                    setattr(amfGameAwayScoreObj, k, v)
                await sync_to_async(lambda:amfGameAwayScoreObj.save(),thread_sensitive=False)()
                if home_score_sum != 0 or away_score_sum != 0:
                    hsObj,_ = await sync_to_async(lambda:self.models.AMFGameScoreSummary.objects.using("default").get_or_create(vhost=self.vhost,match=amfGameObj,team=amfGameObj.home_team),thread_sensitive=False)()
                    hsObj.score = home_score_sum
                    await sync_to_async(lambda:hsObj.save(),thread_sensitive=False)()
                    asObj,_ = await sync_to_async(lambda:self.models.AMFGameScoreSummary.objects.using("default").get_or_create(vhost=self.vhost,match=amfGameObj,team=amfGameObj.away_team),thread_sensitive=False)()
                    asObj.score = away_score_sum
                    await sync_to_async(lambda:asObj.save(),thread_sensitive=False)()
        # print("At the end")
        self.logger.info(f"Worker Processed {len(data['response'])} matches.")

    async def get_games_events_worker(self, amf_id):
        self.logger.info(f"Game Events Worker for {amf_id}")
        amfObj = await sync_to_async(lambda:self.models.AMFGame.objects.using("default").get(id=amf_id, vhost=self.vhost),thread_sensitive=False)()
        url = f"{self.url_root}games/events?id={amfObj.id}&timezone={settings.TIME_ZONE}"
        seasonObj = await sync_to_async(lambda:self.models.Season.objects.using("default").get(active=True, vhost=self.vhost),thread_sensitive=False)()
        response = await self._fetch_with_retry(url)
        if not response:
            return False
        data = response.json()
        for event in data["response"]:
            try:
                teamObj = await sync_to_async(lambda:self.models.Team.objects.using("default").get(id=event["team"]["id"], league=amfObj.league, vhost=self.vhost),thread_sensitive=False)()
            except self.models.Team.DoesNotExist:
                teamObj = self.models.Team(id=event["team"]["id"], name=event["team"]["name"], logo=event["team"]["logo"],
                               vhost=self.vhost,
                               league=amfObj.league)
                await sync_to_async(lambda:teamObj.save(),thread_sensitive=False)()
            if event["player"]["id"] != None:
                try:
                    playerObj = await sync_to_async(lambda:self.models.Player.objects.using("default").get(id=event["player"]["id"]),thread_sensitive=False)()
                except self.models.Player.DoesNotExist:
                    playerObj = self.models.Player(id=event["player"]["id"], name=event["player"]["name"], vhost=self.vhost,
                                       image=event["player"]["image"], team=teamObj, season=seasonObj)
                    await sync_to_async(lambda:playerObj.save(),thread_sensitive=False)()
            else:
                noneId = 6656000 + teamObj.id
                try:
                    playerObj = await sync_to_async(lambda:self.models.Player.objects.using("default").get(id=noneId),thread_sensitive=False)()
                except self.models.Player.DoesNotExist:
                    playerObj = self.models.Player(name="none", team=teamObj, season=seasonObj, id=noneId)
                    await sync_to_async(lambda:playerObj.save(),thread_sensitive=False)()

            try:
                eventObj = await sync_to_async(lambda:self.models.AMFGameEvent.objects.using("default").get(amf_game=amfObj, quarter=event["quarter"], vhost=self.vhost,
                                                    minute=event["minute"], team=teamObj, player=playerObj,
                                                    season=seasonObj, type=event["type"]),thread_sensitive=False)()
            except self.models.AMFGameEvent.DoesNotExist:
                eventObj = self.models.AMFGameEvent(amf_game=amfObj, quarter=event["quarter"], minute=event["minute"],
                                        vhost=self.vhost,
                                        team=teamObj, player=playerObj, type=(event["type"] or "event"),
                                        season=seasonObj)
                eventObj.score = event["score"]
                eventObj.comment = event["comment"]
                await sync_to_async(lambda:eventObj.save(),thread_sensitive=False)()

    async def get_player_worker(self,team_id):
        teamObj = await sync_to_async(lambda:self.models.Team.objects.using("default").get(id=team_id,sport_mask="amf"),thread_sensitive=False)()
        teamLeagueObj = await sync_to_async(lambda:self.models.TeamLeagues.objects.using("default").get(team=teamObj,vhost=self.vhost),thread_sensitive=False)()
        seasons = await sync_to_async(lambda:sync_to_async(lambda:teamLeagueObj.league.seasons)(),thread_sensitive=False)()
        season, seasonObj = await self.aget_league_active_season(seasons,self.vhost)
        url = f"{self.url_root}players?team={teamObj.id}&season={seasonObj.season_key}"
        data = await self._fetch_with_retry(url)
        if not data:
            self.logger.warning ("No player")
            return False
        data = data.json()
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
                self.logger.info(f"Created/updated Player {playerObj.name}... ")
            teamObj.need_sync_players = False
            await sync_to_async(lambda:teamObj.save(),thread_sensitive=False)()


    async def get_player_stats_worker(self,player_id):
        # Step one: Seasons:
        seasonObj = await sync_to_async(lambda:self.models.Season.objects.using("default").get(active=True,vhost=self.vhost),thread_sensitive=False)()
        playerObj = await sync_to_async(lambda:self.models.Player.objects.using("default").get(id=player_id,vhost=self.vhost),thread_sensitive=False)()
        count = 0
        url = f"{self.url_root}/players/statistics?id={playerObj.id}&season={seasonObj.season_key}&timezone={settings.TIME_ZONE}"
        data = await self._fetch_with_retry(url)
        if not data:
            return False
        for data in data["response"]:
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


    async def get_players(self,team_id=False):
        if team_id:
            teams = self.models.Team.objects.using("default").filter(id=team_id, sport_mask="amf",vhost=self.vhost)
        else:
            teams = self.models.Team.objects.using("default").filter(sport_mask="amf",vhost=self.vhost)
        teams = await sync_to_async(lambda:list(teams),thread_sensitive=False)()
        for team in teams:
          self.logger.info(f"Getting players for Team {team.name}")
          await  self.get_player_worker(team.id)


    async def get_games(self,**kwargs):
        self.logger.warning(f"Getting Games from API.")

        _leagueObj = self.models.League.objects.using("default").filter(active=True, sport_mask="amf",vhost=self.vhost)
        if await sync_to_async(lambda:_leagueObj.count(),thread_sensitive=False)() < 1:
            self.logger.warning(
                "There are no Active League objects with an AMF sports mask. Not fetching anything. This is probably -not- what you wanted.")
        leagues = await sync_to_async(lambda:list(_leagueObj),thread_sensitive=False)()
        for leagueObj in leagues:
            if not "date_start" in kwargs:
                date = datetime.now().strftime("%Y-%m-%d")
                await self.get_games_worker(date, leagueObj.id,)
            else:
                date_start = datetime.strptime(kwargs["date_start"], "%Y-%m-%d")
                current_date = date_start
                date_end = datetime.strptime(kwargs["date_stop"], "%Y-%m-%d")
                while current_date < date_end:
                    await self.get_games_worker(current_date.strftime("%Y-%m-%d"), leagueObj.id, )
                    current_date += timedelta(days=1)


    async def fetch_period_fixtures(self,start,stop):
        return await self.get_games(date_start=start,date_stop=stop)


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
            wait_seconds = await  self._seconds_until_midnight()
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
        self.logger.info(f"APISports/AMF Worker Tick!")
        #await sync_to_async(lambda:close_old_connections(),thread_sensitive=True)()


    async def _run(self):

        self.setup_loop()
        await AsyncWorkerABC._run(self)


    async def start(self):
        apiSettings, created = await  sync_to_async(lambda:self.models.VHostParameterRegistry.objects.using("default").get_or_create(vhost=self.vhost, application=self.regappid,
                                                                            name="api_key_str"),thread_sensitive=False)()
        headers = {"x-rapidapi-key": f"{apiSettings.value_text}"}
        self.client = httpx.AsyncClient(headers=headers,limits=self.httpx_limits,timeout=self.httpx_timeout)
        await AsyncWorkerABC.start(self)