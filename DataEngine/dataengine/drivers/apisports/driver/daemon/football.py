import asyncio
import os
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




class APISportsFootballAsync(AsyncWorkerABC):
    url_root = "https://v3.football.api-sports.io/"
    regappid = "dataengine.drivers.apisports"
    last_timestamp = False
    _midnight_task = False
    def __init__(self, vhost = object ,logger = object, name: str = "APISportsFootballD", interval: float = 300,run_in_process: bool = False,loki_url=None,):
        AsyncWorkerABC.__init__(self,vhost, logger, name, interval,run_in_process,loki_url)
        if not self.run_in_process:
            self._child_init()

    def _child_init(self):
        """
        Runs inside the forked child *after* django.setup().
        Safe place for model imports.
        """
        super()._child_init()
        from dataengine.drivers.apisports.models import Team, Player, League, \
            TeamLeagues, Venue, TeamVenue, FBALLPlayerStats, FBALLGame, \
            FBALLGameScore, FBALLGameScoreSummary
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
            Player=Player,
            League=League,
            TeamLeagues=TeamLeagues,
            Venue=Venue,
            TeamVenue=TeamVenue,
            FBALLPlayerStats=FBALLPlayerStats,
            FBALLGame=FBALLGame,
            FBALLGameScore=FBALLGameScore,
            FBALLGameScoreSummary=FBALLGameScoreSummary,
            Timezone=Timezone,
            VHostParameterRegistry=VHostParameterRegistry,

        )
    async def _create_venue(self,venueData):
        if 'id' not in venueData or 'name' not in venueData:
            return False
        venueObj, cc = await sync_to_async(lambda:self.models.Venue.objects.using("default").get_or_create(id=venueData['id'],vhost=self.vhost),thread_sensitive=False)()
        if cc:
            await sync_to_async(lambda:venueObj.save(),thread_sensitive=False)()
        keys = venueData.keys()
        for key in keys:
            setattr(venueObj, key, venueData[key])
        await sync_to_async(lambda:venueObj.save(),thread_sensitive=False)()
        return venueObj


    async def _create_team(self,team, leagueObj, venue=None):
        if "id" and "name" in team:
            teamObj, created = await sync_to_async(lambda:self.models.Team.objects.using("default").get_or_create(id=team["id"], sport_mask="fball",vhost=self.vhost),thread_sensitive=False)()
            if created:
                await sync_to_async(lambda:teamObj.save(),thread_sensitive=False)()
            teamObj.name = team["name"]
            teamObj.logo = team["logo"]
            teamObj.country_name = team["country"]
            # teamObj.country_code = team["code"]
            teamObj.national_team = team["national"]

            if "city" in team:
                teamObj.city = team["city"]
            if "owner" in team:
                teamObj.owner = team["owner"]
            if "established" in team:
                teamObj.established = team["established"]
            if "stadium" in team:
                teamObj.stadium = team["stadium"]
            await sync_to_async(lambda:teamObj.save(),thread_sensitive=False)()
            self.logger.info(f"Created/updated Team {teamObj.name}... Adding to system (if necessary):")
            if venue != None:
                tbo, ctb = await sync_to_async(lambda:self.models.TeamVenue.objects.using("default").get_or_create(venue=venue, team=teamObj,vhost=self.vhost),thread_sensitive=False)()
                if ctb:
                    await sync_to_async(lambda:tbo.save(),thread_sensitive=False)()
                # print(f"Created/updated Team {teamObj.name}... Adding to system (if necessary):")
            teamLeagueObj, cc = await sync_to_async(lambda:self.models.TeamLeagues.objects.using("default").get_or_create(league=leagueObj, team=teamObj, sport_mask="fball",vhost=self.vhost),thread_sensitive=False)()
            await sync_to_async(lambda:teamLeagueObj.save(),thread_sensitive=False)()
            return teamObj

    async def get_leagues(self,id=False):
        # Step one: Seasons:
        self.logger.info(f"Getting seasons from API Sports.")
        url = f"{self.url_root}/leagues"
        if id:
            url += f"?id={id}"
        response = await self._fetch_with_retry(url)
        if not response: return False
        if response.status_code == 200:
            data = response.json()

            for league in data["response"]:
                # print(league["country"])
                leagueObj,_ = await sync_to_async(lambda:self.models.League.objects.using("default").get_or_create(id=league["league"]["id"], sport_mask="fball",vhost=self.vhost),thread_sensitive=False)()
                leagueObj.name = league["league"]["name"]
                leagueObj.logo = league["league"]["logo"]
                leagueObj.sport_mask = "fball"
                leagueObj.country_name = league["country"]["name"]
                if league["country"]["code"] != None:
                    leagueObj.country_code = league["country"]["code"]
                elif "id" in league["country"] and league["country"]["id"] == None:
                    leagueObj.country_code = league["country"]["id"]
                leagueObj.flag = league["country"]["flag"]
                leagueObj.seasons = league["seasons"]
                await sync_to_async(lambda:leagueObj.save(),thread_sensitive=False)()
                self.logger.info(f"Created/updated League {leagueObj.name}... (Currently inactive)")
                if id:
                    return leagueObj

    async def get_teams(self, team_id=False, league_id=False,sync=False):
        # Step one: Seasons:
        self.logger.info(f"Getting Teams from API Sports: Team ID {team_id}, League ID {league_id}")
        if not league_id:
            _leagueObj = self.models.League.objects.using("default").filter(active=True, sport_mask="fball", vhost=self.vhost).order_by("-id")
        else:
            _leagueObj = self.models.League.objects.using("default").filter(active=True, sport_mask="fball", id=league_id,
                                               vhost=self.vhost).order_by("-id")
        if await sync_to_async(lambda:_leagueObj.count(),thread_sensitive=False)() < 1:
            self.logger.warning(
                "There are no Active League objects with a FBALL sports mask. Not fetching anything. This is probably -not- what you wanted.")
        _leagueObj = await sync_to_async(list,thread_sensitive=False)(_leagueObj)
        for leagueObj in _leagueObj:
            # print(f"{leagueObj.id}/{leagueObj.name}")
            seasons = await sync_to_async(list,thread_sensitive=False)(leagueObj.seasons)
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
            url = f"{self.url_root}/teams?league={leagueObj.id}&season={seasonStr}"
            if team_id:
                url += f"&id={team_id}"
            self.logger.info(url)
            # print(url)
            response = await self._fetch_with_retry(url)
            if not response: return False
            if response.status_code == 200:

                data = response.json()
                # print(data)

                if len(data["response"]) == 0:
                    #print(f"***WARNING!!! Empty Response?!*** league:{leagueObj}/season:{season_key}")
                    return False
                for team in data["response"]:
                    if "venue" in team and team["venue"]["id"] != None:
                        venueObj = await self._create_venue(team["venue"])
                    else:
                        venueObj = None

                    cto = await self._create_team(team["team"], leagueObj, venueObj)
                    if sync:
                        return cto
                self.logger.info(f"***Processed {len(data["response"])} teams...***")

    async def get_players_worker(self, league_id, team_id=False, page=1, bkg=False):
        leagueObj = await sync_to_async(lambda:self.models.League.objects.using("default").get(id=league_id, sport_mask="fball", vhost=self.vhost),thread_sensitive=False)()
        if not bkg:
            if not team_id:
                self.logger.info(f"Processing League {leagueObj.id}/{leagueObj.name}... Page {page}")
            else:
                self.logger.info(f"Processing League {leagueObj.id}/{leagueObj.name} - Team {team_id}... Page {page}")
        seasons = await sync_to_async(list,thread_sensitive=False)(leagueObj.seasons)
        season, seasonObj = await self.aget_league_active_season(seasons, self.vhost)
        if not season:
            self.logger.warning(f"League {leagueObj.name} has no active season: Not continuing.")
            return False
        url = f"{self.url_root}players?season={seasonObj.season_key}&page={page}&league={leagueObj.id}"
        if team_id:
            url += f"&team={team_id}"
        response = await self._fetch_with_retry(url)
        if not response: return False
        if response.status_code == 200:
            data = response.json()
            for row in data["response"]:
                if "id" and "name" in row["player"]:
                    self.logger.info(f"Processing Player {row["player"]['id']}/{row["player"]['name']}....")
                    try:
                        playerObj = await sync_to_async(lambda:self.models.Player.objects.using("default").get(id=row["player"]["id"], vhost=self.vhost),thread_sensitive=False)()
                    except self.models.Player.DoesNotExist:
                        playerObj = self.models.Player(id=row["player"]["id"], league=leagueObj, season=seasonObj, vhost=self.vhost)
                        await sync_to_async(lambda:playerObj.save(),thread_sensitive=False)()
                    for k in row["player"]:
                        setattr(playerObj, k, row["player"][k])

                    if "birth" in row["player"]:
                        if type(row["player"]["birth"]) == dict:
                            playerObj.birth_place = row["player"]["birth"]["place"]
                            playerObj.birth_date = row["player"]["birth"]["date"]
                            playerObj.birth_country = row["player"]["birth"]["country"]
                    playerObj.need_sync_player_stats = True
                    await sync_to_async(lambda:playerObj.save(),thread_sensitive=False)()
                    if "statistics" in row:
                        for srow in row["statistics"]:
                            try:
                                teamObj = await sync_to_async(lambda:self.models.Team.objects.using("default").get(id=srow["team"]["id"], sport_mask="fball", vhost=self.vhost),thread_sensitive=False)()
                            except self.models.Team.DoesNotExist:
                                self.get_teams(id=srow["team"]["id"])
                                teamObj = await sync_to_async(lambda:self.models.Team.objects.using("default").get(id=srow["team"]["id"], sport_mask="fball", vhost=self.vhost),thread_sensitive=False)()

                            statsObj, scc = await sync_to_async(lambda:self.models.FBALLPlayerStats.objects.using("default").get_or_create(player=playerObj, team=teamObj,
                                                                                   vhost=self.vhost,
                                                                                   league=leagueObj, season=seasonObj),thread_sensitive=False)()
                            if scc:
                                await sync_to_async(lambda:statsObj.save(),thread_sensitive=False)()
                            for l in ["games", "substitutes", "shots", "goals", "passes", "tackles", "duels",
                                      "dribbles", "fouls", "cards", "penalty"]:
                                for k in srow[l].keys():
                                    dbk = f"{l}_{k}"
                                    if dbk in statsObj._meta.fields:
                                        setattr(statsObj, dbk, srow[l][k])
                            await sync_to_async(lambda:statsObj.save(),thread_sensitive=False)()
                            self.logger.info(f"Created/updated Player Stats {statsObj.uuid}.")

                    self.logger.info(f"Created/updated Player {playerObj.name}... Linking if Necessary")
            # Reentrant/Recursive over pagination range:
            if "paging" in data:
                if data["paging"]["current"] < data["paging"]["total"]:
                    page = page + 1
                    if bkg:
                        await self.get_players_worker(leagueObj.id, team_id, page, bkg)
                    else:
                        await self.get_players_worker(leagueObj.id, team_id, page, bkg)

    async def get_games_worker(self, date=False, league_id=False, season_id=False, match_id=False, page=1, bkg=False):
        if not league_id: return False
        if not date: datetime.now().date()
        self.logger.info(f"Football Games Worker for {league_id}/{season_id}/{match_id} @ {date}")

        if league_id:
            try:
                leagueObj = await sync_to_async(lambda:self.models.League.objects.using("default").get(id=league_id, sport_mask="fball", vhost=self.vhost),thread_sensitive=False)()
            except self.models.League.DoesNotExist as e:
                self.logger.error(f"League ID {league_id} does not exist / Not found. Sport mask: FBALL ")
                self.logger.error(f"This is Match ID {match_id}")
                raise e

            if leagueObj.season_override:
                seasonStr = leagueObj.season_override
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
                url = f"{self.url_root}fixtures?league={leagueObj.id}&season={seasonStr}&date={date}&timezone={settings.TIME_ZONE}"
            else:
                url = f"{self.url_root}fixtures?id={match_id}&timezone={settings.TIME_ZONE}"
        else:
            url = f"{self.url_root}fixtures?live=all&timezone={settings.TIME_ZONE}"

        self.logger.info(url)
        response = await self._fetch_with_retry(url)
        if not response:
            return False

        data = response.json()
        fixtures = data.get("response", [])
        self.logger.info(f"Response contains {len(fixtures)} entries: processing...")

        # ---- helper coroutine per fixture ----
        async def process_fixture(row, sem):
            async with sem:
                currentWinner = None
                try:
                    leagueObj = await sync_to_async(lambda:self.models.League.objects.using("default").get(id=row["league"]["id"], sport_mask="fball", vhost=self.vhost),thread_sensitive=False)()
                except self.models.League.DoesNotExist:
                    leagueObj = await self.get_leagues(row["league"]["id"])

                seasons = await sync_to_async(list,thread_sensitive=False)(leagueObj.seasons)
                season, seasonObj = await self.aget_league_active_season(seasons, self.vhost)

                # Teams
                try:
                    homeTeamObj = await sync_to_async(lambda:self.models.Team.objects.using("default").get(id=row["teams"]["home"]["id"], sport_mask="fball",
                                                          vhost=self.vhost),thread_sensitive=False)()
                except self.models.Team.DoesNotExist:
                    homeTeamObj = await self.get_teams(row["teams"]["home"]["id"], leagueObj.id, True)
                if row["teams"]["home"]["winner"]:
                    currentWinner = homeTeamObj

                try:
                    awayTeamObj = await sync_to_async(lambda:self.models.Team.objects.using("default").get(id=row["teams"]["away"]["id"], sport_mask="fball",
                                                          vhost=self.vhost),thread_sensitive=False)()
                except self.models.Team.DoesNotExist:
                    awayTeamObj = await self.get_teams(row["teams"]["away"]["id"], leagueObj.id, True)
                if row["teams"]["away"]["winner"]:
                    currentWinner = awayTeamObj

                # Game
                try:
                    fballGameObj = await sync_to_async(lambda:self.models.FBALLGame.objects.using("default").get(id=row["fixture"]["id"], league=leagueObj,
                                                                vhost=self.vhost),thread_sensitive=False)()
                except self.models.FBALLGame.DoesNotExist:
                    fballGameObj = self.models.FBALLGame(id=row["fixture"]["id"], league=leagueObj, season=seasonObj,
                                             vhost=self.vhost)
                    await sync_to_async(lambda:fballGameObj.save(),thread_sensitive=False)()
                status_short = row["fixture"]["status"]["short"]
                status_long = row["fixture"]["status"]["long"]
                elapsed = int(row["fixture"]["status"]["elapsed"] or 0)
                commence_time = datetime.fromisoformat(row["fixture"]["date"])
                if status_short == "2H":
                    if elapsed >= 90:
                        extra = int(row["fixture"]["status"]["extra"] or 0)
                        elapsed += extra
                    if commence_time + timedelta(minutes=elapsed) >= localtime():
                        status_short = "FT"
                        status_long = "Finished"
                data_map = {
                    "referee": row["fixture"]["referee"],
                    "commence_time": commence_time,
                    "status_short": status_short,
                    "status_long": status_long,
                    "status_timer": row["fixture"]["status"]["elapsed"],
                    "status_extra": row["fixture"]["status"]["extra"],
                    "home_team": homeTeamObj,
                    "away_team": awayTeamObj,
                }

                for p in ["first", "second"]:
                    if row["fixture"]["periods"].get(p) is not None:
                        data_map[f"{p}_period"] = datetime.fromtimestamp(
                            row["fixture"]["periods"][p],
                            tz=pytz.timezone(settings.TIME_ZONE)
                        ).isoformat()

                if "league" in row and "round" in row["league"]:
                    data_map["round"] = row["league"]["round"]

                if "venue" in row["fixture"]:
                    venue_data = row["fixture"]["venue"]
                    if venue_data.get("id") and venue_data.get("name"):
                        try:
                            venueObj = await sync_to_async(lambda:self.models.Venue.objects.using("default").get(id=venue_data["id"], vhost=self.vhost),thread_sensitive=False)()
                        except self.models.Venue.DoesNotExist:
                            venueObj = self.models.Venue(
                                id=venue_data["id"],
                                name=venue_data["name"],
                                city=venue_data.get("city"),
                                vhost=self.vhost,
                            )
                            await sync_to_async(lambda:venueObj.save(),thread_sensitive=False)()
                        data_map["venue"] = venueObj

                for k, v in data_map.items():
                    setattr(fballGameObj, k, v)
                await sync_to_async(lambda:fballGameObj.save(),thread_sensitive=False)()

                # Scores
                home_score_sum = 0
                away_score_sum = 0
                homeScoreObj, _ = await sync_to_async(lambda:self.models.FBALLGameScore.objects.using("default").get_or_create(
                    match=fballGameObj, team=homeTeamObj, vhost=self.vhost
                ),thread_sensitive=False)()
                awayScoreObj, _ = await sync_to_async(lambda:self.models.FBALLGameScore.objects.using("default").get_or_create(
                    match=fballGameObj, team=awayTeamObj, vhost=self.vhost
                ),thread_sensitive=False)()

                for k in ["halftime", "fulltime", "extratime", "penalty"]:
                    if row["score"][k]["home"] is not None:
                        setattr(homeScoreObj, k, int(row["score"][k]["home"]))
                    if row["score"][k]["away"] is not None:
                        setattr(awayScoreObj, k, int(row["score"][k]["away"]))

                if row["goals"]["home"] is not None:
                    homeScoreObj.goals = int(row["goals"]["home"])
                    home_score_sum = int(row["goals"]["home"])
                if row["goals"]["away"] is not None:
                    awayScoreObj.goals = int(row["goals"]["away"])
                    away_score_sum = int(row["goals"]["away"])

                await sync_to_async(lambda:homeScoreObj.save(),thread_sensitive=False)()
                await sync_to_async(lambda:awayScoreObj.save(),thread_sensitive=False)()
                if home_score_sum != 0 or away_score_sum != 0:
                    hsObj,_ = await sync_to_async(lambda:self.models.FBALLGameScoreSummary.objects.using("default").get_or_create(vhost=self.vhost,match=fballGameObj,team=fballGameObj.home_team),thread_sensitive=False)()
                    hsObj.score = home_score_sum
                    await sync_to_async(lambda:hsObj.save(),thread_sensitive=False)()
                    asObj,_ = await sync_to_async(lambda:self.models.FBALLGameScoreSummary.objects.using("default").get_or_create(vhost=self.vhost,match=fballGameObj,team=fballGameObj.away_team),thread_sensitive=False)()
                    asObj.score = away_score_sum
                    await sync_to_async(lambda:asObj.save(),thread_sensitive=False)()
                self.logger.info(f"Fixture {row['fixture']['id']} Created/Updated.")

        # ---- Run fixtures concurrently ----
        sem = asyncio.Semaphore(self.max_workers)  # limit concurrency
        tasks = [process_fixture(row, sem) for row in fixtures]
        await asyncio.gather(*tasks, return_exceptions=True)

        self.logger.info("All fixtures processed.")
        return True


    async def get_players(self,team_id=False):
        if team_id:
            teams = self.models.Team.objects.using("default").filter(id=team_id, sport_mask="fball",vhost=self.vhost)
        else:
            teams = self.models.Team.objects.using("default").filter(sport_mask="fball",vhost=self.vhost)
        teams = await sync_to_async(list,thread_sensitive=False)(teams)
        for team in teams:
            teamLeagueObj = await sync_to_async(lambda:self.models.TeamLeagues.objects.using("default").filter(team=team).first(),thread_sensitive=False)()
            # season, seasonObj = get_league_active_season(teamLeagueObj.league,self.vhost)
            league_id = await sync_to_async(lambda:teamLeagueObj.league.id,thread_sensitive=False)()
            await self.get_players_worker(league_id,team.id)


    async def get_games(self,**kwargs):
        self.logger.info(f"Getting Games from API.")
        date = datetime.now().strftime("%Y-%m-%d")
        _leagueObj = self.models.League.objects.using("default").filter(active=True, sport_mask="fball",vhost=self.vhost)
        if await sync_to_async(lambda:_leagueObj.count(),thread_sensitive=False)() <1:
            self.logger.warning(
                "There are no Active League objects with an FBALL sports mask. Not fetching anything. This is probably -not- what you wanted.")
        if "live" in kwargs:
            return await self.get_games_worker()
        _leagueObj = await sync_to_async(list,thread_sensitive=False)(_leagueObj)
        # build list of (date, league_id) tasks
        tasks = []
        for leagueObj in _leagueObj:
            if "date_start" not in kwargs:
                # single-day mode
                date = datetime.now().strftime("%Y-%m-%d")
                tasks.append((date, leagueObj.id))
            else:
                # range mode
                date_start = datetime.strptime(kwargs["date_start"], "%Y-%m-%d")
                date_end = datetime.strptime(kwargs["date_stop"], "%Y-%m-%d")

                current_date = date_start
                while current_date < date_end:
                    tasks.append((current_date.strftime("%Y-%m-%d"), leagueObj.id))
                    current_date += timedelta(days=1)

        # handler for each item
        async def fetch_handler(item):
            date_str, league_id = item
            await asyncio.sleep(1)
            return await self.get_games_worker(date_str, league_id)

        # run batches
        await self.run_in_batches(
            tasks,
            handler=fetch_handler,
            batch_size=20,
            label="get_games"
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

    async def _midnight_loop(self):
        """Independent loop waiting until midnight."""
        while not self._shutdown_event.is_set():
            wait_seconds = self._seconds_until_midnight()
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

    def _seconds_until_midnight(self) -> float:
        """Return the number of seconds until next midnight."""
        now = datetime.now()
        tomorrow = now + timedelta(days=1)
        midnight = datetime.combine(tomorrow.date(), datetime.min.time())
        return (midnight - now).total_seconds()

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
        #await sync_to_async(lambda:close_old_connections(),thread_sensitive=True)()
        self.logger.info(f"APISPorts/Football Worker Tick!")

    async def _run(self):
        self.setup_loop()
        await AsyncWorkerABC._run(self)

    async def start(self):
        apiSettings, created = await  sync_to_async(lambda:self.models.VHostParameterRegistry.objects.using("default").get_or_create(vhost=self.vhost, application=self.regappid,
                                                                            name="api_key_str"),thread_sensitive=False)()
        headers = {"x-rapidapi-key": f"{apiSettings.value_text}"}
        self.client = httpx.AsyncClient(headers=headers,limits=self.httpx_limits,timeout=self.httpx_timeout)
        await AsyncWorkerABC.start(self)