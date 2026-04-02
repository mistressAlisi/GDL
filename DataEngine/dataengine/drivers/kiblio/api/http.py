import json
from datetime import timedelta

import boto3
import requests
from django.forms import model_to_dict
from django.utils.timezone import now
from parameters.models import VHostParameterRegistry
from dataengine.drivers.kiblio.models import League, MarketGenres, MarketStatus, Participant, Location, Fixture, \
    FixtureParticipants, Sportsbook, FixtureMarket, Outcome, OutcomeSegmentScore, OutcomeParticipants
from dataengine.drivers.kiblio.models.base import Sport, Region, BetType, MarketType, MarketTypeSport, Segment, Season, State, \
    Sides, FixtureType
from .common import object_setattrs, KIBL_MARKET_UPDATE_FIELDS, process_fixture_market_data, process_fixture_data, \
    process_fixture_outcomes_data


class KiblHttpAPI(object):
    urls = {
        "_prefix":"https://api.kibl.io/sports/",
        "leagues":"get/reference/leagues",
        "sports":"get/reference/sports",
        "region": "get/reference/region",
        "betting_types":"get/reference/betting-types",
        "combined_line_types":"get/reference/combined-line-types",
        "market_types":"get/reference/market-types",
        "market_genres":"get/reference/market-genres",
        "market_statuses":"get/reference/market-statuses",
        "seasons":"get/reference/seasons",
        "segments":"get/reference/segments",
        "sportsbooks":"get/reference/sportsbooks",
        "participants":"get/reference/participants",
        "locations":"get/reference/locations",
        "fixture_types":"get/reference/fixture-types",
        "sides":"get/reference/sides",
        "states":"get/reference/states",
        "leagues_in_season":"get/info/leagues-in-season",
        "fixtures":"get/info/fixtures",
        "fixtures_participants": "get/info/fixtures-participants",
        "markets":"get/info/markets",
        "outcomes":"get/info/outcomes",
    }
    token = False
    refresh_token = None
    expires_at = None
    id_token = None
    vhost = False
    regappid = "dataengine.drivers.kiblio"




    def __init__(self, vhost,**kwargs):
        self.vhost = vhost

    def _get_token(self):
        client = boto3.client('cognito-idp','us-west-2')

        response = client.initiate_auth(
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={
                'USERNAME': VHostParameterRegistry.objects.get(vhost=self.vhost,application=self.regappid,name="username").value_text,
                'PASSWORD': VHostParameterRegistry.objects.get(vhost=self.vhost,application=self.regappid,name="password").value_text
            },
            ClientId=VHostParameterRegistry.objects.get(vhost=self.vhost,application=self.regappid,name="clientid").value_text
        )

        # Tokens
        access_token = response['AuthenticationResult']['AccessToken']
        id_token = response['AuthenticationResult']['IdToken']
        refresh_token = response['AuthenticationResult']['RefreshToken']
        self.expires_at = now() + timedelta(seconds=response['AuthenticationResult']['ExpiresIn'])
        # print('Access Token:', access_token)
        # print('IdToken:', id_token)
        # print('Refresh Token:', refresh_token)
        # print(self.expires_at)
        # print(response['AuthenticationResult']['ExpiresIn'])
        self.token = access_token
        self.id_token = id_token
        self.refresh_token = refresh_token
        return self.token

    def get_token(self):
        if not self.token:
            return self._get_token()
        else:
            if now() > self.expires_at:
                self._get_token()
            return self.token


    def _make_get_req(self,url,**kwargs):
        turl = self.urls["_prefix"]+url
        if "data" in kwargs:
            turl += f"?{kwargs['data']}"
        # print(turl)
        headers = {"Authorization":f"{self.get_token()}"}
        # print(headers)
        r  = requests.get(turl,headers=headers).json()
        if "code" in r and r["code"] == 200:
            if "return_request" in kwargs:
                return r
            else:
                return r["result"]
        else:
            raise Exception(f"{r}")



    def fetch_sports(self,**kwargs):
        data = self._make_get_req(self.urls["sports"])
        for entry in data:
            sportObj,c = Sport.objects.get_or_create(sport_id=entry["sport_id"],vhost=self.vhost)
            if c:
                object_setattrs(sportObj,entry)
        if "verbose" in kwargs:
            return Sport.objects.filter(vhost=self.vhost)
        else:
            return True

    def fetch_regions(self,**kwargs):
        data = self._make_get_req(self.urls["region"])
        for entry in data:
            regionObj = Region.objects.get_or_create(region_id=entry["region_id"],vhost=self.vhost)[0]
            object_setattrs(regionObj,entry)
        if "verbose" in kwargs:
            return Region.objects.filter(vhost=self.vhost)
        else:
            return True

    def get_sports(self):
        return Sport.objects.filter(vhost=self.vhost)

    def get_regions(self):
        return Region.objects.filter(vhost=self.vhost)



    def fetch_leagues(self,**kwargs):
        data = self._make_get_req(self.urls["leagues"])
        # print(data[0])
        for entry in data:
            # print(entry["sport_id"],entry["region_id"])
            sportObj,c = Sport.objects.get_or_create(sport_id=entry["sport_id"],vhost=self.vhost)
            if c: sportObj.save()
            # print(sportObj)
            regionObj,c = Region.objects.get_or_create(region_id=entry["region_id"],vhost=self.vhost)
            if c: regionObj.save()
            # print(regionObj)
            # print(sportObj,regionObj)
            leagueObj,c = League.objects.get_or_create(vhost=self.vhost,sport=sportObj,region=regionObj,league_id=entry["league_id"])
            if c:
                object_setattrs(leagueObj,entry)
        if "verbose" in kwargs:
            return League.objects.filter(vhost=self.vhost)
        else:
            return True

    def get_leagues(self):
        return League.objects.filter(vhost=self.vhost)


    def fetch_betting_types(self,**kwargs):
        data = self._make_get_req(self.urls["betting_types"])
        for entry in data:
            regionObj = BetType.objects.get_or_create(betting_type_id=entry["betting_type_id"],vhost=self.vhost)[0]
            object_setattrs(regionObj,entry)
        if "verbose" in kwargs:
            return BetType.objects.filter(vhost=self.vhost)
        else:
            return True

    def get_betting_types(self):
        return BetType.objects.filter(vhost=self.vhost)

    def fetch_combined_line_types(self):
        data = self._make_get_req(self.urls["combined_line_types"])
        print(data)



    def fetch_market_genres(self):
        data = self._make_get_req(self.urls["market_genres"])
        for entry in data:
            # print(entry)
            genreObj = MarketGenres.objects.get_or_create(market_genre_id=entry["market_genre_id"],vhost=self.vhost)[0]
            # print(entry)
            object_setattrs(genreObj,entry)
        return MarketGenres.objects.filter(vhost=self.vhost)

    def get_market_genres(self):
        return MarketGenres.objects.filter(vhost=self.vhost)

    def fetch_market_types(self,**kwargs):
        data = self._make_get_req(self.urls["market_types"])
        for entry in data[0:10]:
            # print(entry)
            genreObj = MarketGenres.objects.get(market_genre_id=entry["market_genre_id"],vhost=self.vhost)
            marketObj = MarketType.objects.get_or_create(market_type_id=entry["market_type_id"],vhost=self.vhost,genre=genreObj)[0]
            # marketObj.genre = genreObj
            object_setattrs(marketObj,entry)
            for k,v in entry["for_sports"].items():
                # print(k,v)
                for y in v:
                    try:
                        sportObj = Sport.objects.get(sport_id=y, vhost=self.vhost)
                    except Sport.DoesNotExist:
                        sportObj = Sport.objects.get_or_create(sport_id=y, vhost=self.vhost)[0]
                        sportObj.save()
                    mtsObj = MarketTypeSport.objects.get_or_create(market_type=marketObj,for_sport=sportObj)[0]
                    mtsObj.save()
        if "verbose" in kwargs:
            return MarketType.objects.filter(vhost=self.vhost)
        else:
            return True

    def get_market_types(self):
        return MarketType.objects.filter(vhost=self.vhost)

    def fetch_market_statuses(self,**kwargs):
        data = self._make_get_req(self.urls["market_statuses"])
        for entry in data:
            mssObj = MarketStatus.objects.get_or_create(market_status_id=entry["market_status_id"],vhost=self.vhost)[0]
            object_setattrs(mssObj,entry)
        if "verbose" in kwargs:
            return MarketStatus.objects.filter(vhost=self.vhost)
        else:
            return True

    def get_market_statuses(self):
        return MarketStatus.objects.filter(vhost=self.vhost)

    def fetch_segments(self,**kwargs):
        data = self._make_get_req(self.urls["segments"])
        for entry in data:
            mssObj = Segment.objects.get_or_create(segment_id=entry["segment_id"],vhost=self.vhost)[0]
            object_setattrs(mssObj,entry)
        if "verbose" in kwargs:
            return Segment.objects.filter(vhost=self.vhost)
        else:
            return True


    def get_segments(self):
        return Segment.objects.filter(vhost=self.vhost)


    def fetch_seasons(self,**kwargs):
        data = self._make_get_req(self.urls["seasons"])
        for entry in data:
            ssObj = Season.objects.get_or_create(season_id=entry["season_id"],vhost=self.vhost)[0]
            object_setattrs(ssObj,entry)
        if "verbose" in kwargs:
            return Season.objects.filter(vhost=self.vhost)
        else:
            return True


    def get_seasons(self):
        return Season.objects.filter(vhost=self.vhost)

    def fetch_states(self,**kwargs):
        data = self._make_get_req(self.urls["states"])
        for entry in data:
            ssObj = State.objects.get_or_create(state_id=entry["state_id"], vhost=self.vhost)[0]
            object_setattrs(ssObj, entry)
        if "verbose" in kwargs:
            return State.objects.filter(vhost=self.vhost)
        else:
            return True

    def fetch_league_participants(self,**kwargs):
        # print(kwargs)
        league = kwargs["league"]
        # print(f"In FLP,{league}")
        url = f"{self.urls["participants"]}?league_id={league.league_id}"
        if "participant_id" in kwargs:
            # print(kwargs)
            url += f"&participant_id={kwargs['participant_id']}"
        # print(url)
        data = self._make_get_req(url)
        # print(data)
        for entry in data:
            try:
                participantObj = Participant.objects.get_or_create(participant_id=entry["participant_id"],vhost=self.vhost,league=league)[0]
            except Participant.MultipleObjectsReturned:
                participantObj = \
                Participant.objects.filter(participant_id=entry["participant_id"], vhost=self.vhost,
                                                  league=league).first()
            object_setattrs(participantObj,entry)
            participantObj.save()
        retr = Participant.objects.filter(vhost=self.vhost,league=league)
        if "participant_id" in kwargs:
            retr = Participant.objects.filter(vhost=self.vhost,league=league,participant_id=kwargs["participant_id"])

        return retr

    def get_league_participants(self,league):
        return Participant.objects.filter(vhost=self.vhost,league=league)

    def fetch_participants(self,**kwargs):
        if "league" in kwargs:
            leagues = [kwargs["league"]]
        else:
            leagues = self.fetch_leagues_in_season()
        for league in leagues:
            if "participant_id" in kwargs:
                # print("Kwargs")
                participant = self.fetch_league_participants(league=league,participant_id=kwargs["participant_id"])
            else:
                participant = self.fetch_league_participants(league=league)
            # print(participant[0])
        retr = Participant.objects.filter(vhost=self.vhost)
        if "participant_id" in kwargs:
            # print("PPI")
            retr = Participant.objects.filter(vhost=self.vhost,participant_id=kwargs["participant_id"])
        # print(retr)
        return retr

    def get_participants(self):
        return Participant.objects.filter(vhost=self.vhost)

    def fetch_leagues_in_season(self,**kwargs):
        data = self._make_get_req(self.urls["leagues_in_season"])
        ids = []
        for entry in data:
            ids.append(entry["league_id"])
        return League.objects.filter(league_id__in=ids)


    def fetch_sides(self,**kwargs):
        data = self._make_get_req(self.urls["sides"])
        for entry in data:
            sideObj = Sides.objects.get_or_create(vhost=self.vhost,side_id=entry['side_id'])[0]
            object_setattrs(sideObj,entry)
        return Sides.objects.filter(vhost=self.vhost)

    def get_sides(self):
        return Sides.objects.filter(vhost=self.vhost)

    def fetch_locations(self,**kwargs):
        data = self._make_get_req(self.urls["locations"])
        for entry in data:
            sideObj = Location.objects.get_or_create(vhost=self.vhost,location_id=entry['location_id'])[0]
            object_setattrs(sideObj,entry)
        return Location.objects.filter(vhost=self.vhost)

    def get_locations(self):
        return Location.objects.filter(vhost=self.vhost)

    def fetch_fixture_types(self,**kwargs):
        data = self._make_get_req(self.urls["fixture_types"])
        for entry in data:
            ftObj = FixtureType.objects.get_or_create(vhost=self.vhost,fixture_type_id=entry['fixture_type_id'])[0]
            object_setattrs(ftObj,entry)
        return FixtureType.objects.filter(vhost=self.vhost)

    def get_fixture_types(self):
        return FixtureType.objects.filter(vhost=self.vhost)


    def fetch_sportsbooks(self,**kwargs):
        data = self._make_get_req(self.urls["sportsbooks"])
        for entry in data:
            ftObj = Sportsbook.objects.get_or_create(vhost=self.vhost,feed_source_id=entry['feed_source_id'])[0]
            object_setattrs(ftObj,entry)
        return Sportsbook.objects.filter(vhost=self.vhost)

    def get_sportsbooks(self):
        return Sportsbook.objects.filter(vhost=self.vhost)


    def _fetch_league_fixtures(self,league,**kwargs):
        if "fixture_id" in kwargs:
            data = self._make_get_req(self.urls["fixtures"], data=f"league_id={league.league_id}&fixture_id={kwargs['fixture_id']}")

        else:
            data = self._make_get_req(self.urls["fixtures"],data=f"league_id={league.league_id}")
        fixtureObj = None
        self.logger.info(f"FixtureRequest contains {len(data)} entries")
        for entry in data:

            fixtureObj = process_fixture_data(entry,self.vhost)

        if "fixture_id" in kwargs:
            # print(f"Going out swinging! {kwargs["fixture_id"]}")
            return fixtureObj
        else:
            return Fixture.objects.filter(vhost=self.vhost, league=league)

    def fetch_upcoming_fixtures(self,**kwargs):
        leagues = self.fetch_leagues_in_season()
        all_fixtures = []
        for league in leagues:
            fixtures = self._fetch_league_fixtures(league)
            all_fixtures.extend(fixtures)
        return all_fixtures

    def get_fixture(self,fixture_id):
        return Fixture.objects.filter(vhost=self.vhost,fixture_id=fixture_id)

    def get_all_fixtures(self):
        return Fixture.objects.filter(vhost=self.vhost)

    def fetch_fixture_participants(self,fixture,**kwargs):
        data = self._make_get_req(self.urls["fixtures_participants"],data=f"fixture_id={fixture.fixture_id}")
        participants = []
        if data != []:
            for entry in data:
                print(entry)
                sideObj = Sides.objects.get(vhost=self.vhost,side_id=entry["side_id"])
                participantObj = Participant.objects.get(vhost=self.vhost,participant_id=entry["participant_id"])
                fpObj = FixtureParticipants.objects.get_or_create(vhost=self.vhost,fixture=fixture,participant=participantObj,side=sideObj,fixture_participant_id=entry["fixture_participant_id"])[0]
                object_setattrs(fpObj,entry)
                participants.append(fpObj)
        return participants


    def fetch_fixture_markets(self,**kwargs):
        retr = []
        # print("Fetching fixture markets {kwargs}".format(kwargs=kwargs))
        for sbk in Sportsbook.objects.filter(vhost=self.vhost,active=True):
            if "league" in kwargs:
                league = kwargs["league"]
                data = self._make_get_req(self.urls["markets"],
                                          data=f"league_id={league.league_id}&feed_source_id={sbk.feed_source_id}")
            elif "fixture" in kwargs:
                fixture = kwargs["fixture"]
                league = fixture.league
                data = self._make_get_req(self.urls["markets"],data=f"league_id={fixture.league.league_id}&fixture_id={fixture.fixture_id}&feed_source_id={sbk.feed_source_id}")
            # print(f"league_id={fixture.league.league_id}&fixture_id={fixture.fixture_id}&feed_source_id={sbk.feed_source_id}")
            if data != []:
                self.logger.info(f"Market Data Request contains {count(data)} entries")
                for _entry in data:
                    for entry in _entry["participants"]:
                        try:
                            sbkObj = Sportsbook.objects.get(feed_source_id=entry["feed_source_id"],vhost=self.vhost)
                            fixtureObj = Fixture.objects.get(fixture_id=entry["fixture_id"],vhost=self.vhost)
                            # print(self.vhost)
                            fmxObj = process_fixture_market_data(entry, self.vhost, fixtureObj, sbkObj)
                            retr.append(fmxObj)
                            # print("------")
                        except Fixture.DoesNotExist or Sportsbook.DoesNotExist:
                            continue
        return retr

    def fetch_fixture_outcomes(self,**kwargs):
        retr = []
        if "league" in kwargs:
            league = kwargs["league"]
            data = self._make_get_req(self.urls["outcomes"],
                                      data=f"league_id={league.league_id}")
        elif "fixture" in kwargs:
            fixture = kwargs["fixture"]
            league = fixture.league
            data = self._make_get_req(self.urls["outcomes"],
                                  data=f"league_id={fixture.league.league_id}&fixture_id={fixture.fixture_id}")
        # print(f"league_id={fixture.league.league_id}&fixture_id={fixture.fixture_id}&feed_source_id={sbk.feed_source_id}")
        if data != []:
            for entry in data:
                outcomeObj, segments, participants = process_fixture_outcomes_data(entry,self.vhost)
                retr.append([outcomeObj, segments, participants])
        return retr


