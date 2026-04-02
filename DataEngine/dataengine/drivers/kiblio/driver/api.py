from django import db
from django.utils.text import slugify
from logging import getLogger

from dataengine.drivers.kiblio.api.http import KiblHttpAPI
from dataengine.drivers.kiblio.models import Sport, Season, League, Participant, Fixture, FixtureParticipants, \
    MarketType, FixtureMarket, Segment, Sides, Outcome, OutcomeSegmentScore, OutcomeParticipants
from dataengine.engine.abc import DataEngineDriverAPIABC
from dataengine.models import MatchSyncStatus


class DataEngineDriverAPI(DataEngineDriverAPIABC):
    PKEY_MODEL_MAPPINGS = {
        "match":"routing_key",
        "outcome":"routing_key",
        "outcome_segment":"routing_key",

    }
    dbobj_name =  {
        "sport":"kiblio.league.League",
        "group":"kiblio.sport.Sport",
        "team": "kiblio.participant.Participant",
        "match":"kiblio.fixture.Fixture",
        "mkt_summary":"kiblio.outcome.FixtureMarket",
    }
    get_apiobj_map = {
        "kiblio.league.League":League,
        "kiblio.sport.Sport":Sport,
        "kiblio.participant.Participant":Participant,
        "kiblio.fixture.Fixture":Fixture,
        "kiblio.outcome.FixtureMarket":FixtureMarket,
    }
    vhost = False
    logger = getLogger("dataengine.drivers.kiblio.driver.api")
    name = "dataengine.drivers.kiblio"
    def __init__(self,vhost,**kwargs):
        self.vhost = vhost
        self.logger.info(f"KIBL.io driver on {self.vhost} DataEngine Driver Loaded!")

    def get_api_object(self,type,uuid):
        if type not in self.get_apiobj_map: return False
        try:
            return self.get_apiobj_map[type].objects.get(pk=uuid)
        except self.get_apiobj_map[type].DoesNotExist: return False


    def get_updated_synced_matches_index(self,update_at):
        fixtures = []
        fixtureObjs = Fixture.objects.filter(
            vhost=self.vhost,  # restrict to the current vhost
            updated_on__gt=update_at,
            uuid__in=MatchSyncStatus.objects.filter(
                driver_object_type="kiblio.fixture.Fixture"
            ).values("driver_object_uuid")
        )
        # print(fixtureObjs)
        for f in fixtureObjs:
            fd = {
                "id":f.fixture_id,
                "object_uuid": f.uuid,
                "object_type": f"{f._meta.app_label}.{f._meta.model_name}.{f._meta.object_name}",
            }
            fixtures.append(fd)
        return fixtures

    def update_all(self):
        self.logger.info(f"KIBL.io driver on {self.vhost} Updating Fixture Data!")
        apiObj = KiblHttpAPI(self.vhost)

        # ....and from here we go to fixtures in play:
        _fixture = apiObj.fetch_upcoming_fixtures()
        for fixture in _fixture:
            self.logger.info(f"Working on fixture {fixture}")
            apiObj.fetch_fixture_markets(fixture)


    def get_sports_groups(self):
        groups = []
        self.logger.info(f"Getting Active KIBL.io Sports, presenting as groups to DataEngine...")
        sportObjs = Sport.objects.filter(active=True,vhost=self.vhost)
        for sport in sportObjs:
            groups.append(self._format_group(sport))
        return groups


    def get_sports_seasons(self):
        seasons = []
        self.logger.info(f"Getting Active KIBL.io Seasons, presenting as seasons to DataEngine...")
        seasonObjs = Season.objects.filter(vhost=self.vhost)
        for season in seasonObjs:
            seasons.append(self._format_season(season))
        return seasons


    def get_sports_sports(self):
        sports = []
        self.logger.info(f"Getting Active KIBL.io Leagues, presenting as Sports to DataEngine...")
        leagueObjs = League.objects.filter(vhost=self.vhost)
        for league in leagueObjs:
            sports.append(self._format_sport(league))
        return sports


    def get_teams(self):
        teams = []
        self.logger.info(f"Getting Active KIBL.io Participants, presenting as Teams to DataEngine...")
        participantObjs = Participant.objects.filter(vhost=self.vhost)
        for team in participantObjs:
            teams.append(self._format_team(team))
        return teams

    def get_segments(self):
        segments = []
        self.logger.info(f"Getting Active KIBL.io Segments, presenting as Segments to DataEngine...")
        segmentObjs = Segment.objects.filter(vhost=self.vhost)
        for segment in segmentObjs:
            segments.append(self._format_segment(segment))
        return segments

    def get_venues(self):
        """ Stubbed!"""
        return []


    def get_matches(self,**kwargs):
        data = []
        if "provider_match_objs" in kwargs:
            self.logger.info(f"Getting Active KIBL.io Fixtures with passed match (fixture) objects: presenting as Matches to DataEngine...")
            fixtureObjs = kwargs["provider_match_objs"]

        elif "after_time" in kwargs:
            self.logger.info(f"Getting Active KIBL.io Fixtures updated after {kwargs["after_time"]} presenting as Matches to DataEngine...")
            fixtureObjs = Fixture.objects.filter(vhost=self.vhost,updated_at__gte=kwargs["after_time"])
        else:
            self.logger.info(f"Getting Active KIBL.io Fixtures, presenting as Matches to DataEngine...")
            fixtureObjs = Fixture.objects.filter(vhost=self.vhost)
        hSideObj = Sides.objects.get(abrv="HOME", vhost=self.vhost)
        aSideObj = Sides.objects.get(abrv="VISITOR", vhost=self.vhost)

        for f in fixtureObjs:
            # print(f)
            hTeObj = False
            aTeObj = False
            try:
                hTeObj = FixtureParticipants.objects.get(vhost=self.vhost,fixture=f,side=hSideObj)
            except FixtureParticipants.DoesNotExist:
                print(f"Fixture participant for fixture {f} and side {hSideObj} not found")
            except FixtureParticipants.MultipleObjectsReturned:
                _hTeObj = FixtureParticipants.objects.filter(vhost=self.vhost, fixture=f, side=hSideObj)
                hTeObj = _hTeObj[0]
                for delobj in _hTeObj[1:]:
                    delobj.delete()
            try:
                aTeObj = FixtureParticipants.objects.get(vhost=self.vhost, fixture=f, side=aSideObj)
            except FixtureParticipants.DoesNotExist:
                print(f"Fixture participant for fixture {f} and side {aSideObj} not found")
            except FixtureParticipants.MultipleObjectsReturned:
                _aTeObj = FixtureParticipants.objects.filter(vhost=self.vhost, fixture=f, side=aSideObj)
                aTeObj = _aTeObj[0]
                for delobj in _aTeObj[1:]:
                    delobj.delete()
            # print(f.state)
            if f.state:
                status_short = f.state.abrv
                status_long = f.state.name
            else:
                status_short = "UPC"
                status_long = "Upcoming"
            if aTeObj and hTeObj:
                if f.routing_key == "{}.{}.{}.{}.{}.{}.{}":
                    routing_key = None
                else:
                    routing_key = f.routing_key
                htkey = hTeObj.participant.abrv
                if not htkey: htkey = slugify(hTeObj.participant.name)
                atkey = aTeObj.participant.abrv
                if not atkey: atkey = slugify(aTeObj.participant.name)
                skey = f.league.abrv
                if not skey: skey = slugify(f.league.name)
                entry = {
                "match":{
                    "id":f.fixture_id,

                    "object_uuid": f.uuid,
                    "object_type": f"{f._meta.app_label}.{f._meta.model_name}.{f._meta.object_name}",
                    "commence_time":f.start_time,
                    "name":f.name,
                    "routing_key": routing_key,
                    "inserted_on":f.inserted_on,
                    "inserted_on_epoch":f.inserted_on_epoch,
                    "home_team_type":f"{hTeObj.participant._meta.app_label}.{hTeObj.participant._meta.model_name}.{hTeObj.participant._meta.object_name}",
                    "home_team_uuid":hTeObj.participant.uuid,
                    "away_team_type": f"{aTeObj.participant._meta.app_label}.{aTeObj.participant._meta.model_name}.{aTeObj.participant._meta.object_name}",
                    "away_team_uuid": aTeObj.participant.uuid,
                    "sport_type": f"{f.league._meta.app_label}.{f.league._meta.model_name}.{f.league._meta.object_name}",
                    "sport_uuid": f.league.uuid,
                    "season_type": f"{f.season._meta.app_label}.{f.season._meta.model_name}.{f.season._meta.object_name}",
                    "season_uuid": f.season.uuid,
                    "status_short":status_short,
                    "status_long":status_long,
                    "status_timer":None,
                    },
                "group": self._format_group(f.league.sport),
                "season": self._format_season(f.season),
                "sport": self._format_sport(f.league),
                "teams":{
                    "home":self._format_team(hTeObj.participant),
                    "away": self._format_team(aTeObj.participant),
                }
                }
                data.append(entry)
                if not status_long or not status_short:
                    print(f.uuid,status_long,status_short)
            # else:
            #     print(FixtureParticipants.objects.filter(vhost=self.vhost,fixture=f))
            #     print(f"This is strange, {f}: HT {hTeObj}, AT: {aTeObj}")
        return data

    def get_match_odds_ml(self,**kwargs):
        matchOddSummaries = []
        self.logger.info(f"Getting Active KIBL.io Fixtures: Moneyline Markets, presenting as Match OddsSummary to DataEngine...")
        if "provider_match_uuid" in kwargs:
            fixtureObjs = Fixture.objects.filter(vhost=self.vhost,uuid=kwargs["provider_match_uuid"])
            self.logger.info(
                f"Getting Active APISports Matches that match passed UUID: presenting as Matches to DataEngine...")
        elif "provider_match_objs" in kwargs:
            self.logger.info(
                f"Getting Active KIBL.io Fixtures with passed match (fixture) objects: presenting as Matches to DataEngine...")
            fixtureObjs = kwargs["provider_match_objs"]

        else:
            self.logger.info(f"Getting Active KIBL.io Fixtures, presenting as Matches to DataEngine...")
            fixtureObjs = Fixture.objects.filter(vhost=self.vhost)
        mlMrObj = MarketType.objects.get(abrv="2WML",vhost=self.vhost)
        tmlMrObj = MarketType.objects.get(abrv="3WML", vhost=self.vhost)
        segObj = Segment.objects.get(abrv="FG",vhost=self.vhost)
        hSideObj = Sides.objects.get(abrv="HOME",vhost=self.vhost)
        aSideObj = Sides.objects.get(abrv="VISITOR", vhost=self.vhost)
        dSideObj = Sides.objects.get(abrv="DRAW", vhost=self.vhost)

        for f in fixtureObjs:

            _hTeObj = FixtureParticipants.objects.filter(vhost=self.vhost,fixture=f,side=hSideObj)
            if len(_hTeObj)<1:
                hTeObj = None
            else:
                hTeObj = _hTeObj[0]
            _aTeObj = FixtureParticipants.objects.filter(vhost=self.vhost,fixture=f,side=aSideObj)
            if len(_aTeObj)<1:
                aTeObj = None
            else:
                aTeObj = _aTeObj[0]

            mlObj = FixtureMarket.objects.filter(vhost=self.vhost,fixture=f,market_type=mlMrObj,segment=segObj)
            if len(mlObj) == 2 and hTeObj and aTeObj:
                matchOdds = False
                try:

                    hMlObj = mlObj.filter(side=hSideObj)[0]
                    aMlObj = mlObj.filter(side=aSideObj)[0]
                    matchOdds = {
                        "id":f.fixture_id,
                        "match_uuid":f.uuid,
                        "match_type":f"{f._meta.app_label}.{f._meta.model_name}.{f._meta.object_name}",
                        "object_uuid": f.uuid,
                        "object_type": f"{f._meta.app_label}.{f._meta.model_name}.{f._meta.object_name}",
                        "home_team_type":f"{hTeObj.participant._meta.app_label}.{hTeObj.participant._meta.model_name}.{hTeObj.participant._meta.object_name}",
                        "home_team_uuid":hTeObj.participant.uuid,
                        "away_team_type": f"{aTeObj.participant._meta.app_label}.{aTeObj.participant._meta.model_name}.{aTeObj.participant._meta.object_name}",
                        "away_team_uuid": aTeObj.participant.uuid,
                        "home_price":hMlObj.price_american,
                        "home_price_fraction": hMlObj.price_fraction,
                        "away_price":aMlObj.price_american,
                        "away_price_fraction":aMlObj.price_fraction,
                        "bookmaker":{
                            "uuid":hMlObj.sportsbook.uuid,
                            "object_uuid": hMlObj.sportsbook.uuid,
                            "object_type": f"{hMlObj.sportsbook._meta.app_label}.{hMlObj.sportsbook._meta.model_name}.{hMlObj.sportsbook._meta.object_name}",
                            "feed_source_id":hMlObj.sportsbook.feed_source_id,
                            "feed_type_id": f"{hMlObj.sportsbook.feed_source_id}",
                            "name": f"{hMlObj.sportsbook.name}",
                            "tag": f"{hMlObj.sportsbook.tag}",
                            }
                        }
                except IndexError:
                    matchOdds = False
                if matchOdds:
                    matchOddSummaries.append(matchOdds)
            else:
                pass
                # Not working on 3WML for now...
                # mlObj = FixtureMarket.objects.filter(vhost=self.vhost, fixture=f, market_type=tmlMrObj, segment=segObj)
                #
                # if len(mlObj) == 3:
                #     print(mlObj.filter(side=aSideObj))
                #     hMlObj = mlObj.get(side=hSideObj)
                #     aMlObj = mlObj.get(side=aSideObj)
                #     dMLObj = mlObj.get(side=dSideObj)
                #
                #     matchOdds = {
                #         "id": f.fixture_id,
                #         "object_uuid": f.uuid,
                #         "object_type": f"{f._meta.app_label}.{f._meta.model_name}.{f._meta.object_name}",
                #         "home_team_type": f"{hTeObj.participant._meta.app_label}.{hTeObj.participant._meta.model_name}.{hTeObj.participant._meta.object_name}",
                #         "home_team_uuid": hTeObj.participant.uuid,
                #         "away_team_type": f"{aTeObj.participant._meta.app_label}.{aTeObj.participant._meta.model_name}.{aTeObj.participant._meta.object_name}",
                #         "away_team_uuid": aTeObj.participant.uuid,
                #         "home_price": hMlObj.price_american,
                #         "home_price_fraction": hMlObj.price_fraction,
                #         "away_price": aMlObj.price_american,
                #         "away_price_fraction": aMlObj.price_fraction,
                #         "draw_price":dMLObj.price_american,
                #         "draw_price_fraction":dMLObj.price_fraction,
                #
                #     }
                #     matchOddSummaries.append(matchOdds)



        return matchOddSummaries

    def get_outcomes(self, **kwargs):
        all_outcomes = []
        if "provider_match_uuid" in kwargs:
            fuuid = kwargs["provider_match_uuid"]
            self.logger.info(
                f"Getting Active KIBL.io Fixture {fuuid}: Outcomes, presenting as Outcomes, OutcomeSegments and OutcomeParticipants to DataEngine...")
            fixtureObjs = Fixture.objects.filter(vhost=self.vhost,uuid=fuuid)
        elif "provider_match_objs" in kwargs:
            self.logger.info(
                f"Getting Active KIBL.io Outcomes with passed match (fixture) objects: presenting  Outcomes, OutcomeSegments and OutcomeParticipants to DataEngine...")
            fixtureObjs = kwargs["provider_match_objs"]
        else:
            self.logger.info(f"Getting Active KIBL.io Outcomes, presenting as Outcomes, OutcomeSegments and OutcomeParticipants to DataEngine...")
            fixtureObjs = Fixture.objects.filter(vhost=self.vhost)
        for f in fixtureObjs:
            outcomeObj = Outcome.objects.filter(vhost=self.vhost,fixture=f,is_end_game=True)
            status_short = ""
            status_long = ""

            if (len(outcomeObj)<1):
                outcomeObj = Outcome.objects.filter(vhost=self.vhost, fixture=f)
                finished = False
            else:
                status_short = "FINAL"
                status_long = "FINAL"
                finished = True

            for o in outcomeObj:
                ooo = {
                    "id": o.outcome_id,
                    "apiid":None,
                    "object_uuid": o.uuid,
                    "object_type": f"{o._meta.app_label}.{o._meta.model_name}.{o._meta.object_name}",
                    "fixture_uuid": o.fixture.uuid,
                    "fixture_type": f"{o.fixture._meta.app_label}.{o.fixture._meta.model_name}.{o.fixture._meta.object_name}",
                    "segment_uuid": o.segment.uuid,
                    "segment_type": f"{o.segment._meta.app_label}.{o.segment._meta.model_name}.{o.segment._meta.object_name}",
                    "segment": o.segment.name,
                    "state_id":o.state_id,
                    "status_long": status_long,
                    "status_short": status_short,
                    "routing_key": o.routing_key,
                    "inserted_on": o.inserted_on,
                    "clock": o.clock,
                    "is_current": o.is_current,
                    "is_start_game": o.is_start_game,
                    "is_end_game": o.is_end_game,
                    "is_start_segment": o.is_start_segment,
                    "is_end_segment": o.is_end_segment,
                    "segments": [],
                    "teams": [],
                    "finished":finished

                }

                segmentObjs = OutcomeSegmentScore.objects.filter(vhost=self.vhost,outcome=o)
                for s in segmentObjs:
                    so = {
                        "id": s.uuid,
                        "object_uuid":s.uuid,
                        "object_type":f"{s._meta.app_label}.{s._meta.model_name}.{s._meta.object_name}",
                        "segment_uuid": s.segment.uuid,
                        "segment_type": f"{s.segment._meta.app_label}.{s.segment._meta.model_name}.{s.segment._meta.object_name}",
                        "segment": o.segment.name,
                        "team_uuid":s.participant.uuid,
                        "team_type": f"{s.participant._meta.app_label}.{s.participant._meta.model_name}.{s.participant._meta.object_name}",
                        "routing_key": s.routing_key,
                        "score": s.score,
                        "is_winner": s.is_winner,
                        "state_id": s.state_id,
                        "inserted_on": s.inserted_on,
                        "team":self._format_team(s.participant),

                    }
                    ooo["segments"].append(so)

                ooo["teams"] = []
                participantObjs = OutcomeParticipants.objects.filter(vhost=self.vhost,outcome=o)
                for p in participantObjs:
                    po = {
                        "id": p.uuid,
                        "team_uuid": p.participant.uuid,
                        "team_type":f"{p.participant._meta.app_label}.{p.participant._meta.model_name}.{p.participant._meta.object_name}",
                        "score": p.score,
                        "is_winner": p.is_winner,
                        "inserted_on": p.inserted_on,
                        "routing_key": p.routing_key,
                        "object_uuid": p.uuid,
                        "object_type": f"{p._meta.app_label}.{p._meta.model_name}.{p._meta.object_name}",
                        "team": self._format_team(p.participant),

                    }
                    ooo["teams"].append(po)
                all_outcomes.append(ooo)
        return all_outcomes