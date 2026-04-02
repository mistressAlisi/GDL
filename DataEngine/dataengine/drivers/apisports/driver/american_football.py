from datetime import datetime, timedelta

import pytz
from django.conf import settings
from django.db import IntegrityError
from django.utils import timezone

from dataengine.drivers.apisports.driver.toolkit import get_api_sports_session, getLogger, get_league_active_season
from dataengine.drivers.apisports.models import Season, Team, Player, AMFGamePlayerStats, League, AMFGame, AMFGameScore, \
    TeamLeagues, AMFGameEvent, PlayerStats
from parameters.models import Timezone


class APISportsAmericanFootball(object):

    logger = getLogger("dataengine.drivers.apisports.driver.american_football","american_football.log","apisports")
    url_root = "https://v1.american-football.api-sports.io/"

    def __init__(self, vhost, **kwargs):
        self.vhost = vhost
        self.session, self.api_settings = get_api_sports_session(vhost)

    def get_games_stats_worker(self,amf_id):
        self.logger.info(f"Game Stats Worker for {amf_id}")
        r_url = f"{self.url_root}games/statistics/players?id={amf_id}&timezone={settings.TIME_ZONE}"
        response = self.session.get(r_url)
        seasonObj = Season.objects.get(active=True)
        amfObj = AMFGame.objects.get(id=amf_id)
        if response.status_code == 200:
            data = response.json()
            for game in data["response"]:
                team = Team.objects.filter(id=game["team"]["id"])[0]

                for group in game["groups"]:
                    group_name = group["name"]
                    for player in group["players"]:
                        if player["player"]["id"] != "":
                            try:
                                playerObj = Player.objects.get(id=int(player["player"]["id"]),vhost=self.vhost)
                            except Player.DoesNotExist:
                                playerObj = Player(id=int(player["player"]["id"]),name=player['player']["name"],image=player['player']["image"],team=team,season=seasonObj,group=group_name,vhost=self.vhost)
                                playerObj.save()
                            except IntegrityError as e:
                                self.logger.error(f"Integrity Error inside get_game_stats_worker: {e}. Player Name={player['player']['name']}, ID={player['player']['id']}")
                                playerObj = False
                            if playerObj:
                                for stat in player["statistics"]:
                                    statObj = AMFGamePlayerStats.objects.get_or_create(player=playerObj,season=seasonObj,group=group_name,name=stat["name"],amf_game=amfObj,vhost=self.vhost)[0]
                                    statObj.value = stat["value"]
                                    statObj.save()
        else:
            self.logger.warning(f"Request Result: HTTP {response.status_code}")
            self.logger.info(response)

    def get_teams(self,team_id=None, league_id=None):
        self.logger.info(f"Getting Teams from API Sports.")

        if not league_id:
            _leagueObj = League.objects.filter(active=True, sport_mask="amf",vhost=self.vhost)
        else:
            _leagueObj = League.objects.filter(active=True, sport_mask="amf", id=league_id,vhost=self.vhost)

        if (len(_leagueObj) < 1):
            self.logger.warning(
                "There are no Active League objects with an AMF sports mask. Not fetching anything. This is probably -not- what you wanted.")
        for leagueObj in _leagueObj:
            season, seasonObj = get_league_active_season(leagueObj.seasons,self.vhost)
            if not season:
                self.logger.warning(f"League {leagueObj.name} has no active season: Not continuing.")
                return False
            url = f"{self.url_root}teams?league={leagueObj.id}&season={seasonObj.season_key}"
            # print(url)
            if team_id:
                url += f"&id={team_id}"
            self.logger.info(url)
            response = self.session.get(url)
            # print(response.json())
            if response.status_code == 200:
                data = response.json()
                # print(data)
                for team in data["response"]:
                    if "id" and "name" in team:
                        teamObj, created = Team.objects.get_or_create(id=team["id"], sport_mask="amf",vhost=self.vhost)
                        if created:
                            teamObj.save()
                        teamObj.name = team["name"]
                        teamObj.logo = team["logo"]
                        teamObj.country_name = team["country"]["name"]
                        teamObj.country_code = team["country"]["code"]
                        teamObj.flag = team["country"]["flag"]
                        teamObj.city = team["city"]
                        teamObj.owner = team["owner"]
                        teamObj.established = team["established"]
                        teamObj.stadium = team["stadium"]
                        teamObj.save()
                        self.logger.info(f"Created/updated Team {teamObj.name}... Adding to System (if necessary):")
                        teamLeagueObj, cc = TeamLeagues.objects.get_or_create(league=leagueObj, team=teamObj,
                                                                              sport_mask="amf",vhost=self.vhost)
                        teamLeagueObj.save()

    def get_leagues(self,arg=False):
        # Step one: Seasons:
        self.logger.info(f"Getting seasons from API Sports.")
        url = f"{self.url_root}leagues"
        response = self.session.get(url)
        if response.status_code == 200:
            data = response.json()
            for league in data["response"]:
                leagueObj = League.objects.get_or_create(id=league["league"]["id"], sport_mask="amf",vhost=self.vhost)[0]
                leagueObj.name = league["league"]["name"]
                leagueObj.logo = league["league"]["logo"]
                leagueObj.country_name = league["country"]["name"]
                leagueObj.country_code = league["country"]["code"]
                leagueObj.flag = league["country"]["flag"]
                leagueObj.seasons = league["seasons"]
                leagueObj.sport_mask = "amf"
                leagueObj.save()
                self.logger.info(f"Created/updated League {leagueObj.name}...")

    def get_games_worker(self,date, league_id, match_id=False):
        if not match_id:
            if not date: date = datetime.now()
            self.logger.info(f"Games Worker for {league_id}/{date}")
        else:
            self.logger.info(f"Games Worker for Match {match_id}")
        # Step one: Seasons:
        self.logger.info(f"Getting Games from API.")

        try:
            leagueObj = League.objects.get(id=league_id, sport_mask="amf",vhost=self.vhost)
        except League.DoesNotExist as e:
            self.logger.error(f"League ID {league_id} does not exist / Not found. Sport mask: AMF ")
            self.logger.error(f"This is Match ID {match_id}")
            raise e
        season, seasonObj = get_league_active_season(leagueObj.seasons,self.vhost)

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
        count = 0

        if not match_id:
            url = f"{self.url_root}games?league={leagueObj.id}&season={seasonStr}&date={date}&timezone={settings.TIME_ZONE}"
        else:
            url = f"{self.url_root}games?id={match_id}&timezone={settings.TIME_ZONE}"
        self.logger.info(url)
        response = self.session.get(url)
        if response.status_code == 200:
            data = response.json()
            # timezone.activate(settings.TIME_ZONE)
            # ctz = timezone.localtime(timezone.now()).tzinfo
            for game in data["response"]:
                try:
                    home_team = Team.objects.get(id=game["teams"]["home"]["id"], sport_mask="amf",vhost=self.vhost)
                except Team.DoesNotExist:
                    self.logger.warning(
                        f'Team not found: HT: {game["teams"]["home"]["id"]}/{game["teams"]["home"]["name"]} - Creating in Place')
                    self.get_teams(game["teams"]["home"]["id"], leagueObj.id)
                    home_team = Team.objects.get(id=game["teams"]["home"]["id"], sport_mask="amf",vhost=self.vhost)
                except Team.MultipleObjectsReturned as e:
                    home_team = home_team = Team.objects.filter(team__id=game["teams"]["home"]["id"], sport_mask="amf",vhost=self.vhost)
                    self.logger.warning(
                        f"Warning! HT: {game['teams']['home']['id']}/{game['teams']['home']['name']}: Returned more than one team, selecting: {home_team}")

                try:
                    away_team = Team.objects.get(id=game["teams"]["away"]["id"], sport_mask="amf",vhost=self.vhost)
                except Team.DoesNotExist:
                    self.logger.warning(
                        f'Team not found: AT: {game["teams"]["away"]["id"]}/{game["teams"]["away"]["name"]}  - Creating in Place')
                    self.get_teams(game["teams"]["away"]["id"], leagueObj.id)
                    away_team = Team.objects.get(id=game["teams"]["away"]["id"], sport_mask="amf",vhost=self.vhost)
                except Team.MultipleObjectsReturned as e:
                    away_team = Team.objects.filter(id=game["teams"]["away"]["id"], sport_mask="amf",vhost=self.vhost)
                    self.logger.warning(
                        f"Warning! AT: {game['teams']['away']['id']}/{game['teams']['away']['name']}: Returned more than one team, selecting: {away_team}")

                if home_team and away_team:
                    if not match_id:
                        amfGameObj,_ = AMFGame.objects.get_or_create(id=game["game"]["id"], season=seasonObj,vhost=self.vhost,
                                                                   league=leagueObj)
                    else:
                        amfGameObj = AMFGame.objects.get(id=match_id,vhost=self.vhost)
                    gtz = datetime.fromtimestamp(int(game["game"]["date"]["timestamp"]),tz=pytz.timezone(settings.TIME_ZONE))
                    # print(gtz)
                    # print(game)
                    data_map = {"stage": game["game"]["stage"],
                                "week": game["game"]["week"],
                                "commence_time": gtz,
                                "venue": game["game"]["venue"]["name"],
                                "city": game["game"]["venue"]["city"],
                                "status_short": game["game"]["status"]["short"],
                                "status_long": game["game"]["status"]["long"],
                                "status_timer": game["game"]["status"]["timer"],
                                "home_team": home_team,
                                "away_team": away_team, }
                    if "time" in game:
                        data_map["time"] = game["time"]
                    for k, v in data_map.items():
                        setattr(amfGameObj, k, v)
                    amfGameObj.save()
                    try:
                        amfGameHomeScoreObj = AMFGameScore.objects.get(match=amfGameObj, team=home_team,vhost=self.vhost)
                    except AMFGameScore.DoesNotExist:
                        amfGameHomeScoreObj = AMFGameScore(match=amfGameObj, team=home_team,vhost=self.vhost)
                    data_map = {
                        "quarter_1": game["scores"]["home"]["quarter_1"],
                        "quarter_2": game["scores"]["home"]["quarter_2"],
                        "quarter_3": game["scores"]["home"]["quarter_3"],
                        "quarter_4": game["scores"]["home"]["quarter_4"],
                        "overtime": game["scores"]["home"]["overtime"],
                        "total": game["scores"]["home"]["total"]
                    }
                    for k, v in data_map.items():
                        setattr(amfGameHomeScoreObj, k, v)
                    amfGameHomeScoreObj.save()
                    try:
                        amfGameAwayScoreObj = AMFGameScore.objects.get(match=amfGameObj, team=away_team,vhost=self.vhost)
                    except AMFGameScore.DoesNotExist:
                        amfGameAwayScoreObj = AMFGameScore(match=amfGameObj, team=away_team,vhost=self.vhost)
                    data_map = {
                        "quarter_1": game["scores"]["away"]["quarter_1"],
                        "quarter_2": game["scores"]["away"]["quarter_2"],
                        "quarter_3": game["scores"]["away"]["quarter_3"],
                        "quarter_4": game["scores"]["away"]["quarter_4"],
                        "overtime": game["scores"]["away"]["overtime"],
                        "total": game["scores"]["away"]["total"]
                    }
                    for k, v in data_map.items():
                        setattr(amfGameAwayScoreObj, k, v)
                    amfGameAwayScoreObj.save()

            self.logger.info(f"Worker Processed {len(data['response'])} matches.")

    def get_games_events_worker(self,amf_id):
        self.logger.info(f"Game Events Worker for {amf_id}")
        amfObj = AMFGame.objects.get(id=amf_id,vhost=self.vhost)
        count = 0
        url = f"{self.url_root}games/events?id={amfObj.id}&timezone={settings.TIME_ZONE}"
        self.logger.info(f"URL: {url}")
        response = self.session.get(url)
        seasonObj = Season.objects.get(active=True,vhost=self.vhost)
        if response.status_code == 200:

            data = response.json()
            # print(data)
            for event in data["response"]:
                try:
                    teamObj = Team.objects.get(id=event["team"]["id"], league=amfObj.league,vhost=self.vhost)
                except Team.DoesNotExist:
                    teamObj = Team(id=event["team"]["id"], name=event["team"]["name"], logo=event["team"]["logo"],vhost=self.vhost,
                                   league=amfObj.league)
                    teamObj.save()
                if event["player"]["id"] != None:
                    try:
                        playerObj = Player.objects.get(id=event["player"]["id"])
                    except Player.DoesNotExist:
                        playerObj = Player(id=event["player"]["id"], name=event["player"]["name"],vhost=self.vhost,
                                           image=event["player"]["image"], team=teamObj, season=seasonObj)
                        playerObj.save()
                else:
                    noneId = 6656000 + teamObj.id
                    try:
                        playerObj = Player.objects.get(id=noneId)
                    except Player.DoesNotExist:
                        playerObj = Player(name="none", team=teamObj, season=seasonObj, id=noneId)
                        playerObj.save()

                try:
                    eventObj = AMFGameEvent.objects.get(amf_game=amfObj, quarter=event["quarter"],vhost=self.vhost,
                                                        minute=event["minute"], team=teamObj, player=playerObj,
                                                        season=seasonObj, type=event["type"])
                except AMFGameEvent.DoesNotExist:
                    eventObj = AMFGameEvent(amf_game=amfObj, quarter=event["quarter"], minute=event["minute"],vhost=self.vhost,
                                            team=teamObj, player=playerObj, type=(event["type"] or "event"),
                                            season=seasonObj)
                    eventObj.score = event["score"]
                    eventObj.comment = event["comment"]
                    eventObj.save()

        else:
            self.logger.info(f"Request Result: HTTP {response.status_code}")
            self.logger.info(response)

    def get_player_worker(self,team_id):
        teamObj = Team.objects.get(id=team_id,sport_mask="amf")
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
                    self.logger.info(f"Created/updated Player {playerObj.name}... ")
            teamObj.need_sync_players = False
            teamObj.save()

    def get_player_stats_worker(self,player_id):
        # Step one: Seasons:
        seasonObj = Season.objects.get(active=True,vhost=self.vhost)
        playerObj = Player.objects.get(id=player_id,vhost=self.vhost)
        count = 0
        url = f"{self.url_root}/players/statistics?id={playerObj.id}&season={seasonObj.season_key}&timezone={settings.TIME_ZONE}"
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

    def get_players(self,team_id=False):
        if team_id:
            teams = Team.objects.filter(id=team_id, sport_mask="amf",vhost=self.vhost)
        else:
            teams = Team.objects.filter(sport_mask="amf",vhost=self.vhost)
        for team in teams:
            self.get_player_worker(team.id)

    def fetch_period_fixtures(self,start,stop):
        return self.get_games(date_start=start,date_stop=stop)

    def get_games(self,**kwargs):
        self.logger.warning(f"Getting Games from API.")

        _leagueObj = League.objects.filter(active=True, sport_mask="amf",vhost=self.vhost)
        if (len(_leagueObj) < 1):
            self.logger.warning(
                "There are no Active League objects with an AMF sports mask. Not fetching anything. This is probably -not- what you wanted.")
        for leagueObj in _leagueObj:
            if not "date_start" in kwargs:
                date = datetime.now().strftime("%Y-%m-%d")
                self.get_games_worker(date, leagueObj.id,)
                old_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
                self.get_games_worker(old_date, leagueObj.id, )
            else:
                date_start = datetime.strptime(kwargs["date_start"], "%Y-%m-%d")
                current_date = date_start
                date_end = datetime.strptime(kwargs["date_stop"], "%Y-%m-%d")
                while current_date < date_end:
                    self.get_games_worker(current_date.strftime("%Y-%m-%d"), leagueObj.id, )
                    current_date += timedelta(days=1)




APISportsDriver = APISportsAmericanFootball