import asyncio
import re
from datetime import timedelta, datetime
from decimal import Decimal
from types import SimpleNamespace

import boto3

import httpx
from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from django.db import connections

from django.utils.timezone import now, localtime, make_aware

from asynctools.abc import AsyncWorkerABC


class KIBLAsyncHTTPDDaemon(AsyncWorkerABC):
    last_timestamp = None
    urls = {
        "_prefix":"https://api.kibl.io/sports",
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
    debug = True
    regappid = "dataengine.drivers.kiblio"
    MAX_RETRIES = 10
    RETRY_DELAY = 5

    def __init__(self, vhost = object ,logger = object, name: str = "worker", interval: float = 60,run_in_process: bool = False,loki_url=None,):
        AsyncWorkerABC.__init__(self,vhost, logger, name, interval,run_in_process,loki_url)
        if not run_in_process:  # in forked child
            self._child_init()


    def _child_init(self):
        """
        Runs inside the forked child *after* django.setup().
        Safe place for model imports.
        """
        super()._child_init()

        from dataengine.drivers.kiblio.models import Region, League, MarketGenres, MarketType, MarketTypeSport, \
            MarketStatus, \
            Segment, State, Participant, Sides, Location, FixtureType, Sportsbook, FixtureParticipants, Sport, Season, \
            Fixture
        from dataengine.drivers.kiblio.api.async_common import aprocess_fixture_data, aprocess_fixture_market_data, \
            aprocess_fixture_outcomes_data

        from parameters.models import Timezone, VHostParameterRegistry
        self.last_timestamp = localtime()
        self.models = SimpleNamespace(
            Region=Region,
            League=League,
            MarketGenres=MarketGenres,
            MarketType=MarketType,
            MarketTypeSport=MarketTypeSport,
            MarketStatus=MarketStatus,
            Segment=Segment,
            State=State,
            Participant=Participant,
            Sides=Sides,
            Location=Location,
            FixtureType=FixtureType,
            Sportsbook=Sportsbook,
            FixtureParticipants=FixtureParticipants,
            Sport=Sport,
            Season=Season,
            Fixture=Fixture,
            VHostParameterRegistry=VHostParameterRegistry
        )
        self.aprocess_fixture_data = aprocess_fixture_data
        self.aprocess_fixture_market_data = aprocess_fixture_market_data
        self.aprocess_fixture_outcomes_data = aprocess_fixture_outcomes_data

    async def _get_token(self):
        auth = True
        if not self.expires_at:
            auth = True
        elif self.expires_at < now() and self.token:
            auth = False
        if not auth:
            return self.token
        else:
            un = await sync_to_async(lambda:self.models.VHostParameterRegistry.objects.get(vhost=self.vhost,application=self.regappid,name="username").value_text,thread_sensitive=False)()
            pw = await sync_to_async(lambda: self.models.VHostParameterRegistry.objects.get(vhost=self.vhost, application=self.regappid,name="password").value_text, thread_sensitive=False)()
            cid = await sync_to_async(lambda: self.models.VHostParameterRegistry.objects.get(vhost=self.vhost, application=self.regappid,name="clientid").value_text, thread_sensitive=False)()
            client = boto3.client('cognito-idp','us-west-2')
            response = client.initiate_auth(
                AuthFlow='USER_PASSWORD_AUTH',
                AuthParameters={
                    'USERNAME': un,
                    'PASSWORD': pw,
                },
                ClientId=cid
            )
            # Tokens
            access_token = response['AuthenticationResult']['AccessToken']
            id_token = response['AuthenticationResult']['IdToken']
            refresh_token = response['AuthenticationResult']['RefreshToken']
            self.expires_at = now() + timedelta(seconds=response['AuthenticationResult']['ExpiresIn'])
            self.token = access_token
            self.id_token = id_token
            self.refresh_token = refresh_token
            return self.token

    async def _make_get_req(self,url_key,**kwargs):
        turl = f"{self.urls['_prefix']}/{self.urls[url_key]}"
        if not self.debug:
            if "data" in kwargs:
                turl += f"?{kwargs['data']}"
        else:
            if "data" in kwargs:
                turl += f"?from=solstic&{kwargs['data']}"
        request = await self._fetch_with_retry(turl)
        if not request: return False
        if request.status_code == 401:
            self.token = False
            return False
        if request.status_code != 200:
            self.logger.warning(f"Failed to fetch {self.urls[url_key]}: {request.status_code}")
            self.logger.warning(request.text)
            return False
        else:
            data = request.json()
            if "code" in data and data["code"] != 200:
                self.logger.warning(f"Failed to fetch {self.urls[url_key]}: {data['code']}: {data['description']}")
                return False
            return data["result"]

    async def fetch_sports(self,**kwargs):
        sports_data = await self._make_get_req("sports",**kwargs)
        if not sports_data:
            return False
        for entry in sports_data:
            sportObj,_ = await sync_to_async(lambda:self.models.Sport.objects.get_or_create(sport_id=entry["sport_id"], vhost=self.vhost),thread_sensitive=False)()
            await self._object_setattrs(sportObj, entry)
        return True

    async def fetch_regions(self,**kwargs):
        sports_data = await self._make_get_req("region",**kwargs)

        if not sports_data:
            return False
        for entry in sports_data:
            regionObj,_ = await sync_to_async(lambda:self.models.Region.objects.get_or_create(region_id=entry["region_id"],vhost=self.vhost),thread_sensitive=False)()
            await self._object_setattrs(regionObj, entry)
        return True

    async def fetch_leagues(self,**kwargs):
        data = await self._make_get_req("leagues",**kwargs)
        if not data: return False

        # print(data[0])
        for entry in data:
            # print(entry["sport_id"],entry["region_id"])
            sportObj,c = await sync_to_async(lambda:self.models.Sport.objects.get_or_create(sport_id=entry["sport_id"],vhost=self.vhost),thread_sensitive=False)()
            if c: await sync_to_async(lambda:sportObj.save(),thread_sensitive=False)()
            # print(sportObj)
            regionObj,c = await sync_to_async(lambda:self.models.Region.objects.get_or_create(region_id=entry["region_id"],vhost=self.vhost),thread_sensitive=False)()
            if c: await sync_to_async(lambda:regionObj.save(),thread_sensitive=False)()
            # print(regionObj)
            # print(sportObj,regionObj)
            leagueObj,_ = await sync_to_async(lambda:self.models.League.objects.get_or_create(vhost=self.vhost,sport=sportObj,region=regionObj,league_id=entry["league_id"]),thread_sensitive=False)()
            await self._object_setattrs(leagueObj,entry)
        return True

    async def fetch_market_genres(self):
        data = await self._make_get_req("market_genres")
        if not data: return False
        for entry in data:
            # print(entry)
            genreObj,_ = await sync_to_async(lambda:self.models.MarketGenres.objects.get_or_create(market_genre_id=entry["market_genre_id"],vhost=self.vhost),thread_sensitive=False)()
            # print(entry)
            await self._object_setattrs(genreObj,entry)
        return True

    @database_sync_to_async
    def _debug_leagues(self, ids,vhost_uuid):
        qs = self.models.League.objects.filter(league_id__in=ids)
        print("Total matching league_id:", qs.count())

        qs2 = qs.filter(vhost_id=vhost_uuid)
        print("After vhost filter:", qs2.count())
        qs2f = list(qs2)
        # print(qs2f)
        print("before ret")
        return qs2f
    async def fetch_leagues_in_season(self,**kwargs):
        data = await self._make_get_req("leagues_in_season")
        if not data: return False
        ids = []
        for entry in data:
            ids.append(entry["league_id"])
        vhost_uuid = self.vhost.uuid
        # print(f"Active Leagues for {vhost_uuid}")
        # print(ids)
        qs = self.models.League.objects.filter(league_id__in=ids,vhost_id=vhost_uuid)
        leagues = await sync_to_async(lambda:list(qs),thread_sensitive=False)()
        return leagues
        # return qs

    async def fetch_market_types(self,**kwargs):
        data = await self._make_get_req("market_types")
        if not data: return False
        for entry in data:
            # print(entry)
            genreObj = await sync_to_async(lambda:self.models.MarketGenres.objects.get(market_genre_id=entry["market_genre_id"],vhost=self.vhost),thread_sensitive=False)()
            marketObj,_ = await sync_to_async(lambda:self.models.MarketType.objects.get_or_create(market_type_id=entry["market_type_id"],vhost=self.vhost,genre=genreObj),thread_sensitive=False)()
            # marketObj.genre = genreObj
            await self._object_setattrs(marketObj,entry)
            for k,v in entry["for_sports"].items():
                # print(k,v)
                for y in v:
                    try:
                        sportObj = await sync_to_async(lambda:self.models.Sport.objects.get(sport_id=y, vhost=self.vhost),thread_sensitive=False)()
                    except self.models.Sport.DoesNotExist:
                        sportObj,_ = await sync_to_async(lambda:self.models.Sport.objects.get_or_create(sport_id=y, vhost=self.vhost),thread_sensitive=False)()
                        await sync_to_async(lambda:sportObj.save(),thread_sensitive=False)()
                    mtsObj,_ = await sync_to_async(lambda:self.models.MarketTypeSport.objects.get_or_create(market_type=marketObj,for_sport=sportObj),thread_sensitive=False)()
                    await sync_to_async(lambda:mtsObj.save(),thread_sensitive=False)()
        return True

    async def fetch_market_statuses(self,**kwargs):
        data = await self._make_get_req("market_statuses")
        if not data: return False
        for entry in data:
            mssObj,_ = await sync_to_async(lambda:self.models.MarketStatus.objects.get_or_create(market_status_id=entry["market_status_id"],vhost=self.vhost),thread_sensitive=False)()
            await self._object_setattrs(mssObj,entry)
        return True

    async def fetch_segments(self,**kwargs):
        data = await self._make_get_req("segments")
        if not data: return False
        for entry in data:
            mssObj,_ = await sync_to_async(lambda:self.models.Segment.objects.get_or_create(segment_id=entry["segment_id"],vhost=self.vhost),thread_sensitive=False)()
            await self._object_setattrs(mssObj,entry)
        return True

    async def fetch_seasons(self,**kwargs):
        data = await self._make_get_req("seasons")
        if not data: return False
        for entry in data:
            ssObj,_ = await sync_to_async(lambda:self.models.Season.objects.get_or_create(season_id=entry["season_id"],vhost=self.vhost),thread_sensitive=False)()
            await self._object_setattrs(ssObj,entry)

    async def fetch_states(self,**kwargs):
        data = await self._make_get_req("states")
        if not data: return False
        for entry in data:
            if entry != "code":
                ssObj,_ = await sync_to_async(lambda:self.models.State.objects.get_or_create(state_id=entry["state_id"], vhost=self.vhost),thread_sensitive=False)()
                await self._object_setattrs(ssObj, entry)
        return True

    async def fetch_league_participants(self,**kwargs):
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
                participantObj,_ = await sync_to_async(lambda:self.models.Participant.objects.get_or_create(participant_id=entry["participant_id"],vhost=self.vhost,league=league),thread_sensitive=False)()
            except self.models.Participant.MultipleObjectsReturned:
                participantObj = sync_to_async(lambda:self.models.Participant.objects.filter(participant_id=entry["participant_id"], vhost=self.vhost,
                                                  league=league).first(),thread_sensitive=False)()
            await self._object_setattrs(participantObj,entry)
            sync_to_async(lambda:participantObj.save(),thread_sensitive=False)()
        retr = self.models.Participant.objects.filter(vhost=self.vhost,league=league)
        if "participant_id" in kwargs:
            retr = self.models.Participant.objects.filter(vhost=self.vhost,league=league,participant_id=kwargs["participant_id"])
        return retr


    async def fetch_participants(self,**kwargs):
        if "league" in kwargs:
            leagues = [kwargs["league"]]
        else:
            leagues = await self.fetch_leagues_in_season()
        for league in leagues:
            if "participant_id" in kwargs:
                # print("Kwargs")
                participant = await self.fetch_league_participants(league=league,participant_id=kwargs["participant_id"])
            else:
                participant = await self.fetch_league_participants(league=league)
            # print(participant[0])
        retr = self.models.Participant.objects.filter(vhost=self.vhost)
        if "participant_id" in kwargs:
            # print("PPI")
            retr = self.models.Participant.objects.filter(vhost=self.vhost,participant_id=kwargs["participant_id"])
        # print(retr)
        return retr


    async def fetch_sides(self,**kwargs):
        data = await self._make_get_req("sides")
        if not data: return False
        for entry in data:
            sideObj,_ = await sync_to_async(lambda:self.models.Sides.objects.get_or_create(vhost=self.vhost,side_id=entry['side_id']),thread_sensitive=False)()
            await self._object_setattrs(sideObj,entry)
        return self.models.Sides.objects.filter(vhost=self.vhost)


    async def fetch_locations(self,**kwargs):
        data = await self._make_get_req("locations")
        if not data: return False
        for entry in data:
            sideObj,_ = await sync_to_async(lambda:self.models.Location.objects.get_or_create(vhost=self.vhost,location_id=entry['location_id']),thread_sensitive=False)()
            await self._object_setattrs(sideObj,entry)
        return self.models.Location.objects.filter(vhost=self.vhost)


    async def fetch_fixture_types(self,**kwargs):
        data = await self._make_get_req("fixture_types")
        if not data: return False
        for entry in data:
            ftObj,_ = await sync_to_async(lambda:self.models.FixtureType.objects.get_or_create(vhost=self.vhost,fixture_type_id=entry['fixture_type_id']),thread_sensitive=False)()
            await self._object_setattrs(ftObj,entry)
        return self.models.FixtureType.objects.filter(vhost=self.vhost)


    async def fetch_sportsbooks(self,**kwargs):
        data = await self._make_get_req("sportsbooks")
        if not data: return False
        for entry in data:
            ftObj,_ = await sync_to_async(lambda:self.models.Sportsbook.objects.get_or_create(vhost=self.vhost,feed_source_id=entry['feed_source_id']),thread_sensitive=False)()
            await self._object_setattrs(ftObj,entry)
        return self.models.Sportsbook.objects.filter(vhost=self.vhost)

    async def fetch_league_fixtures(self, league, **kwargs):
        # print("FLF")
        # print("B'")
        # print(type(league))
        league_id = await sync_to_async(lambda:league.league_id,thread_sensitive=False)()
        league_name = await sync_to_async(lambda:league.name,thread_sensitive=False)()
        # print("Leagueid",league_id)
        if "fixture_id" in kwargs:
            data = await self._make_get_req("fixtures", data=f"league_id={league_id}&fixture_id={kwargs['fixture_id']}")
        else:
            data = await self._make_get_req("fixtures",data=f"league_id={league_id}")
        # print("foof")
        if not data: return False
        fixtureObj = None
        self.logger.info(f"Fetching fixtures for league: {league.uuid}/{league_name} contains {len(data)} entries")
        for entry in data:
            # print("EA")
            fixtureObj = await self.aprocess_fixture_data(entry,self.vhost)
            # print("EB")
        if "fixture_id" in kwargs:
            # print(f"Going out swinging! {kwargs["fixture_id"]}")
            return fixtureObj
        else:
            return await sync_to_async(lambda:list(self.models.Fixture.objects.filter(vhost=self.vhost, league=league)),thread_sensitive=False)()


    async def fetch_upcoming_fixtures(self,**kwargs):
        self.logger.info("Fetching upcoming fixtures")
        print("LiS")
        leagues = await self.fetch_leagues_in_season()
        # print('I hath returned')
        # print("A")
        tasks = [
            asyncio.create_task(self.fetch_league_fixtures(league))
            for league in leagues
        ]
        # print("A'")
        results = await asyncio.gather(*tasks)
        # print("B")
        all_fixtures = []
        for res in results:
            if isinstance(res, Exception):
                self.logger.warning(f"Error fetching fixtures: {res}")
            elif res:
                all_fixtures.extend(res)
        return all_fixtures

    async def fetch_fixture_participants(self,fixture,**kwargs):
        data = await self._make_get_req("fixtures_participants",data=f"fixture_id={fixture.fixture_id}")
        participants = []
        if data != []:
            for entry in data:
                # print(entry)
                sideObj = await sync_to_async(lambda:self.models.Sides.objects.get(vhost=self.vhost,side_id=entry["side_id"]),thread_sensitive=False)()
                participantObj = await sync_to_async(lambda:self.models.Participant.objects.get(vhost=self.vhost,participant_id=entry["participant_id"]),thread_sensitive=False)()
                fpObj,_ = await sync_to_async(lambda:self.models.FixtureParticipants.objects.get_or_create(vhost=self.vhost,fixture=fixture,participant=participantObj,side=sideObj,fixture_participant_id=entry["fixture_participant_id"]),thread_sensitive=False)
                await self._object_setattrs(fpObj,entry)
                participants.append(fpObj)
        return participants

    async def fetch_fixture_markets(self,**kwargs):
        self.logger.info("Fetching upcoming fixture Markets...")
        leagues = await self.fetch_leagues_in_season()
        if not leagues:
            return []
        #print("A")
        tasks = [
            asyncio.create_task(self._fetch_fixture_markets(league=league))
            for league in leagues
        ]
        results = await asyncio.gather(*tasks,return_exceptions=True)
        #print("B")
        all_fixtures = []
        for res in results:
            if isinstance(res, Exception):
                self.logger.warning(f"Error fetching Markets: {res}")
            elif res:
                all_fixtures.extend(res)
        return all_fixtures

    async def _fetch_fixture_markets(self,**kwargs):

        retr = []
        data = []
        # print("Fetching fixture markets {kwargs}".format(kwargs=kwargs))
        for sbk in await sync_to_async(lambda:list(self.models.Sportsbook.objects.filter(vhost=self.vhost,active=True)),thread_sensitive=False)():
            if "league" in kwargs:
                league = kwargs["league"]
                # print(f"league_id={league.league_id}&feed_source_id={sbk.feed_source_id}")
                data = await self._make_get_req("markets",
                                          data=f"league_id={league.league_id}&feed_source_id={sbk.feed_source_id}")
            elif "fixture" in kwargs:
                fixture = kwargs["fixture"]
                league = fixture.league
                # print(f"league_id={fixture.league.league_id}&fixture_id={fixture.fixture_id}&feed_source_id={sbk.feed_source_id}")
                data = self._make_get_req("markets",data=f"league_id={fixture.league.league_id}&fixture_id={fixture.fixture_id}&feed_source_id={sbk.feed_source_id}")
            # else:
                # print("No fixture, no League? No chance.")
            # print(f"league_id={fixture.league.league_id}&fixture_id={fixture.fixture_id}&feed_source_id={sbk.feed_source_id}")
            if not data: return False
            if data != []:
                for _entry in data:
                    for entry in _entry["participants"]:
                        # if int(entry["market_type_id"]) == 7:
                        #     print(_entry)
                        try:
                            sbkObj = await sync_to_async(lambda:self.models.Sportsbook.objects.get(feed_source_id=entry["feed_source_id"],vhost=self.vhost),thread_sensitive=False)()
                            fixtureObj = await sync_to_async(lambda:self.models.Fixture.objects.get(fixture_id=entry["fixture_id"],vhost=self.vhost),thread_sensitive=False)()
                            # print(self.vhost)
                            fmxObj = await self.aprocess_fixture_market_data(entry, self.vhost, fixtureObj, sbkObj)
                            retr.append(fmxObj)
                            # print("------")
                        except self.models.Fixture.DoesNotExist or self.models.Sportsbook.DoesNotExist:
                            continue
                self.logger.info(f"Fixture Markets Data contains: {len(data)} entries - processed.")
            # else:
            #     self.logger.info(f"Fixture Markets Data contains no entries")
        return retr

    async def fetch_fixture_outcomes(self,**kwargs):
        self.logger.info("Fetching current fixture outcomes")
        leagues = await self.fetch_leagues_in_season()
        if not leagues:
            return []
        #print("A")
        tasks = [
            asyncio.create_task(self._fetch_fixture_outcomes(league=league))
            for league in leagues
        ]
        results = await asyncio.gather(*tasks,return_exceptions=True)
        #print("B")
        all_fixtures = []
        for res in results:
            if isinstance(res, Exception):
                self.logger.warning(f"Error fetching fixture Outcomes: {res}")
            elif res:
                all_fixtures.extend(res)
        return all_fixtures

    async def _fetch_fixture_outcomes(self,**kwargs):
        # self.logger.info("Fetching fixture outcomes")
        retr = []
        data = []
        if "league" in kwargs:
            league = kwargs["league"]
            data = await self._make_get_req("outcomes",data=f"league_id={league.league_id}")
        elif "fixture" in kwargs:
            fixture = kwargs["fixture"]
            league = fixture.league
            data = await self._make_get_req("outcomes",data=f"league_id={fixture.league.league_id}&fixture_id={fixture.fixture_id}")
        # print(f"league_id={fixture.league.league_id}&fixture_id={fixture.fixture_id}&feed_source_id={sbk.feed_source_id}")
        if not data: return False
        if data != []:
            # self.logger.info(f"Fixture Outcomes Data contains {len(data)} entries")
            for entry in data:
                outcomeObj, segments, participants = await self.aprocess_fixture_outcomes_data(entry,self.vhost)
                retr.append([outcomeObj, segments, participants])
        return retr

    async def _reset_auth(self):
        self.token = False
        token = await self._get_token()
        headers = {"Authorization": f"{token}"}
        self.client = httpx.AsyncClient(headers=headers,limits=self.httpx_limits,timeout=self.httpx_timeout)

    async def start(self):
        await self._reset_auth()
        await AsyncWorkerABC.start(self)

    async def _work_cycle(self):
        print("KIBL Tick")
        self.logger.info("KIBLHTTPd Tick .....")
        # if not self.last_timestamp:
            # await asyncio.gather(
                # self.fetch_sports(),
                # self.fetch_regions(),
                # self.fetch_leagues(),
                # self.fetch_market_types(),
                # self.fetch_market_statuses(),
                # self.fetch_segments(),
                # self.fetch_seasons(),
                # self.fetch_states(),
                # self.fetch_sides(),
                # self.fetch_locations(),
                # self.fetch_fixture_types(),
                # self.fetch_sportsbooks()
            # )
            # self.logger.info("KIBLHTTPd Initial setup complete")
        # print("A")
        await asyncio.gather(
            self.fetch_upcoming_fixtures(),
            self.fetch_fixture_markets(),
            self.fetch_fixture_outcomes(),
            return_exceptions = True
        )
        self.last_timestamp = localtime()
        # print("B")
        await sync_to_async(lambda:connections.close_all(),thread_sensitive=False)()
        print("KIBL Tock")
        self.logger.info(f"KIBLHTTPd Data Run Complete!")

