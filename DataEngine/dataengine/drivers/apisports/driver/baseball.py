from datetime import datetime, timedelta

from django.conf import settings
from django.db import IntegrityError

from dataengine.drivers.apisports.driver.toolkit import get_api_sports_session, getLogger, get_league_active_season
from dataengine.drivers.apisports.models import Season, Team, Player, League, TeamLeagues, PlayerStats, BABGame, \
    BABGamePlayerStats, BABGameScore, BASEGameScore, BASEGame
# from providers.apisports.tasks.amf import get_teams


class APISportsBaseball(object):
    logger = getLogger("dataengine.drivers.apisports.driver.baseball","basketball.log","apisports")
    url_root = "https://v1.baseball.api-sports.io/"

    def __init__(self, vhost, **kwargs):
        self.vhost = vhost
        self.session, self.api_settings = get_api_sports_session(vhost)

    def _create_team(self,team, leagueObj):
        if "id" and "name" in team:
            teamObj, created = Team.objects.get_or_create(id=team["id"], sport_mask="base",vhost=self.vhost)
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
            self.logger.info(f"Created/updated Team {teamObj.name}...")
            teamLeagueObj, cc = TeamLeagues.objects.get_or_create(league=leagueObj, team=teamObj, sport_mask="base",vhost=self.vhost)
            teamLeagueObj.save()

    def get_games_worker(self,date, league_id, match_id=False):
        if not match_id:
            if not date: date = datetime.now()
            self.logger.info(f"Games Worker for {league_id}/{date}")
        else:
            self.logger.info(f"Games Worker for Match {match_id}")
        # Step one: Seasons:
        self.logger.info(f"Getting Games from API.")
        leagueObj = League.objects.get(id=league_id, sport_mask="base",vhost=self.vhost)
        season, seasonObj = get_league_active_season(leagueObj.seasons,self.vhost)
        if not season:
            self.logger.warning(f"League {leagueObj.name} has no active season: Not continuing.")
        else:

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
                url = f"{self.url_root}games?id={match_id}&timezone={settings.TIME_ZONE}"
            self.logger.info(url)
            # print(url)
            response = self.session.get(url)
            if response.status_code == 200:
                data = response.json()
                # print(url)
                # print(data)
                for game in data["response"]:
                    # print(game)
                    try:
                        home_team = Team.objects.get(id=game["teams"]["home"]["id"], sport_mask="base",vhost=self.vhost)
                    except Team.DoesNotExist:
                        self.logger.warning(
                            f'Team not found: HT: {game["teams"]["home"]["id"]}/{game["teams"]["home"]["name"]} - Creating!')
                        home_team,cc = Team.objects.get_or_create(id=game["teams"]["home"]["id"], sport_mask="base",vhost=self.vhost)
                        home_team.name = game["teams"]["home"]["name"]
                        home_team.save()
                        self.get_teams(game["teams"]["home"]["id"], leagueObj.id)
                        tcc,cc = TeamLeagues.objects.get_or_create(team=home_team, league=leagueObj,vhost=self.vhost)
                        tcc.save()
                    try:
                        away_team = Team.objects.get(id=game["teams"]["away"]["id"], sport_mask="base",vhost=self.vhost)
                    except Team.DoesNotExist:
                        away_team,cc = Team.objects.get_or_create(id=game["teams"]["away"]["id"], sport_mask="base",vhost=self.vhost)
                        away_team.name = game["teams"]["away"]["name"]
                        away_team.save()
                        self.get_teams(game["teams"]["away"]["id"], leagueObj.id)
                        tcc,cc = TeamLeagues.objects.get_or_create(team=away_team, league=leagueObj,vhost=self.vhost)
                        tcc.save()

                    if home_team and away_team:
                        if not match_id:
                            BASEGameObj = \
                            BASEGame.objects.get_or_create(id=game["id"], league=leagueObj, season=seasonObj,vhost=self.vhost)[0]
                        else:
                            BASEGameObj = BASEGame.objects.get(id=match_id,vhost=self.vhost)
                        # print(game)

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
                            "league": leagueObj, }
                        for k, v in data_map.items():
                            setattr(BASEGameObj, k, v)
                        BASEGameObj.save()
                        try:
                            BASEGameHomeScoreObj = BASEGameScore.objects.get(match=BASEGameObj, team=home_team,vhost=self.vhost)
                        except BASEGameScore.DoesNotExist:
                            BASEGameHomeScoreObj = BASEGameScore(match=BASEGameObj, team=home_team,vhost=self.vhost)
                        inning_keys = range(1,10)
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
                        for k, v in data_map.items():
                            setattr(BASEGameHomeScoreObj, k, v)
                        try:
                            BASEGameAwayScoreObj = BASEGameScore.objects.get(match=BASEGameObj, team=away_team,vhost=self.vhost)
                        except BASEGameScore.DoesNotExist:
                            BASEGameAwayScoreObj = BASEGameScore(match=BASEGameObj, team=away_team,vhost=self.vhost)
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
                        for k, v in data_map.items():
                            setattr(BASEGameAwayScoreObj, k, v)
                        sys_event = False
                        sys_link = False
                        BASEGameAwayScoreObj.save()
                        BASEGameHomeScoreObj.save()

            else:
                # TODO: Feex me
                spammer = False
                if spammer:
                    print(response.status_code)
                    print(response)

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
                leagueObj = League.objects.get_or_create(id=league["id"],sport_mask="base",vhost=self.vhost)[0]
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
                leagueObj.save()
                self.logger.info(f"Created/updated League {leagueObj.name}... (Currently inactive)")

    def get_players(self,team_id=False):
        # Not yet implemented
        pass

    def fetch_period_fixtures(self,start,stop):
        return self.get_games(date_start=start,date_stop=stop)

    def get_games(self,**kwargs):
        self.logger.warning(f"Getting Games from API.")
        date = datetime.now().strftime("%Y-%m-%d")
        _leagueObj = League.objects.filter(active=True, sport_mask="base",vhost=self.vhost)
        if (len(_leagueObj) < 1):
            self.logger.warning(
                "There are no Active League objects with an BASE sports mask. Not fetching anything. This is probably -not- what you wanted.")
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

APISportsDriver = APISportsBaseball
