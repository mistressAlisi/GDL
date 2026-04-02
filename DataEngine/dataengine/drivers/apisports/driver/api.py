import pytz
from django import db
from django.conf import settings
from django.db.models import Q
from django.utils.text import slugify
from logging import getLogger

from dataengine.drivers.apisports.models import Season, League, Team, TeamLeagues, Venue, AMFGame, BABGame, BASEGame, \
    FBALLGame, HOCKGame, AMFGameScore, BABGameScore, BASEGameScore, FBALLGameScore, HOCKGameScore
from dataengine.models import MatchSyncStatus


class DataEngineDriverAPI(object):
    PKEY_MODEL_MAPPINGS = {
        "match":"routing_key",
        "outcome":"routing_key",
        "outcome_segment":"routing_key",

    }
    dbobj_name =  {
        "sport":"apisports.league.League",
        "group":"apisports.group",
        "team":"apisports.team.Team",
        "match":"apisports.match.*",
        "mkt_summary":""

    }

    get_apiobj_map =  {
        "apisports.league.League":League,
        "apisports.team.Team":Team,
        # "apisports.match.*":""
    }
    vhost = False
    GAME_CLASSES = [AMFGame,BABGame,BASEGame,FBALLGame,HOCKGame]
    logger = getLogger("dataengine.drivers.apisports.driver.api")
    name = "dataengine.drivers.apisports"
    groups = {"AF":{"n":"American Football"},
              "BB":{"n":"Baseball"},
              "BK":{"n":"Basketball"},
              "IH":{"n":"Ice Hockey"},
              "SC":{"n":"Soccer"},
              }
    def __init__(self,vhost,**kwargs):
        self.vhost = vhost
        self.logger.info(f"APISports.io driver on {self.vhost} DataEngine Driver Loaded!")

    def get_api_object(self,type,uuid):
        if type not in self.get_apiobj_map: return False
        try:
            return self.get_apiobj_map[type].objects.get(pk=uuid)
        except self.get_apiobj_map[type].DoesNotExist: return False

    def get_sports_groups(self):
        groups = []
        for entry in self.groups:
            groups.append({
                    "id":self.vhost.uuid,
                    "slug":entry,
                    "name":self.groups[entry]["n"],
                    "inserted_on":None,
                    "inserted_on_epoch":None,
                    "object_uuid":self.vhost.uuid,
                    "object_type": f"apisports.driver.{entry}",
            })
        return groups

    def get_sports_seasons(self):
        seasons = []
        self.logger.info(f"Getting Active APISports.io Seasons, presenting as seasons to DataEngine...")
        seasonObjs = Season.objects.filter(vhost=self.vhost)
        for s in seasonObjs:
            group = {
                "id":s.uuid,
                "season_key":s.season_key,
                "name":s.season_key,
                "object_uuid":s.uuid,
                "object_type": f"{s._meta.app_label}.{s._meta.model_name}.{s._meta.object_name}"
            }
            seasons.append(group)
        return seasons

    def get_sports_sports(self):
        sports = []
        self.logger.info(f"Getting Active APISports Leagues, presenting as Sports to DataEngine...")
        leagueObjs = League.objects.filter(vhost=self.vhost,active=True)
        for s in leagueObjs:
            key = slugify(s.name)
            sport = {
                "id":s.id,
                "key":s.id,
                "title":s.name,
                "logo":s.logo,
                "group":None,
                "sport_mask":s.sport_mask,
                "group_type": s.sync_sport_mask,
                "group_uuid":self.vhost.uuid,
                "inserted_on":s.created_at,
                "inserted_on_epoch":None,
                "object_uuid":s.uuid,
                "object_type": f"{s._meta.app_label}.{s._meta.model_name}.{s._meta.object_name}"
            }
            sports.append(sport)
        return sports


    # FIXME: Don't stub me, bro!
    def get_api_matches(self,home_team_uuid,away_team_uuid,commence_date):
        return False

    def get_teams(self):
        teams = []
        self.logger.info(f"Getting Active APISports Participants, presenting as Teams to DataEngine...")
        participantObjs = Team.objects.filter(vhost=self.vhost)
        for s in participantObjs:
            if s.name is None:
                continue
            league = TeamLeagues.objects.filter(team=s).first()

            key = f"{s.id}-{slugify(s.name)}"
            sport = {
                "id":s.id,
                "key":key,
                "name":s.name,
                "country": None,
                "bday": None,
                "logo": None,
                "mascot": None,
                "parent_team":None,
                "inserted_on":s.created_at,
                "sport": league
            }
            if league:
                sport.update({
                    "sport_type": f"{league._meta.app_label}.{league._meta.model_name}.{league._meta.object_name}",
                    "sport_uuid": league.uuid,
                    "object_uuid":s.uuid,
                    "object_type": f"{s._meta.app_label}.{s._meta.model_name}.{s._meta.object_name}"
                })
            teams.append(sport)
        return teams

    def get_segments(self):
        """ Stubbed!"""
        return []


    def get_venues(self):
        venues = []
        self.logger.info(f"Getting Active APISports Venues, presenting as Venues to DataEngine...")
        venueObjs = Venue.objects.filter(vhost=self.vhost)
        for s in venueObjs:
            ven = {
                "id":s.id,
                "name":s.name,
                "address": s.address,
                "city": s.city,
                "capacity": s.capacity,
                "surface": s.surface,
                "image": s.image,
                "object_uuid":s.uuid,
                "object_type": f"{s._meta.app_label}.{s._meta.model_name}.{s._meta.object_name}"
            }
            venues.append(ven)
        return venues
    def find_match(self,**kwargs):
        # First, let's find the group and sport:
        # print(kwargs)
        if "group_obj" not in kwargs:
            if not "group_slug" in kwargs:
                return False,"GROUP"
            if kwargs["group_slug"] not in self.groups.keys():
                return False, "NOT_SUPPORTED_GROUP"
            group = self.groups[kwargs["group_slug"]]
        league = False
        if "sport_obj" in kwargs:
            league = League.objects.get(Q(vhost=self.vhost)&Q(uuid=kwargs["sport_obj"]))
        elif "sport_title" in kwargs:
            leagues = League.objects.filter(Q(vhost=self.vhost)&Q(name__icontains=kwargs["sport_name"]))
            league = leagues.first()
        if "home_team_obj" in kwargs:
            home_team = Team.objects.get(vhost=self.vhost,uuid=kwargs["home_team_obj"])
        elif "home_team_name" in kwargs:
            _home_team = Team.objects.filter(Q(vhost=self.vhost) & Q(name__icontains=kwargs["home_team_name"]))
            if len(_home_team) < 1:
                return False,"HOME_TEAM"
            home_team = _home_team[0]
        if "away_team_obj" in kwargs:
            away_team = Team.objects.get(vhost=self.vhost,uuid=kwargs["away_team_obj"])
        elif "away_team_name" in kwargs:
            _away_team = Team.objects.filter(Q(vhost=self.vhost) & Q(name__icontains=kwargs["away_team_name"]))
            if len(_away_team) < 1:
                return False,"AWAY_TEAM"
            away_team = _away_team[0]
        qkwargs = {"vhost":self.vhost}
        if league:
            qkwargs["league"] = league
        match = False
        for gc in self.GAME_CLASSES:
            _match = gc.objects.filter(**qkwargs).filter(Q(commence_time=kwargs["commence_time"])&(Q(home_team=home_team) & Q(away_team=away_team))|(Q(home_team=away_team) & Q(away_team=home_team)))
            if (len(_match) > 0):
                match = _match[0]
        if not match:
            return False,"NO_MATCH"
        retdata =  {
            "match":{
                "match":match,
                "object_uuid": match.uuid,
                "object_type": f"{match._meta.app_label}.{match._meta.model_name}.{match._meta.object_name}",
            },
            "sport":{
                "sport":match.league,
                "object_uuid": match.league.uuid,
                "object_type": f"{match.league._meta.app_label}.{match.league._meta.model_name}.{match.league._meta.object_name}",
            },
            "group": group,
            "home_team":{
                "team":home_team,
                "object_uuid": home_team.uuid,
                "object_type": f"{home_team._meta.app_label}.{home_team._meta.model_name}.{home_team._meta.object_name}",
            },
            "away_team": {
                "team": away_team,
                "object_uuid": away_team.uuid,
                "object_type": f"{away_team._meta.app_label}.{away_team._meta.model_name}.{away_team._meta.object_name}",
            },

        }

        return True,retdata

    def _format_match(self, f):
        """Helper to standardize match dict construction"""
        return {
            "id": f.uuid,
            "object_uuid": f.uuid,
            "object_type": f"{f._meta.app_label}.{f._meta.model_name}.{f._meta.object_name}",
            "commence_time": f.commence_time,
            "name": None,
            "routing_key": None,
            "apiid": f.id,
            "inserted_on": f.created_at,
            "inserted_on_epoch": "None",
            "home_team_type": f"{f.home_team._meta.app_label}.{f.home_team._meta.model_name}.{f.home_team._meta.object_name}",
            "home_team_uuid": f.home_team.uuid,
            "away_team_type": f"{f.away_team._meta.app_label}.{f.away_team._meta.model_name}.{f.away_team._meta.object_name}",
            "away_team_uuid": f.away_team.uuid,
            "sport_type": f"{f.league._meta.app_label}.{f.league._meta.model_name}.{f.league._meta.object_name}",
            "sport_uuid": f.league.uuid,
            "season_type": f"{f.season._meta.app_label}.{f.season._meta.model_name}.{f.season._meta.object_name}",
            "season_uuid": f.season.uuid,
            "status_short": f.status_short,
            "status_long": f.status_long,
            "status_timer": f.status_timer,
        }

    def get_updated_synced_matches_index(self,update_at):
        allfixtures = []
        for cls in self.GAME_CLASSES:
            # Subquery for this class (driver_object_type must match fully qualified path)
            subquery = MatchSyncStatus.objects.filter(
                driver_object_type="apisports.match.*",
            ).values("driver_object_uuid")
            # print(update_at)
            # print(subquery)
            fixtures = cls.objects.filter(
                vhost=self.vhost,
                updated_at__gte=update_at,
                uuid__in=subquery,
            )
            # print(fixtures)
            for f in fixtures:
                fd = {
                    "id":f.id,
                    "object_uuid": f.uuid,
                    "object_type": f"{f._meta.app_label}.{f._meta.model_name}.{f._meta.object_name}",
                }
                allfixtures.append(fd)
        # print(allfixtures)
        return allfixtures

    def get_matches(self, **kwargs):
        matches = []

        # Base query constraints
        if "provider_match_uuid" in kwargs:
            qkwargs = {"vhost": self.vhost, "uuid": kwargs["provider_match_uuid"]}
            self.logger.info(
                "Getting Active APISports Matches that match passed UUID: presenting as Matches to DataEngine..."
            )
        else:
            qkwargs = {"vhost": self.vhost}
            self.logger.info(
                "Getting Active APISports Matches, presenting as Matches to DataEngine..."
            )

        # Handle incremental sync using update_at timestamp
        update_at = kwargs.get("sync_update_at")
        if update_at:
            for cls in self.GAME_CLASSES:
                # Subquery for this class (driver_object_type must match fully qualified path)
                subquery = MatchSyncStatus.objects.filter(
                    vhost=self.vhost,
                    driver_object_type=f"{cls._meta.app_label}.{cls.__name__}",
                ).values("driver_object_uuid")

                fixtures = cls.objects.filter(
                    **qkwargs,
                    updated_on__gt=update_at,
                    uuid__in=subquery,
                )
                for f in fixtures:
                    matches.append(self._format_match(f))
        else:
            for cls in self.GAME_CLASSES:
                fixtures = cls.objects.filter(**qkwargs)
                for f in fixtures:
                    matches.append(self._format_match(f))

        return matches

    def get_outcomes(self, **kwargs):
        outcomes = []
        # Base query constraints
        if "provider_match_uuid" in kwargs:
            qkwargs = {"vhost": self.vhost, "uuid": kwargs["provider_match_uuid"]}
            self.logger.info(
                "Getting Active APISports Matches that match passed UUID: presenting as Outcomes to DataEngine..."
            )
        else:
            qkwargs = {"vhost": self.vhost}
            self.logger.info(
                "Getting Active APISports Matches, presenting as Outcomes to DataEngine..."
            )

        update_at = kwargs.get("sync_update_at")

        game_classes = [
            {"m": AMFGame, "s": AMFGameScore},
            {"m": BABGame, "s": BABGameScore},
            {"m": BASEGame, "s": BASEGameScore},
            {"m": FBALLGame, "s": FBALLGameScore},
            {"m": HOCKGame, "s": HOCKGameScore},
        ]

        for cls in game_classes:
            game_model = cls["m"]
            score_model = cls["s"]

            if update_at:
                subquery = MatchSyncStatus.objects.filter(
                    vhost=self.vhost,
                    driver_object_type=f"{game_model._meta.app_label}.{game_model.__name__}",
                ).values("driver_object_uuid")

                fixtures = game_model.objects.filter(
                    **qkwargs,
                    updated_on__gt=update_at,
                    uuid__in=subquery,
                )
            else:
                fixtures = game_model.objects.filter(**qkwargs)

            for f in fixtures:
                # print(f)
                finished = False
                if f.status_short == "FT":
                    finished = True
                outcome = {
                    "id": f.id,
                    "object_uuid": f.uuid,
                    "object_type": f"{f._meta.app_label}.{f._meta.model_name}.{f._meta.object_name}",
                    "commence_time": f.commence_time,
                    "routing_key": None,
                    "apiid": f.id,
                    "fixture_uuid": f.uuid,
                    "fixture_type": f"{f._meta.app_label}.{f._meta.model_name}.{f._meta.object_name}",
                    "state_id": None,
                    "status_short": f.status_short,
                    "status_long": f.status_long,
                    "inserted_on": f.created_at,
                    "clock": f.status_timer,
                    "segment_uuid": None,
                    "segment_type": None,
                    "segment": None,
                    "is_current": None,
                    "is_start_game": None,
                    "is_end_game": None,
                    "is_start_segment": None,
                    "is_end_segment": None,
                    "segments": [],
                    "teams": [],
                    "finished":finished
                }

                # Scores and segments
                for p in score_model.objects.filter(vhost=self.vhost, match=f):
                    # print(p)
                    team_score = {
                        "id": p.uuid,
                        "team_uuid": p.team.uuid,
                        "team_type": f"{p.team._meta.app_label}.{p.team._meta.model_name}.{p.team._meta.object_name}",
                        "score": p.total,
                        "is_winner": None,
                        "inserted_on": None,
                        "routing_key": None,
                        "object_uuid": p.uuid,
                        "object_type": f"{p._meta.app_label}.{p._meta.model_name}.{p._meta.object_name}",
                    }
                    outcome["teams"].append(team_score)
                    # print(team_score)
                    for key in [
                        "quarter_1", "quarter_2", "quarter_3", "quarter_4", "overtime", "total",
                        "inning_1", "inning_2", "inning_3", "inning_4", "inning_5", "inning_6", "inning_7",
                        "inning_8", "inning_9", "hits", "errors", "extra", "halftime",
                        "fulltime", "extratime", "penalty", "goals", "first", "third", "second", "penalties",
                    ]:
                        if getattr(p, key, None) is not None:
                            score = getattr(p, key)
                            so = {
                                "id": p.uuid,
                                "object_uuid": p.uuid,
                                "object_type": f"{p._meta.app_label}.{p._meta.model_name}.{p._meta.object_name}",
                                "segment_uuid": None,
                                "segment_type": key,
                                "segment": key,
                                "team_uuid": p.team.uuid,
                                "team_type": f"{p.team._meta.app_label}.{p.team._meta.model_name}.{p.team._meta.object_name}",
                                "routing_key": None,
                                "score": score,
                                "is_winner": None,
                                "state_id": key,
                                "inserted_on": None,
                            }
                            outcome["segments"].append(so)

                outcomes.append(outcome)

        return outcomes
    def get_match_odds_ml(self,**kwargs):
        return []