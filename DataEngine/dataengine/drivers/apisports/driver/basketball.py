from datetime import datetime, timedelta

from django.conf import settings
from django.db import IntegrityError

from dataengine.drivers.apisports.driver.toolkit import get_api_sports_session, getLogger, get_league_active_season
from dataengine.drivers.apisports.models import Season, Team, Player, League, TeamLeagues, PlayerStats, BABGame, BABGamePlayerStats,BABGameScore
# from providers.apisports.tasks.amf import get_teams


class APISportsBasketball(object):
    logger = getLogger("dataengine.drivers.apisports.driver.basketball","basketball.log","apisports")
    url_root = "https://v1.basketball.api-sports.io/"

    def __init__(self, vhost, **kwargs):
        self.vhost = vhost
        self.session, self.api_settings = get_api_sports_session(vhost)

    def _create_team(self,team, leagueObj):
        if "id" and "name" in team:
            teamObj, created = Team.objects.get_or_create(id=team["id"], sport_mask="bab",vhost=self.vhost)
            if created:
                teamObj.save()
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
            teamObj.save()
            self.logger.info(f"Created/updated Team {teamObj.name}... Adding to system")
            teamLeagueObj, cc = TeamLeagues.objects.get_or_create(league=leagueObj, team=teamObj, sport_mask="bab",vhost=self.vhost)
            teamLeagueObj.save()

    def get_games_stats_worker(self,bab_id):
        self.logger.info(f"Game Stats Worker for {bab_id}")
        babObj = BABGame.objects.get(id=bab_id)
        count = 0
        url = f"{self.url_root}/games/statistics/players?id={babObj.id}&timezone={settings.TIME_ZONE}"
        response = self.session.get(url)
        season, seasonObj = get_league_active_season(babObj.league.seasons,self.vhost)
        if response.status_code == 200:
            data = response.json()
            # print(data)
            for game in data["response"]:
                try:
                    team = Team.objects.get(id=game["team"]["id"], sport_mask="bab",vhost=self.vhost)
                except Team.MultipleObjectsReturned:
                    team = Team.objects.filter(id=game["team"]["id"], sport_mask="bab",vhost=self.vhost)[0]
                    self.logger.warning(f"Multiple objects returned for Team {game['team']['id']}: Picking 1st one: {team}")
                if "groups" in game:
                    for group in game["groups"]:
                        group_name = group["name"]
                        for player in group["players"]:
                            if player["player"]["id"] != "":
                                try:
                                    playerObj = Player.objects.get(id=int(player["player"]["id"]))
                                except Player.DoesNotExist:
                                    playerObj = Player(id=int(player["player"]["id"]), name=player['player']["name"],
                                                       image=player['player']["image"], team=team, season=seasonObj,
                                                       group=group_name,vhost=self.vhost)
                                    playerObj.save()
                                except IntegrityError as e:
                                    self.logger.error(
                                        f"Integrity Error inside get_game_stats_worker: {e}. Player Name={player['player']['name']}, ID={player['player']['id']}")
                                    playerObj = False
                                if playerObj:
                                    for stat in player["statistics"]:
                                        statObj = \
                                        BABGamePlayerStats.objects.get_or_create(player=playerObj, season=seasonObj,
                                                                                 group=group_name, name=stat["name"],
                                                                                 bab_game=babObj,vhost=self.vhost)[0]
                                        statObj.value = stat["value"]
                                        statObj.save()
                                    # print(statObj)

        else:
            self.logger.info(f"Request Result: HTTP {response.status_code}")
            self.logger.info(response)

    def get_games_worker(self,date, league_id, match_id=False, bkg=False):
        if not match_id:
            if not date: date = datetime.now()
            self.logger.info(f"Games Worker for {league_id}/{date}")
        else:
            self.logger.info(f"Games Worker for Match {match_id}")
        # Step one: Seasons:
        self.logger.info(f"Getting Games from API.")
        leagueObj = League.objects.get(id=league_id, sport_mask="bab",vhost=self.vhost)
        season, seasonObj = get_league_active_season(leagueObj.seasons,self.vhost)
        if not season:
            self.logger.warning(f"League {leagueObj.name} has no active season: Not continuing.")
            return False
        count = 0
        if leagueObj.season_override:
            seasonStr = leagueObj.season_override
        else:
            try:
                season, seasonObj = get_league_active_season(leagueObj.seasons, self.vhost)
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
        if not match_id:

            url = f"{self.url_root}games?league={leagueObj.id}&season={seasonStr}&date={date}&timezone={settings.TIME_ZONE}"

        else:
            url = f"{self.url_root}games?id={match_id}&timezone={settings.TIME_ZONE}"
        self.logger.info(url)
        response = self.session.get(url)
        if response.status_code == 200:
            data = response.json()
            # print(url)
            # print(data)
            for game in data["response"]:
                try:
                    home_team = Team.objects.get(id=game["teams"]["home"]["id"], sport_mask="bab",vhost=self.vhost)
                except Team.DoesNotExist:
                    self.logger.warning(
                        f'Team not found: HT: {game["teams"]["home"]["id"]}/{game["teams"]["home"]["name"]} - Creating!')
                    self.get_teams(game["teams"]["home"]["id"], leagueObj.id)
                    home_team = Team.objects.get(id=game["teams"]["home"]["id"], sport_mask="bab",vhost=self.vhost)
                try:
                    away_team = Team.objects.get(id=game["teams"]["away"]["id"], sport_mask="bab",vhost=self.vhost)
                except Team.DoesNotExist:
                    self.logger.warning(
                        f'Team not found: AT: {game["teams"]["away"]["id"]}/{game["teams"]["away"]["name"]} - Creating!')
                    self.get_teams(game["teams"]["away"]["id"], leagueObj.id)
                    away_team = Team.objects.get(id=game["teams"]["away"]["id"], sport_mask="bab",vhost=self.vhost)

                if home_team and away_team:
                    if not match_id:
                        BABGameObj = BABGame.objects.get_or_create(id=game["id"], league=leagueObj, season=seasonObj,vhost=self.vhost)[0]
                    else:
                        BABGameObj = BABGame.objects.get(id=match_id,vhost=self.vhost)
                    # print(game)
                    if BABGameObj.league.name == "NCAA":
                        if game["status"]["short"] in ["Q1","Q2"]:
                            game["status"]["short"] = "H1"
                            game["status"]["long"] = "First Half"
                        elif game["status"]["short"] in ["Q3","Q4"]:
                            game["status"]["short"] = "H2"
                            game["status"]["long"] = "Second Half"
                    # self.logger.info(f"BAB Match Timer: {game["status"]["timer"]}")
                    data_map = {"stage": game["stage"],
                                "week": game["week"],
                                "commence_time": datetime.fromisoformat(game["date"]),
                                # "venue": game["venue"],
                                # "city": game["venue"]["city"],
                                "status_short": game["status"]["short"],
                                "status_long": game["status"]["long"],
                                "status_timer": game["status"]["timer"],
                                "home_team": home_team,
                                "away_team": away_team, }
                    for k, v in data_map.items():
                        setattr(BABGameObj, k, v)
                    BABGameObj.save()
                    try:
                        BABGameHomeScoreObj = BABGameScore.objects.get(match=BABGameObj, team=home_team,vhost=self.vhost)
                    except BABGameScore.DoesNotExist:
                        BABGameHomeScoreObj = BABGameScore(match=BABGameObj, team=home_team,vhost=self.vhost)
                    data_map = {
                        "quarter_1": game["scores"]["home"]["quarter_1"],
                        "quarter_2": game["scores"]["home"]["quarter_2"],
                        "quarter_3": game["scores"]["home"]["quarter_3"],
                        "quarter_4": game["scores"]["home"]["quarter_4"],
                        "overtime": game["scores"]["home"]["over_time"],
                        "total": game["scores"]["home"]["total"]
                    }
                    for k, v in data_map.items():
                        setattr(BABGameHomeScoreObj, k, v)
                    try:
                        BABGameAwayScoreObj = BABGameScore.objects.get(match=BABGameObj, team=away_team,vhost=self.vhost)
                    except BABGameScore.DoesNotExist:
                        BABGameAwayScoreObj = BABGameScore(match=BABGameObj, team=away_team,vhost=self.vhost)
                    data_map = {
                        "quarter_1": game["scores"]["away"]["quarter_1"],
                        "quarter_2": game["scores"]["away"]["quarter_2"],
                        "quarter_3": game["scores"]["away"]["quarter_3"],
                        "quarter_4": game["scores"]["away"]["quarter_4"],
                        "overtime": game["scores"]["away"]["over_time"],
                        "total": game["scores"]["away"]["total"]
                    }
                    for k, v in data_map.items():
                        setattr(BABGameAwayScoreObj, k, v)
                    BABGameAwayScoreObj.save()
                    BABGameHomeScoreObj.save()

            else:
                # TODO: Feex me
                spammer = False
                if spammer:
                    print(response.status_code)
                    print(response)

    def get_player_worker(self,team_id):
        teamObj = Team.objects.get(id=team_id,sport_mask="bab",vhost=self.vhost)
        teamLeagueObj = TeamLeagues.objects.get(team=teamObj,vhost=self.vhost)
        season, seasonObj = get_league_active_season(teamLeagueObj.league.seasons,self.vhost)
        url = f"{self.url_root}players?team={teamObj.id}&season={seasonObj.season_key}"
        response = self.session.get(url)
        if response.status_code == 200:
            data = response.json()
            for player in data["response"]:
                if "id" and "name" in player:
                    try:
                        playerObj = Player.objects.get(id=player["id"],vhost=self.vhost)
                    except Player.DoesNotExist:
                        playerObj = Player(id=player["id"], team=teamObj, season=seasonObj,vhost=self.vhost)
                        playerObj.save()
                    for k in player:
                        setattr(playerObj, k, player[k])
                    playerObj.save()
                    self.logger.info(f"Created/updated Player {playerObj.name}...")
            teamObj.need_sync_players = False
            teamObj.save()

    def get_player_stats_worker(self,player_id, season_key):
        # Step one: Seasons:
        seasonObj = Season.objects.get(season_key=season_key,vhost=self.vhost)
        playerObj = Player.objects.get(id=player_id,vhost=self.vhost)
        count = 0
        url = f"{self.url_root}players/statistics?id={playerObj.id}&season={seasonObj.season_key}&timezone={settings.TIME_ZONE}"
        response = self.session.get(url)
        if response.status_code == 200:

            _data = response.json()
            for data in _data["response"]:
                for team in data["teams"]:
                    group_data = team["groups"][0]
                    # print(group_data)
                    for stat in group_data["statistics"]:
                        # print(stat)
                        try:
                            playerStatsObj = PlayerStats.objects.get(player=playerObj, season=seasonObj,vhost=self.vhost,
                                                                     group=group_data["name"], name=stat["name"])
                        except PlayerStats.DoesNotExist:
                            playerStatsObj = PlayerStats(player=playerObj, season=seasonObj, group=group_data["name"],
                                                         name=stat["name"],vhost=self.vhost)
                        playerStatsObj.value = stat["value"]
                        playerStatsObj.save()
                        count += 1
            playerObj.need_sync_player_stats = False
            playerObj.save()
            self.logger.info(f"Created/updated Player {playerObj.name}: {count} stats.")

    def get_teams(self,team_id=False, league_id=False):
        # Step one: Seasons:
        self.logger.info(f"Getting Teams from API Sports.")
        if not league_id:
            _leagueObj = League.objects.filter(active=True, sport_mask="bab",vhost=self.vhost).order_by("-id")
        else:
            _leagueObj = League.objects.filter(active=True, sport_mask="bab", id=league_id,vhost=self.vhost).order_by("-id")
        if (len(_leagueObj) < 1):
            self.logger.warning(
                "There are no Active League objects with a BAB sports mask. Not fetching anything. This is probably -not- what you wanted.")
        for leagueObj in _leagueObj:
            # print(leagueObj)
            # print(leagueObj.seasons)
            season, seasonObj = get_league_active_season(leagueObj.seasons,self.vhost)
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
            response = self.session.get(url)
            if response.status_code == 200:
                data = response.json()
                for team in data["response"]:
                    # print(team)
                    self._create_team(team, leagueObj)

    def get_leagues(self,arg=False):
        # Step one: Seasons:
        self.logger.info(f"Getting seasons from API Sports.")
        url = f"{self.url_root}/leagues"
        response = self.session.get(url)
        if response.status_code == 200:

            data = response.json()
            for league in data["response"]:
                # print(league)
                leagueObj = League.objects.get_or_create(id=league["id"],sport_mask="bab",vhost=self.vhost)[0]
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
                leagueObj.save()
                self.logger.info(f"Created/updated League {leagueObj.name}... (Currently inactive)")

    def get_players(self,team_id=False):
        if team_id:
            teams = Team.objects.filter(id=team_id, sport_mask="bab",vhost=self.vhost)
        else:
            teams = Team.objects.filter(sport_mask="bab",vhost=self.vhost)
        for team in teams:
            self.get_player_worker(team.id)

    def fetch_period_fixtures(self,start,stop):
        return self.get_games(date_start=start,date_stop=stop)

    def get_games(self,**kwargs):
        self.logger.warning(f"Getting Games from API.")
        date = datetime.now().strftime("%Y-%m-%d")
        _leagueObj = League.objects.filter(active=True, sport_mask="bab",vhost=self.vhost)
        if (len(_leagueObj) < 1):
            self.logger.warning(
                "There are no Active League objects with an BAB sports mask. Not fetching anything. This is probably -not- what you wanted.")
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



APISportsDriver = APISportsBasketball
