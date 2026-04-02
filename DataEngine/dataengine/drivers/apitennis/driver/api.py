import re
from datetime import datetime, timedelta
from decimal import Decimal

import pytz
from django import db
from django.conf import settings
from django.db.models import Q
from django.utils.text import slugify
from logging import getLogger

from dataengine.drivers.apitennis.driver.daemons.apitennishttpd import APITennisHTTPd
from dataengine.drivers.apitennis.models.fixtures import Fixture
from dataengine.drivers.apitennis.models.players import Players
from dataengine.drivers.apitennis.models.tournaments import Tournament
from dataengine.drivers.kiblio.models import Participant
from dataengine.models import MatchSyncStatus


class DataEngineDriverAPI(object):
    PKEY_MODEL_MAPPINGS = {
        "match":"routing_key",
        "outcome":"routing_key",
        "outcome_segment":"routing_key",

    }
    dbobj_name =  {
        "sport":"apitennis.tournament.Tournament",
        "group":"apitennis.driver",
        "team": "apitennis.players.Player",
        "match":"apitennis.fixture.Fixture",
        "mkt_summary":""
    }
    get_apiobj_map =  {
        "apitennis.tournament.Tournament":Tournament,
        "apitennis.players.Player":Players,
        "apitennis.fixture.Fixture":Fixture,
    }
    vhost = False
    logger = getLogger("dataengine.drivers.apitennis.driver.api")
    name = "dataengine.drivers.apitennis"
    def __init__(self,vhost,**kwargs):
        self.vhost = vhost
        self.logger.info(f"APITennis driver on {self.vhost} DataEngine Driver Loaded!")

    def get_api_object(self,type,uuid):
        if type not in self.get_apiobj_map: return False
        try:
            return self.get_apiobj_map[type].objects.get(vhost=self.vhost,pk=uuid)
        except self.get_apiobj_map[type].DoesNotExist: return False

    def get_api_teams(self):
        players = Players.objects.all().order_by("player_name")
        teams = []
        for player in players:
            teams.append({"value":str(player.uuid),"label":player.player_name})
        return teams


    def get_api_matches(self,home_team_uuid,away_team_uuid,commence_date):
        # Find fixtures that match the parameters:
        # print(commence_date)
        c_lower = commence_date - timedelta(days=-1)
        c_upper = commence_date - timedelta(days=1)
        # print(c_upper,c_lower)
        player_1 = Players.objects.get(vhost=self.vhost,uuid=home_team_uuid)
        player_2 = Players.objects.get(vhost=self.vhost,uuid=away_team_uuid)
        fixtures = Fixture.objects.filter(vhost=self.vhost,event_first_player=player_1,event_second_player=player_2,commence_time__gte=c_lower,commence_time__lte=c_upper)
        matches = []
        for f in fixtures:
            matches.append({"value":str(f.uuid),"label":f.get_name()})
        fixtures = Fixture.objects.filter(vhost=self.vhost, event_first_player=player_2, event_second_player=player_1,commence_time__gte=c_lower,commence_time__lte=c_upper)
        for f in fixtures:
            matches.append({"value":str(f.uuid),"label":f.get_name()})
        return matches

    def update_all(self):
        self.logger.info(f"APITennis driver on {self.vhost} Updating Fixture Data!")
        apiObj = APITennisHTTPd(self.vhost)

        # ....and from here we go to fixtures in play:
        _fixture = apiObj.fetch_upcoming_fixtures()

    def shorten_first_name(self,full_name: str) -> str:
        return re.sub(r'^(\w)\w*\s+(\w+)$', r'\1. \2', full_name)

    def find_match(self,**kwargs):
        # First, let's find the group and sport:
        # print(kwargs)
        if "group_obj" not in kwargs:
            if not "group_slug" != kwargs:
                return False, "GROUP"
            if kwargs["group_slug"] != "TN":
                return False, "NOT_SUPPORTED_GROUP"
        group = self.get_sports_groups()[0]
        tournament = False
        if "sport_obj" in kwargs:
            tournament = Tournament.objects.get(Q(vhost=self.vhost)&Q(uuid=kwargs["sport_obj"]))
        elif "sport_key" in kwargs:
            tournaments = Tournament.objects.filter(
                Q(vhost=self.vhost) & Q(tournament_key__icontains=kwargs["sport_key"]))
            tournament = tournaments.first()

        if ("sport_title" in kwargs) and (not tournament):
            tournaments = Tournament.objects.filter(Q(vhost=self.vhost)&Q(tournament_name__icontains=kwargs["sport_name"]))
            tournament = tournaments.first()
        if "home_team_obj" in kwargs:
            home_team = Players.objects.get(vhost=self.vhost, uuid=kwargs["home_team_obj"])
        elif "home_team_name" in kwargs:
            sht_name = self.shorten_first_name(kwargs["home_team_name"])
            _home_team = Players.objects.filter(Q(vhost=self.vhost) & (Q(player_name__icontains=kwargs["home_team_name"])|(Q(player_name__icontains=sht_name))))
            if len(_home_team) < 1:
                return False, "HOME_TEAM"
            home_team = _home_team[0]
        if "away_team_obj" in kwargs:
            away_team = Players.objects.get(vhost=self.vhost, uuid=kwargs["away_team_obj"])
        elif "away_team_name" in kwargs:
            sht_name = self.shorten_first_name(kwargs["away_team_name"])
            _away_team = Players.objects.filter(Q(vhost=self.vhost) & (Q(player_name__icontains=kwargs["away_team_name"]))|(Q(player_name__icontains=sht_name)))
            if len(_away_team) < 1:
                return False, "AWAY_TEAM"
            away_team = _away_team[0]
        qkwargs = {"vhost":self.vhost}
        if tournament:
            qkwargs["tournament"] = tournament
        match_dt = kwargs["commence_time"].strftime("%Y-%m-%d")
        match = Fixture.objects.filter(**qkwargs).filter(Q(event_date=match_dt)
                                                          &(Q(event_first_player=home_team) & Q(event_second_player=away_team))|
                                                          (Q(event_first_player=away_team) & Q(event_second_player=home_team)))
        if (len(match) < 1):
            return False, "MATCH"
        else:
            retdata = {
                "match": {
                    "match": match[0],
                    "object_uuid": match[0].uuid,
                    "object_type": f"{match[0]._meta.app_label}.{match[0]._meta.model_name}.{match[0]._meta.object_name}",
                },

                "group": group,
                "home_team": {
                    "team": home_team,
                    "object_uuid": home_team.uuid,
                    "object_type": f"{home_team._meta.app_label}.{home_team._meta.model_name}.{home_team._meta.object_name}",
                },
                "away_team": {
                    "team": away_team,
                    "object_uuid": away_team.uuid,
                    "object_type": f"{away_team._meta.app_label}.{away_team._meta.model_name}.{away_team._meta.object_name}",
                },
            }
            if tournament:
                retdata["sport"]  = {
                    "sport": tournament,
                    "object_uuid": tournament.uuid,
                    "object_type": f"{tournament._meta.app_label}.{tournament._meta.model_name}.{tournament._meta.object_name}",
                }
            return True, retdata



    def get_sports_groups(self):
        groups = [{
                "id":self.vhost.uuid,
                "slug":'TN',
                "name":'Tennis',
                "inserted_on":None,
                "inserted_on_epoch":None,
                "object_uuid":self.vhost.uuid,
                "object_type": 'apitennis.driver',
            }]
        return groups


    def get_sports_seasons(self):
        seasons = []
        return seasons


    def get_sports_sports(self):
        sports = []
        self.logger.info(f"Getting Active APITennis Leagues, presenting as Sports to DataEngine...")
        tournamentObjs = Tournament.objects.filter(vhost=self.vhost)
        for s in tournamentObjs:
            if s.tournament_key != None:
                key = s.tournament_key
            else:
                key = slugify(s.tournament_name)
            sport = {
                "id":s.uuid,
                "key":key,
                "title":s.tournament_name,
                "logo":None,
                "group":None,
                "sport_mask":None,
                "group_type": 'apitennis.driver',
                "group_uuid": self.vhost.uuid,
                "inserted_on":s.inserted_on,
                "inserted_on_epoch":None,
                "object_uuid":s.uuid,
                "object_type": f"{s._meta.app_label}.{s._meta.model_name}.{s._meta.object_name}"
            }
            sports.append(sport)
        return sports


    def get_teams(self):
        teams = []
        self.logger.info(f"Getting Active APITennis Participants, presenting as Teams to DataEngine...")
        participantObjs = Players.objects.filter(vhost=self.vhost)
        for s in participantObjs:
            if s.player_key != None:
                key = s.player_key
            else:
                key = slugify(s.player_name)
            sport = {
                "id":s.uuid,
                "key":key,
                "name":s.player_name,
                "country":s.player_country,
                "bday":s.player_bday,
                "logo":s.player_logo,
                "mascot": None,
                "parent_team":None,
                "inserted_on":s.inserted_on,
                "sport": None,
                "sport_type": None,
                "sport_uuid": None,
                "object_uuid":s.uuid,
                "object_type": f"{s._meta.app_label}.{s._meta.model_name}.{s._meta.object_name}"
            }
            teams.append(sport)
        return teams

    def get_segments(self):
        segments = []

        return segments

    def get_venues(self):
        """ Stubbed!"""
        return []

    def get_updated_synced_matches_index(self,update_at):
        fixtures = []
        fixtureObjs = Fixture.objects.filter(
            vhost=self.vhost,  # restrict to the current vhost
            updated_on__gte=update_at,
            uuid__in=MatchSyncStatus.objects.filter(
                driver_object_type="apitennis.fixture.Fixture"
            ).values("driver_object_uuid")
        )
        # print("aaaaa")
        # print(pytz.timezone(settings.TIME_ZONE).localize(update_at))
        # print(fixtureObjs)

        for f in fixtureObjs:
            fd = {
                "id":f.event_key,
                "object_uuid": f.uuid,
                "object_type": f"{f._meta.app_label}.{f._meta.model_name}.{f._meta.object_name}",
            }
            fixtures.append(fd)
        return fixtures

    def get_matches(self,**kwargs):
        matches = []
        if "sync_update_at" in kwargs:
            update_at = kwargs["sync_update_at"]

            fixtureObjs = Fixture.objects.filter(
                vhost=self.vhost,  # restrict to the current vhost
                updated_on__gte=update_at,
                uuid__in=MatchSyncStatus.objects.filter(
                    vhost=self.vhost,
                    driver_object_type="apitennis.fixture.Fixture"
                ).values("driver_object_uuid")
            )
            # print(fixtureObjs)
        elif "provider_match_uuid" in kwargs:
            fixtureObjs = Fixture.objects.filter(vhost=self.vhost,uuid=kwargs["provider_match_uuid"])
            self.logger.info(
                f"Getting Active APITennis Matches that match passed UUID: presenting as Matches to DataEngine...")
        elif "provider_match_objs" in kwargs:
            self.logger.info(f"Getting Active APITennis Fixtures with passed match (fixture) objects: presenting as Matches to DataEngine...")
            fixtureObjs = kwargs["provider_match_objs"]
        else:
            self.logger.info(f"Getting Active APITennis Fixtures, presenting as Matches to DataEngine...")
            fixtureObjs = Fixture.objects.filter(vhost=self.vhost)
        for f in fixtureObjs:

            # print(f.state)
            finished = False
            if f.event_status:
                status_short = f.event_status
                status_long = f.event_status
            else:
                status_short = "UPC"
                status_long = "Upcoming"
            if f.event_status in ["Finished","Retired","Walk Over"]:
                finished = True
            commence_time = datetime.strptime(f"{f.event_date}T{f.event_time}", "%Y-%m-%dT%H:%M:%S")
            match = {
                "id":f.event_key,
                "object_uuid": f.uuid,
                "object_type": f"{f._meta.app_label}.{f._meta.model_name}.{f._meta.object_name}",
                "commence_time":commence_time,
                "name":f"{f.event_first_player.player_name} vs {f.event_second_player.player_name}",
                "routing_key": None,
                "inserted_on":f.inserted_on,
                "inserted_on_epoch":None,
                "home_team_type":f"{f.event_first_player._meta.app_label}.{f.event_first_player._meta.model_name}.{f.event_first_player._meta.object_name}",
                "home_team_uuid":f.event_first_player.uuid,
                "away_team_type": f"{f.event_second_player._meta.app_label}.{f.event_second_player._meta.model_name}.{f.event_second_player._meta.object_name}",
                "away_team_uuid": f.event_second_player.uuid,
                "sport_type": f"{f.tournament._meta.app_label}.{f.tournament._meta.model_name}.{f.tournament._meta.object_name}",
                "sport_uuid": f.tournament.uuid,
                "season_type": None,
                "season_uuid": None,
                "status_short":status_short,
                "status_long":status_long,
                "status_timer":None,
                "finished": finished

            }
            matches.append(match)
            # else:
            #     print(FixtureParticipants.objects.filter(vhost=self.vhost,fixture=f))
            #     print(f"This is strange, {f}: HT {hTeObj}, AT: {aTeObj}")
        return matches

    def get_match_odds_ml(self,**kwargs):
      return []

    def get_outcomes(self, **kwargs):
        all_outcomes = []
        if "sync_update_at" in kwargs:
            update_at = kwargs["sync_update_at"]
            fixtureObjs = Fixture.objects.filter(
                vhost=self.vhost,  # restrict to the current vhost
                updated_on__gt=update_at,
                uuid__in=MatchSyncStatus.objects.filter(
                    vhost=self.vhost,
                    driver_object_type="apitennis.fixture.Fixture"
                ).values("driver_object_uuid")
            )
        elif "provider_match_uuid" in kwargs:
            fuuid = kwargs["provider_match_uuid"]
            self.logger.info(
                f"Getting Active APITennis Fixture {fuuid}: Outcomes, presenting as Outcomes, OutcomeSegments and OutcomeParticipants to DataEngine...")
            fixtureObjs = Fixture.objects.filter(vhost=self.vhost,uuid=fuuid)
        elif "provider_match_objs" in kwargs:
            self.logger.info(
                f"Getting Active APITennis Outcomes with passed match (fixture) objects: presenting  Outcomes, OutcomeSegments and OutcomeParticipants to DataEngine...")
            fixtureObjs = kwargs["provider_match_objs"]
        else:
            self.logger.info(f"Getting Active APITennis Outcomes, presenting as Outcomes, OutcomeSegments and OutcomeParticipants to DataEngine...")
            fixtureObjs = Fixture.objects.filter(vhost=self.vhost)
        outcomes = []
        for f in fixtureObjs:
            # print(f'Fixture: {f.uuid}: SS: {f.event_status}')
            outcome = {
                "id": f.uuid,
                "apiid":None,
                "apitennisid":f.event_key,
                "object_uuid": f.uuid,
                "object_type": f"{f._meta.app_label}.{f._meta.model_name}.{f._meta.object_name}",
                "fixture_uuid": f.uuid,
                "fixture_type": f"{f._meta.app_label}.{f._meta.model_name}.{f._meta.object_name}",
                "segment_uuid": None,
                "segment_type": None,
                "segment":None,
                "state_id":f.event_status,
                "status_long": f.event_status,
                "status_short": f.event_status,
                "routing_key": "",
                "inserted_on": f.inserted_on,
                "clock": f.event_time,
                "is_current": None,
                "is_start_game": None,
                "is_end_game": None,
                "is_start_segment": None,
                "is_end_segment": None,
                "segments":[],
                "teams":[]
            }
            first_score = 0
            second_score = 0
            for score in f.scores:
                set = f'Set {score["score_set"]}'
                first = Decimal(score["score_first"])
                second = Decimal(score["score_second"])
                first_set = 0
                second_set = 0
                if first == 0 and second == 0:
                    continue
                if first > second:
                    fw = True
                    sw = False
                    first_score += 1
                    first_set  = 1
                else:
                    fw = False
                    sw = True
                    second_score += 1
                    second_set = 1
                # print(f"APITennis Debugging: First {first}, First_set: {first_set}, Second: {second}, FW: {fw}, SW: {sw}, second_Set: {second_set}")
                so = {
                    "id": f.uuid,
                    "object_uuid":f.uuid,
                    "object_type":f"{f._meta.app_label}.{f._meta.model_name}.{f._meta.object_name}",
                    "segment_uuid": self.vhost.uuid,
                    "segment_type": set,
                    "segment": set,
                    "team_uuid":f.event_first_player.uuid,
                    "team_type": f"{f.event_first_player._meta.app_label}.{f.event_first_player._meta.model_name}.{f.event_first_player._meta.object_name}",
                    "routing_key": None,
                    "score": first_set,
                    "is_winner": fw,
                    "state_id": None,
                    "inserted_on": f.inserted_on,
                }
                outcome["segments"].append(so)
                so = {
                    "id": f.uuid,
                    "object_uuid": f.uuid,
                    "object_type": f"{f._meta.app_label}.{f._meta.model_name}.{f._meta.object_name}",
                    "segment_uuid": self.vhost.uuid,
                    "segment_type": set,
                    "segment": set,
                    "team_uuid": f.event_second_player.uuid,
                    "team_type": f"{f.event_second_player._meta.app_label}.{f.event_second_player._meta.model_name}.{f.event_second_player._meta.object_name}",
                    "routing_key": None,
                    "score": second_set,
                    "is_winner": fw,
                    "state_id": None,
                    "inserted_on": f.inserted_on,
                }
                outcome["segments"].append(so)
            if first_score > second_score:
                fw = True
                sw = False
            else:
                fw = False
                sw = True
            po = {
                "id": f.uuid,
                "team_uuid": f.event_first_player.uuid,
                "team_type":f"{f.event_first_player._meta.app_label}.{f.event_first_player._meta.model_name}.{f.event_first_player._meta.object_name}",
                "score": first_score,
                "is_winner": fw,
                "inserted_on": f.inserted_on,
                "routing_key": None,
                "object_uuid": f.uuid,
                "object_type": f"{f._meta.app_label}.{f._meta.model_name}.{f._meta.object_name}",
            }
            outcome["teams"].append(po)
            po = {
                "id": f.uuid,
                "team_uuid": f.event_second_player.uuid,
                "team_type":f"{f.event_second_player._meta.app_label}.{f.event_second_player._meta.model_name}.{f.event_first_player._meta.object_name}",
                "score": second_score,
                "is_winner": sw,
                "inserted_on": f.inserted_on,
                "routing_key": None,
                "object_uuid": f.uuid,
                "object_type": f"{f._meta.app_label}.{f._meta.model_name}.{f._meta.object_name}",

            }
            outcome["teams"].append(po)
            outcomes.append(outcome)
        return outcomes