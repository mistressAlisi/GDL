from datetime import datetime, timedelta
from time import timezone

import pytz
from django.conf import settings
from django.db import IntegrityError

from dataengine.drivers.apisports.driver.toolkit import get_api_sports_session, getLogger, get_league_active_season
from dataengine.drivers.apisports.models import Season, Team, Player, League, TeamLeagues, PlayerStats, Venue, \
    TeamVenue, FBALLPlayerStats, FBALLGame, FBALLGameScore
# from providers.apisports.tasks.amf import get_teams


class APISportsFootball(object):
    logger = getLogger("dataengine.drivers.apisports.driver.football","football.log","apisports")
    url_root = "https://v3.football.api-sports.io/"

    def __init__(self, vhost, **kwargs):
        self.vhost = vhost
        self.session, self.api_settings = get_api_sports_session(vhost)

    def _create_venue(self,venueData):
        if 'id' not in venueData or 'name' not in venueData:
            return False
        venueObj, cc = Venue.objects.get_or_create(id=venueData['id'],vhost=self.vhost)
        if cc:
            venueObj.save()
        keys = venueData.keys()
        for key in keys:
            setattr(venueObj, key, venueData[key])
        venueObj.save()
        return venueObj

    def _create_team(self,team, leagueObj, venue=None):
        if "id" and "name" in team:
            teamObj, created = Team.objects.get_or_create(id=team["id"], sport_mask="fball",vhost=self.vhost)
            if created:
                teamObj.save()
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
            teamObj.save()
            self.logger.info(f"Created/updated Team {teamObj.name}... Adding to system (if necessary):")
            if venue != None:
                tbo, ctb = TeamVenue.objects.get_or_create(venue=venue, team=teamObj,vhost=self.vhost)
                if ctb:
                    tbo.save()
                # print(f"Created/updated Team {teamObj.name}... Adding to system (if necessary):")
            teamLeagueObj, cc = TeamLeagues.objects.get_or_create(league=leagueObj, team=teamObj, sport_mask="fball",vhost=self.vhost)
            teamLeagueObj.save()
            return teamObj

    def get_leagues(self,id=False):
        # Step one: Seasons:
        self.logger.info(f"Getting seasons from API Sports.")
        url = f"{self.url_root}/leagues"
        if id:
            url += f"?id={id}"
        response = self.session.get(url)
        if response.status_code == 200:
            data = response.json()

            for league in data["response"]:
                # print(league["country"])
                leagueObj = League.objects.get_or_create(id=league["league"]["id"], sport_mask="fball",vhost=self.vhost)[0]
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
                leagueObj.save()
                self.logger.info(f"Created/updated League {leagueObj.name}... (Currently inactive)")
                if id:
                    return leagueObj

    def get_teams(self,team_id=False, league_id=False, sync=False):
        # Step one: Seasons:
        self.logger.info(f"Getting Teams from API Sports.")
        if not league_id:
            _leagueObj = League.objects.filter(active=True, sport_mask="fball",vhost=self.vhost).order_by("-id")
        else:
            _leagueObj = League.objects.filter(active=True, sport_mask="fball", id=league_id,vhost=self.vhost).order_by("-id")
        if (len(_leagueObj) < 1):
            self.logger.warning(
                "There are no Active League objects with a FBALL sports mask. Not fetching anything. This is probably -not- what you wanted.")
            if sync:
                print(f"League ID: {league_id}")
                print(
                    "There are no Active League objects with a FBALL sports mask. Not fetching anything. This is probably -not- what you wanted.")
        for leagueObj in _leagueObj:
            # print(f"{leagueObj.id}/{leagueObj.name}")
            season, seasonObj = get_league_active_season(leagueObj.seasons,self.vhost)
            if not season:
                self.logger.warning(f"League {leagueObj.name} has no active season: Not continuing.")
            # print(season)
            if leagueObj.needs_plusone:
                season_key = seasonObj.get_season_key_full()
            else:
                season_key = seasonObj.season_key
            url = f"{self.url_root}/teams?league={leagueObj.id}&season={season_key}"
            if team_id:
                url += f"&id={team_id}"
            self.logger.info(url)
            # print(url)
            response = self.session.get(url)
            if response.status_code == 200:

                data = response.json()
                # print(data)

                if len(data["response"]) == 0:
                    print(f"***WARNING!!! Empty Response?!*** league:{leagueObj}/season:{season_key}")
                for team in data["response"]:
                    if "venue" in team and team["venue"]["id"] != None:
                        venueObj = self._create_venue(team["venue"])
                    else:
                        venueObj = None

                    cto = self._create_team(team["team"], leagueObj, venueObj)
                    if sync:
                        return cto
                self.logger.info(f"***Processed {len(data["response"])} teams...***")

    def get_players_worker(self,league_id, team_id=False, page=1, bkg=False):
        leagueObj = League.objects.get(id=league_id, sport_mask="fball",vhost=self.vhost)
        if not bkg:
            if not team_id:
                self.logger.info(f"Processing League {leagueObj.id}/{leagueObj.name}... Page {page}")
            else:
                self.logger.info(f"Processing League {leagueObj.id}/{leagueObj.name} - Team {team_id}... Page {page}")
        season, seasonObj = get_league_active_season(leagueObj.seasons,self.vhost)
        if not season:
            self.logger.warning(f"League {leagueObj.name} has no active season: Not continuing.")
            return False
        url = f"{self.url_root}players?season={seasonObj.season_key}&page={page}&league={leagueObj.id}"
        if team_id:
            url += f"&team={team_id}"
        response = self.session.get(url)
        if response.status_code == 200:
            data = response.json()
            for row in data["response"]:
                if "id" and "name" in row["player"]:
                    if not bkg:
                        print(f"Processing Player {row["player"]['id']}/{row["player"]['name']}....")
                    try:
                        playerObj = Player.objects.get(id=row["player"]["id"],vhost=self.vhost)
                    except Player.DoesNotExist:
                        playerObj = Player(id=row["player"]["id"], league=leagueObj, season=seasonObj,vhost=self.vhost)
                        playerObj.save()
                    for k in row["player"]:
                        setattr(playerObj, k, row["player"][k])

                    if "birth" in row["player"]:
                        if type(row["player"]["birth"]) == dict:
                            playerObj.birth_place = row["player"]["birth"]["place"]
                            playerObj.birth_date = row["player"]["birth"]["date"]
                            playerObj.birth_country = row["player"]["birth"]["country"]
                    playerObj.need_sync_player_stats = True
                    playerObj.save()
                    if "statistics" in row:
                        for srow in row["statistics"]:
                            try:
                                teamObj = Team.objects.get(id=srow["team"]["id"], sport_mask="fball",vhost=self.vhost)
                            except Team.DoesNotExist:
                                self.get_teams(id=srow["team"]["id"])
                                teamObj = Team.objects.get(id=srow["team"]["id"], sport_mask="fball",vhost=self.vhost)

                            statsObj, scc = FBALLPlayerStats.objects.get_or_create(player=playerObj, team=teamObj,vhost=self.vhost,
                                                                                   league=leagueObj, season=seasonObj)
                            if scc:
                                statsObj.save()
                            for l in ["games", "substitutes", "shots", "goals", "passes", "tackles", "duels",
                                      "dribbles", "fouls", "cards", "penalty"]:
                                for k in srow[l].keys():
                                    dbk = f"{l}_{k}"
                                    if dbk in statsObj._meta.fields:
                                        setattr(statsObj, dbk, srow[l][k])
                            statsObj.save()
                            self.logger.info(f"Created/updated Player Stats {statsObj.uuid}.")

                    self.logger.info(f"Created/updated Player {playerObj.name}... Linking if Necessary")
            # Reentrant/Recursive over pagination range:
            if "paging" in data:
                if data["paging"]["current"] < data["paging"]["total"]:
                    page = page + 1
                    if bkg:
                        self.get_players_worker(leagueObj.id, team_id, page, bkg)
                    else:
                        self.get_players_worker(leagueObj.id, team_id, page, bkg)

    def get_games_worker(self,date, league_id=False, season_id=False, match_id=False, bkg=False):
        # Step one: Seasons:
        self.logger.info(f"Football Games Worker for {league_id}/{season_id}/{match_id} @ {date}")
        if not bkg:
            self.logger.info(f"Football Games Worker for {league_id}/{season_id}/{match_id} @ {date}")
        if league_id:
            try:
                leagueObj = League.objects.get(id=league_id, sport_mask="fball",vhost=self.vhost)
            except League.DoesNotExist as e:
                self.logger.error(f"League ID {league_id} does not exist / Not found. Sport mask: FBALL ")
                self.logger.error(f"This is Match ID {match_id}")
                raise e
            if leagueObj.season_override:
                seasonStr = leagueObj.season_override
            else:
                try:
                    season, seasonObj = get_league_active_season(leagueObj.seasons,self.vhost)
                except Exception as e:
                    season = False
                    seasonObj = None
                    self.logger.info(f"Unable to get active season for {leagueObj.name} ignoring.")
                if not season:
                    self.logger.warning(f"League {leagueObj.name} has no active season: Not continuing.")
                    return False
                if leagueObj.needs_plusone:
                    seasonStr = seasonObj.get_season_key_full()
                else:
                    seasonStr = seasonObj.season_key
            count = 0
            if not match_id:
                url = f"{self.url_root}fixtures?league={leagueObj.id}&season={seasonStr}&date={date}&timezone={settings.TIME_ZONE}"
            else:
                url = f"{self.url_root}fixtures?id={match_id}&timezone={settings.TIME_ZONE}"
        else:
            # No LeagueObj specified, go Live fixtures:
            url = f"{self.url_root}fixtures?live=all&timezone={settings.TIME_ZONE}"
        self.logger.info(url)
        response = self.session.get(url)
        data = response.json()

        if not bkg:
            self.logger.info(f"Response contains {len(data["response"])} entries: processing...")
            # print(data)
        for row in data["response"]:
            currentWinner = False
            # Get League:
            try:
                leagueObj = League.objects.get(id=row["league"]["id"], sport_mask="fball",vhost=self.vhost)
            except League.DoesNotExist as e:
                leagueObj = self.get_leagues(row["league"]["id"])

            season, seasonObj = get_league_active_season(leagueObj.seasons,self.vhost)
            # Get Teams:
            try:
                homeTeamObj = Team.objects.get(id=row["teams"]["home"]["id"], sport_mask="fball",vhost=self.vhost)
            except Team.DoesNotExist:
                homeTeamObj = self.get_teams(row["teams"]["home"]["id"], leagueObj.id, True)
            if row["teams"]["home"]["winner"]:
                currentWinner = homeTeamObj
            try:
                awayTeamObj = Team.objects.get(id=row["teams"]["away"]["id"], sport_mask="fball",vhost=self.vhost)
            except Team.DoesNotExist:

                awayTeamObj = self.get_teams(row["teams"]["away"]["id"], leagueObj.id, True)
            if row["teams"]["away"]["winner"]:
                currentWinner = awayTeamObj
            try:
                fballGameObj = FBALLGame.objects.get(id=row["fixture"]["id"], league=leagueObj,vhost=self.vhost)
            except FBALLGame.DoesNotExist:
                fballGameObj = FBALLGame(id=row["fixture"]["id"], league=leagueObj, season=seasonObj,vhost=self.vhost)
                fballGameObj.save()
            data_map = {
                "referee": row["fixture"]["referee"],
                "commence_time": datetime.fromisoformat(row["fixture"]["date"]),
                "status_short": row["fixture"]["status"]["short"],
                "status_long": row["fixture"]["status"]["long"],
                "status_timer": row["fixture"]["status"]["elapsed"],
                "status_extra": row["fixture"]["status"]["extra"],
                "home_team": homeTeamObj,
                "away_team": awayTeamObj,
            }
            # print(f"Home Team: {homeTeamObj} / Away Team: {awayTeamObj}")
            for p in ["first", "second"]:
                if row["fixture"]["periods"][p] != None:
                    data_map[f"{p}_period"] = datetime.fromtimestamp(row["fixture"]["periods"][p],tz=pytz.timezone(settings.TIME_ZONE)).isoformat()
                    # print(row["fixture"]["periods"][p],datetime.fromtimestamp(row["fixture"]["periods"][p]))

            if "league" in row:
                if "round" in row["league"]:
                    data_map["round"] = row["league"]["round"]
            if "venue" in row["fixture"]:
                if "id" in row["fixture"]["venue"] and "name" in row["fixture"]["venue"] and \
                        row["fixture"]["venue"]["id"]:
                    try:
                        venueObj = Venue.objects.get(id=row["fixture"]["venue"]["id"],vhost=self.vhost)
                    except Venue.DoesNotExist:
                        venueObj = Venue(id=row["fixture"]["venue"]["id"], name=row["fixture"]["venue"]["name"],
                                         city=row["fixture"]["venue"]["city"],vhost=self.vhost)
                        venueObj.save()
                    data_map["venue"] = venueObj

            for k, v in data_map.items():
                setattr(fballGameObj, k, v)
            # print(fballGameObj.first_period)

            fballGameObj.save()
            homeScoreObj = FBALLGameScore.objects.get_or_create(match=fballGameObj, team=homeTeamObj,vhost=self.vhost)[0]
            homeScoreObj.save()
            awayScoreObj = FBALLGameScore.objects.get_or_create(match=fballGameObj, team=awayTeamObj,vhost=self.vhost)[0]
            awayScoreObj.save()
            for k in ["halftime", "fulltime", "extratime", "penalty"]:
                if row["score"][k]["home"] != None:
                    setattr(homeScoreObj, k, int(row["score"][k]["home"]))
                if row["score"][k]["away"] != None:
                    setattr(awayScoreObj, k, int(row["score"][k]["away"]))
            if row["goals"]["home"] != None:
                homeScoreObj.goals = int(row["goals"]["home"])
            if row["goals"]["away"] != None:
                awayScoreObj.goals = int(row["goals"]["away"])
            homeScoreObj.save()
            awayScoreObj.save()


    def get_players(self,team_id=False):
        if team_id:
            teams = Team.objects.filter(id=team_id, sport_mask="fball",vhost=self.vhost)
        else:
            teams = Team.objects.filter(sport_mask="fball",vhost=self.vhost)
        for team in teams:

            teamLeagueObj = TeamLeagues.objects.filter(team=team).first()
            # season, seasonObj = get_league_active_season(teamLeagueObj.league,self.vhost)
            self.get_players_worker(teamLeagueObj.league.id,team.id)

    def fetch_period_fixtures(self,start,stop):
        return self.get_games(date_start=start,date_stop=stop)

    def get_games(self,**kwargs):
        self.logger.warning(f"Getting Games from API.")
        date = datetime.now().strftime("%Y-%m-%d")
        _leagueObj = League.objects.filter(active=True, sport_mask="fball",vhost=self.vhost)
        if (len(_leagueObj) < 1):
            self.logger.warning(
                "There are no Active League objects with an FBALL sports mask. Not fetching anything. This is probably -not- what you wanted.")
        for leagueObj in _leagueObj:
            if not "date_start" in kwargs:
                date = datetime.now().strftime("%Y-%m-%d")
                self.get_games_worker(date, leagueObj.id, )
                old_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
                self.get_games_worker(old_date, leagueObj.id, )
            else:
                date_start = datetime.strptime(kwargs["date_start"], "%Y-%m-%d")
                current_date = date_start
                date_end = datetime.strptime(kwargs["date_stop"], "%Y-%m-%d")
                while current_date < date_end:
                    self.get_games_worker(current_date.strftime("%Y-%m-%d"), leagueObj.id, )
                    current_date += timedelta(days=1)


APISportsDriver = APISportsFootball