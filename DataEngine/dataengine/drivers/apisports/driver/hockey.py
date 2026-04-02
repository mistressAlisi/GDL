from datetime import datetime, timedelta
from time import timezone

from django.conf import settings
from django.db import IntegrityError

from dataengine.drivers.apisports.driver.toolkit import get_api_sports_session, getLogger, get_league_active_season
from dataengine.drivers.apisports.models import Season, Team, Player, League, TeamLeagues, PlayerStats, Venue, \
    TeamVenue, FBALLPlayerStats, FBALLGame, FBALLGameScore, HOCKGame, HOCKGameScore
# from providers.apisports.tasks.amf import get_teams


class APISportsHockey(object):
    logger = getLogger("dataengine.drivers.apisports.driver.hockey","hockey.log","apisports")
    url_root = "https://v1.hockey.api-sports.io/"

    def __init__(self, vhost, **kwargs):
        self.vhost = vhost
        self.session, self.api_settings = get_api_sports_session(vhost)

    def get_leagues(self,arg=False):
        # Step one: Seasons:
        self.logger.info(f"Getting seasons from API Sports.")
        url = f"{self.url_root}leagues"
        response = self.session.get(url)
        if response.status_code == 200:
            data = response.json()
            for league in data["response"]:
                # print(league)
                leagueObj = League.objects.get_or_create(id=league["id"], sport_mask="hock",vhost=self.vhost)[0]
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
                leagueObj.save()
                self.logger.info(f"Created/updated League {leagueObj.name}... (Currently inactive)")

    def _create_team(self,team, leagueObj):
        if "id" and "name" in team:
            teamObj, created = Team.objects.get_or_create(id=team["id"], sport_mask="hock",vhost=self.vhost)
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
            if "arena" in team:
                teamObj.stadium = team["arena"]
            teamObj.save()
            self.logger.info(f"Created/updated Team {teamObj.name}")
            teamLeagueObj, cc = TeamLeagues.objects.get_or_create(league=leagueObj, team=teamObj, sport_mask="hock",vhost=self.vhost)
            teamLeagueObj.save()

    def fetch_period_fixtures(self,start,stop):
        return self.get_games(date_start=start,date_stop=stop)

    def get_teams(self,team_id=False, league_id=False):
        # Step one: Seasons:
        self.logger.info(f"Getting Teams from API Sports.")
        if not league_id:
            _leagueObj = League.objects.filter(active=True, sport_mask="hock",vhost=self.vhost).order_by("-id")
        else:
            _leagueObj = League.objects.filter(active=True, sport_mask="hock", id=league_id,vhost=self.vhost).order_by("-id")
        if (len(_leagueObj) < 1):
            self.logger.warning(
                "There are no Active League objects with a HOCK sports mask. Not fetching anything. This is probably -not- what you wanted.")
        for leagueObj in _leagueObj:
            self.logger.info(f"Processing League: {leagueObj.id}/{leagueObj.name}")
            season, seasonObj = get_league_active_season(leagueObj.seasons,self.vhost)
            if not season:
                self.logger.warning(f"League {leagueObj.name} has no active season: Not continuing.")
                return False
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
                # print(data)
                for team in data["response"]:
                    # print(team)
                    self._create_team(team, leagueObj)

    def get_games_worker(self,date, league_id, match_id=False):
        if not match_id:
            if not date: date = datetime.now()
            self.logger.info(f"Games Worker for {league_id}/{date}")
        else:
            self.logger.info(f"Games Worker for Match {match_id}")
        # Step one: Seasons:
        self.logger.info(f"Getting Games from API.")
        leagueObj = League.objects.get(id=league_id, sport_mask="hock",vhost=self.vhost)
        season, seasonObj = get_league_active_season(leagueObj.seasons,self.vhost)
        if not season:
            self.logger.warning(f"League {leagueObj.name} has no active season: Not continuing.")
        else:
            self.logger.warning(f"Processing League {leagueObj.name}")

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
            if not match_id:
                url = f"{self.url_root}games?league={leagueObj.id}&season={seasonStr}&date={date}&timezone={settings.TIME_ZONE}"
            else:
                url = f"{self.url_root}/games?id={match_id}"
            self.logger.info(url)
            response = self.session.get(url)
            if response.status_code == 200:
                data = response.json()
                # print(url)
                # print(data)
                for game in data["response"]:
                    # print(game)
                    try:
                        home_team = Team.objects.get(id=game["teams"]["home"]["id"], sport_mask="hock",vhost=self.vhost)
                    except Team.DoesNotExist:
                        self.logger.warning(
                            f'Team not found: HT: {game["teams"]["home"]["id"]}/{game["teams"]["home"]["name"]} - Creating!')
                        self.get_teams(game["teams"]["home"]["id"], leagueObj.id)
                        home_team = Team.objects.get(id=game["teams"]["home"]["id"], sport_mask="hock",vhost=self.vhost)
                    try:
                        away_team = Team.objects.get(id=game["teams"]["away"]["id"], sport_mask="hock",vhost=self.vhost)
                    except Team.DoesNotExist:
                        self.logger.warning(
                            f'Team not found: AT: {game["teams"]["away"]["id"]}/{game["teams"]["away"]["name"]} - Creating!')
                        self.get_teams(game["teams"]["away"]["id"], leagueObj.id)
                        away_team = Team.objects.get(id=game["teams"]["away"]["id"], sport_mask="hock",vhost=self.vhost)

                    if home_team and away_team:
                        if not match_id:
                            HOCKGameObj = HOCKGame.objects.get_or_create(id=game["id"], season=seasonObj)[0]
                        else:
                            HOCKGameObj = HOCKGame.objects.get(id=match_id)

                        data_map = {
                            # "stage": game["stage"],
                            "week": game["week"],
                            "commence_time": datetime.fromisoformat(game["date"]),
                            # "venue": game["venue"],
                            # "city": game["venue"]["city"],
                            "status_short": game["status"]["short"],
                            "status_long": game["status"]["long"],
                            "status_timer": game["time"],
                            "home_team": home_team,
                            "away_team": away_team,
                            "league": leagueObj,
                        }
                        for k, v in data_map.items():
                            setattr(HOCKGameObj, k, v)
                        HOCKGameObj.save()
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
                            HOCKGameHomeScoreObj = HOCKGameScore.objects.get(match=HOCKGameObj, team=home_team,vhost=self.vhost)
                        except HOCKGameScore.DoesNotExist:
                            HOCKGameHomeScoreObj = HOCKGameScore(match=HOCKGameObj, team=home_team,vhost=self.vhost)
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
                            HOCKGameAwayScoreObj = HOCKGameScore.objects.get(match=HOCKGameObj, team=away_team,vhost=self.vhost)
                        except HOCKGameScore.DoesNotExist:
                            HOCKGameAwayScoreObj = HOCKGameScore(match=HOCKGameObj, team=away_team,vhost=self.vhost)
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
                        HOCKGameAwayScoreObj.save()
                        HOCKGameHomeScoreObj.save()

            else:
                # TODO: Feex me
                spammer = False
                if spammer:
                    print(response.status_code)
                    print(response)


    def get_players(self,team_id=False):
        # Not yet implemented
        pass

    def get_games(self,**kwargs):
        self.logger.warning(f"Getting Games from API.")
        date = datetime.now().strftime("%Y-%m-%d")
        _leagueObj = League.objects.filter(active=True, sport_mask="hock",vhost=self.vhost)
        if (len(_leagueObj) < 1):
            self.logger.warning(
                "There are no Active League objects with an HOCK sports mask. Not fetching anything. This is probably -not- what you wanted.")
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


APISportsDriver = APISportsHockey