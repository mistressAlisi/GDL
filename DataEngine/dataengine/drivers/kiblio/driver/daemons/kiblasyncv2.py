import asyncio
import decimal
import json
import re
import traceback
from datetime import timedelta, datetime, time
from decimal import Decimal
from types import SimpleNamespace
from typing import Dict, List
from uuid import UUID

import boto3

import httpx
import numpy as np

from aio_pika import IncomingMessage, connect_robust
from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from django.db import connections, IntegrityError
from django.utils.text import slugify

from django.utils.timezone import now, localtime, make_aware
from kombu.utils import fxrange

from asynctools.abc import AsyncWorkerABC
from grader.toolkit.parlays import three_way_juicer, validate_three_way


class KIBLAsyncDaemonV2(AsyncWorkerABC):
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
    debug = False
    verbose = False
    regappid = "dataengine.drivers.kiblio"
    MAX_RETRIES = 10
    RETRY_DELAY = 5

    def __init__(self, vhost = object ,logger = object, name: str = "KIBLAsyncDaemonV2", interval: float = 60,run_in_process: bool = False,loki_url=None,):
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
            Segment, State, Participant, Sides, Location, FixtureType, Sportsbook, FixtureParticipants,\
            Fixture,OutcomeParticipants,FixtureMarket,OutcomeSegmentScore,Outcome
        from dataengine.drivers.kiblio.api.async_common import aprocess_fixture_data, aprocess_fixture_market_data, \
            aprocess_fixture_outcomes_data

        from parameters.models import VHostParameterRegistry
        from matches.models import Match
        from odds.models import MatchOddsSummary
        from outcomes.models import (
            OutcomeTeams as Sys_OutcomeTeams,
            Outcome as Sys_Outcome,
            OutcomeSegmentScore as Sys_OutcomeSegmentScore
        )
        from sports.models import Group, Sport, Season
        from teams.models import Team, TeamSport
        from matches.models import Match as Sys_Match
        self.last_timestamp = localtime() - timedelta(days=1)
        self.models = SimpleNamespace(
            Fixture=Fixture,
            Sides=Sides,
            FixtureParticipants=FixtureParticipants,
            OutcomeParticipants=OutcomeParticipants,
            MarketType=MarketType,
            Segment=Segment,
            FixtureMarket=FixtureMarket,
            Outcome=Outcome,
            OutcomeSegmentScore=OutcomeSegmentScore,
            Match=Match,
            MatchOddsSummary=MatchOddsSummary,
            Sys_OutcomeTeams=Sys_OutcomeTeams,
            Sys_Outcome=Sys_Outcome,
            Sys_OutcomeSegmentScore=Sys_OutcomeSegmentScore,
            Group=Group,
            Sport=Sport,
            Season=Season,
            Team=Team,
            TeamSport=TeamSport,
            Sys_Match=Sys_Match,
            Region=Region,
            League=League,
            MarketGenres=MarketGenres,
            MarketTypeSport=MarketTypeSport,
            MarketStatus=MarketStatus,
            State=State,
            Participant=Participant,
            Location=Location,
            FixtureType=FixtureType,
            Sportsbook=Sportsbook,
            VHostParameterRegistry=VHostParameterRegistry


        )
        self.aprocess_fixture_data = aprocess_fixture_data
        self.aprocess_fixture_market_data = aprocess_fixture_market_data
        self.aprocess_fixture_outcomes_data = aprocess_fixture_outcomes_data
        self._connection = None
        self._channel = None
        self._queues = []
        self._connected = asyncio.Event()
        self.amqp_url = "amqps://miker:MikeR88!@rabbitmq.kibl.io/"
        from dataengine.drivers.kiblio.api.common import process_fixture_data
        from dataengine.drivers.kiblio.api.common import process_fixture_outcomes_data
        from dataengine.drivers.kiblio.api.common import process_fixture_market_data
        from grader.toolkit.parlays import american_juicer_v2, american_to_fraction_str
        self.process_fixture_outcomes_data = process_fixture_outcomes_data
        self.process_fixture_data = process_fixture_data
        self.process_fixture_market_data = process_fixture_market_data
        self.american_juicer_v2 = american_juicer_v2
        self.three_way_juicer = three_way_juicer
        self.american_to_fraction_str = american_to_fraction_str
        self.constants = SimpleNamespace(
            TWML = self.models.MarketType.objects.get(abrv="2WML", vhost=self.vhost),
            W3ML=self.models.MarketType.objects.get(abrv="3WML", vhost=self.vhost),
            FG = self.models.Segment.objects.get(abrv="FG", vhost=self.vhost),
            HOME = self.models.Sides.objects.get(abrv="HOME", vhost=self.vhost),
            VISITOR = self.models.Sides.objects.get(abrv="VISITOR", vhost=self.vhost),
            DRAW = self.models.Sides.objects.get(abrv="DRAW", vhost=self.vhost)
            
        )
        self._sync_task: asyncio.Task | None = None





    #---------------------------
    # HTTP STUFF
    #---------------------------
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
        # print("C'")
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
        if self.verbose:
            self.logger.info(f"Fetching fixtures for league: {league.uuid}/{league_name} contains {len(data)} entries")
        for entry in data:
            # print("EA")
            fixtureObj = await self.aprocess_fixture_data(entry,self.vhost,self.logger)
            # print("EB")
        if "fixture_id" in kwargs:
            # print(f"Going out swinging! {kwargs["fixture_id"]}")
            return fixtureObj
        else:
            return await sync_to_async(lambda:list(self.models.Fixture.objects.filter(vhost=self.vhost, league=league)),thread_sensitive=False)()


    async def fetch_upcoming_fixtures(self,**kwargs):
        self.logger.info("Fetching upcoming fixtures")
        # print("LiS")
        leagues = await self.fetch_leagues_in_season()
        # print('I hath returned')
        # print("A'")
        tasks = [
            asyncio.create_task(self.fetch_league_fixtures(league))
            for league in leagues
        ]
        # print("A'")
        results = await asyncio.gather(*tasks)
        # print("B''")
        all_fixtures = []
        for res in results:
            if isinstance(res, Exception):
                tb = "".join(
                    traceback.format_exception(type(res), res, res.__traceback__)
                )

                self.logger.error(
                    "Error fetching fixtures task crashed:\n%s",
                    tb,
                )
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
        # leagues = await sync_to_async(lambda:list(self.models.League.objects.filter(uuid=UUID('b15b50cb-0d82-46b6-b943-bfba92ca12fa'))),thread_sensitive=False)()
        #print("A")
        tasks = [
            asyncio.create_task(self._fetch_fixture_markets(league=league))
            for league in leagues
        ]
        all_fixtures = []
        for coro in asyncio.as_completed(tasks):
            try:
                res = await coro
            except Exception:
                # full traceback
                self.logger.error(
                    "Error fetching Markets",
                    exc_info=True,
                )
                continue
            if res:
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
            if not data: return False
            if data != []:
                for _entry in data:
                    # print("_entry********")
                    # print(_entry)
                    # print("***************")
                    for entry in _entry["participants"]:
                        # if int(entry["market_type_id"]) == 7:
                        #     print(_entry)
                        # print("ENTRY*****")
                        # print(entry)
                        # print("**********")
                        # print("P")
                        try:
                            sbkObj = await sync_to_async(lambda:self.models.Sportsbook.objects.get(feed_source_id=entry["feed_source_id"],vhost=self.vhost),thread_sensitive=False)()
                            fixtureObj = await sync_to_async(lambda:self.models.Fixture.objects.get(fixture_id=entry["fixture_id"],vhost=self.vhost),thread_sensitive=False)()
                            # print(self.vhost)
                            # print("FMX")
                            # try:
                            fmxObj = await self.aprocess_fixture_market_data(entry, self.vhost, fixtureObj, sbkObj, league)
                            # except Exception as e:
                            #     traceback.print_exc()
                            # print("PFMX")
                            retr.append(fmxObj)

                            # await sync_to_async(lambda:print(fmxObj),thread_sensitive=False)()
                            # print("------")
                            asyncio.create_task(self.process_fixture(fixtureObj))

                        except self.models.Fixture.DoesNotExist or self.models.Sportsbook.DoesNotExist:
                            continue
                self.logger.info(f"League {league.name}:  Fixture Markets Data contains: {len(data)} entries - processed.")
            else:
                if self.verbose:
                    self.logger.info(f"Fixture Markets Data contains no entries")
        return retr


    async def fetch_fixture_outcomes(self,**kwargs):
        self.logger.info("Fetching current fixture outcomes")
        leagues = await self.fetch_leagues_in_season()
        if not leagues:
            return []
        # print("FFCO")
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



    #---------------------------
    # AQMP STUFF
    #---------------------------
    async def _connect(self):
        """Establish AMQP connection and channel."""
        try:
            self._connection = await connect_robust(self.amqp_url)
            self._channel = await self._connection.channel()
            self._connected.set()
            self.logger.info("Connected to RabbitMQ.")
        except Exception as e:
            self.logger.error(f"AMQP connection failed: {e}")
            await asyncio.sleep(10)

    async def _subscribe(self):
        """Attach consumers to queues."""
        queues = [
            ("miker.get.info.markets", self._on_mkt_message),
            ("miker.get.info.fixtures", self._on_fxt_message),
            ("miker.get.info.outcomes", self._on_outc_message),
        ]
        for queue_name, handler in queues:
            try:
                queue = await self._channel.declare_queue(queue_name, durable=True)
                await queue.consume(lambda msg: asyncio.create_task(handler(msg)))
                self._queues.append(queue)
                self.logger.info(f"Subscribed to queue: {queue_name}")
            except Exception as e:
                self.logger.error(f"Failed to subscribe to {queue_name}: {e}")

    async def _safe_close_connection(self):
        try:
            if self._channel and not self._channel.is_closed:
                await self._channel.close()
        except Exception:
            pass

        try:
            if self._connection and not self._connection.is_closed:
                await self._connection.close()
        except Exception:
            pass

    async def _run(self):
        self.setup_loop()

        if self.loki_url:
            await self.loki_logger_start()

        backoff = 2
        MAX_BACKOFF = 60

        self.logger.info("Sync loop started")

        # force running
        self._running = True
        self._exit = False

        while not self._exit:
            try:
                # ───── ensure connection ─────
                if not self._connection or self._connection.is_closed:
                    self.logger.warning("Pika not connected — attempting reconnect")
                    await self._connect()

                if not self._connection or self._connection.is_closed:
                    raise RuntimeError("RabbitMQ unavailable after connect")

                await self._subscribe()

                # reset backoff once healthy
                backoff = 2

                # ───── main work loop ─────
                while not self._exit:
                    if not self._connection or self._connection.is_closed:
                        raise RuntimeError("RabbitMQ connection dropped")

                    try:
                        await self._work_cycle()
                    except asyncio.CancelledError:
                        raise
                    except Exception:
                        self.logger.error(
                            "🔥 Exception inside work cycle — continuing",
                            exc_info=True,
                        )

                    await asyncio.sleep(self.interval)

            except asyncio.CancelledError:
                self.logger.info("Worker cancelled")
                break

            except Exception:
                self.logger.exception("🔥 Connection loop crashed — reconnecting")

                await self._safe_close_connection()

                await asyncio.sleep(backoff)
                backoff = min(backoff * 2, MAX_BACKOFF)

        await self._cleanup()

    async def _on_mkt_message(self, message: IncomingMessage):
        async with message.process(ignore_processed=True):
            try:
                mkt_msg = json.loads(message.body.decode("utf-8"))
                for entry in mkt_msg.get("result", []):
                    for participant in entry.get("participants", []):
                        await self._handle_market_update(participant)
            except Exception as e:
                self.logger.exception(f"Error processing market message: {e}")

    async def _on_fxt_message(self, message: IncomingMessage):
        async with message.process(ignore_processed=True):
            try:
                fxt_msg = json.loads(message.body.decode("utf-8"))
                api_key = fxt_msg.get("api_key")

                if api_key == "get_sport_market_info_by_interest:markets":
                    return await self._on_mkt_message(message)
                if api_key != "get_sport_market_info_by_interest:fixtures":
                    self.logger.debug(f"Ignored fixture message with key: {api_key}")
                    return

                for entry in fxt_msg.get("result", []):
                    fixture_obj = await self.aprocess_fixture_data(entry, self.vhost,self.logger)
                    if self.verbose:
                        self.logger.info(f"Updated fixture {fixture_obj.fixture_id} from AMQP.")

            except Exception as e:
                self.logger.exception(f"Error processing fixture message: {e}")

    async def _on_outc_message(self, message: IncomingMessage):
        async with message.process(ignore_processed=True):
            try:
                outc_msg = json.loads(message.body.decode("utf-8"))
                api_key = outc_msg.get("api_key")

                if api_key == "get_sport_market_info_by_interest:markets":
                    return await self._on_mkt_message(message)
                if api_key != "get_sport_market_info_by_interest:outcomes":
                    self.logger.debug(f"Ignored outcome message with key: {api_key}")
                    return

                for entry in outc_msg.get("result", []):
                    outcome_obj, _, _ = await self.aprocess_fixture_outcomes_data(
                        entry, self.vhost
                    )
                    if outcome_obj:
                        osync = await sync_to_async(lambda: outcome_obj.fixture.fixture_id,thread_sensitive=False)()
                        if self.verbose:
                            self.logger.info(f"Updated fixture {osync} outcomes from AMQP.")
            except Exception as e:
                self.logger.exception(f"Error processing outcome message: {e}")

    async def _handle_market_update(self, participant):
        """ORM handler for market messages."""
        # if self.debug:
        #     self.logger.info(f"Handle Market Update - Fixture: {participant["fixture_id"]}")
        try:
            sbk_obj = await sync_to_async(lambda:self.models.Sportsbook.objects.get(feed_source_id=participant["feed_source_id"],vhost=self.vhost),thread_sensitive=False)()
            fixture_obj = await sync_to_async(lambda:self.models.Fixture.objects.get(fixture_id=participant["fixture_id"],vhost=self.vhost),thread_sensitive=False)(
            )
            leagueObj = await sync_to_async(lambda:fixture_obj.league,thread_sensitive=False)()
            fmx_obj = await self.aprocess_fixture_market_data(
                participant, self.vhost, fixture_obj, sbk_obj, leagueObj
            )
            if fmx_obj:
                osync = await sync_to_async(lambda: fixture_obj.fixture_id,thread_sensitive=False)()
                if self.verbose:
                    self.logger.info(f"Updated Markets for fixture {osync} from AMQP.")
        except Exception as e:
            self.logger.warning(f"Market update failed for participant {participant}: {e}")
            self.logger.warning(f"Failing Participant: {participant}.")

    #---------------------------
    # DATA ENGINE SYNC STUFF
    #---------------------------
    # -------------------------
    # Basic helpers (ORM via dbcall)
    # -------------------------
    async def get_participant(self, fixture, side_obj):
        """Return the first FixtureParticipants for a fixture and side, or None."""
        return await sync_to_async(
            lambda: self.models.FixtureParticipants.objects.using("default").filter(
                vhost=self.vhost,
                fixture=fixture,
                side=side_obj
            ).first(),thread_sensitive=False)()

    def fixture_format_sync(self, fixture, home, away):
        """Return the big nested dict as in your original function."""
        sport_key = fixture.league.abrv if fixture.league and fixture.league.abrv else slugify(fixture.league.name)
        home_key = home.participant.abrv if getattr(home.participant, "abrv", None) else slugify(home.participant.name)
        away_key = away.participant.abrv if getattr(away.participant, "abrv", None) else slugify(away.participant.name)

        return {
            "group_data": {
                "id": fixture.league.sport.sport_id,
                "slug": fixture.league.sport.abrv,
                "name": fixture.league.sport.name,
                "inserted_on": fixture.league.sport.inserted_on,
                "inserted_on_epoch": fixture.league.sport.inserted_on_epoch,
                "object_uuid": fixture.league.sport.uuid,
                "object_type": f"{fixture.league.sport._meta.app_label}.{fixture.league.sport._meta.model_name}.{fixture.league.sport._meta.object_name}"
            },
            "sport_data": {
                "id": fixture.league.league_id,
                "key": sport_key,
                "title": fixture.league.name,
                "logo": getattr(fixture.league, "logo", None),
                "group": fixture.league.sport,
                "sport_mask": getattr(fixture.league, "sport_mask", None),
                "group_type": f"{fixture.league.sport._meta.app_label}.{fixture.league.sport._meta.model_name}.{fixture.league.sport._meta.object_name}",
                "group_uuid": fixture.league.sport.uuid,
                "inserted_on": fixture.league.inserted_on,
                "inserted_on_epoch": fixture.league.inserted_on_epoch,
                "object_uuid": fixture.league.uuid,
                "object_type": f"{fixture.league._meta.app_label}.{fixture.league._meta.model_name}.{fixture.league._meta.object_name}"
            },
            "teams_data": {
                "home": {
                    "id": home.participant_id,
                    "key": home_key,
                    "name": home.participant.name,
                    "country": getattr(home.participant, "country", None),
                    "bday": getattr(home.participant, "bday", None),
                    "logo": getattr(home.participant, "logo", None),
                    "mascot": home.participant.mascot,
                    "parent_team": home.fixture_participant_id,
                    "inserted_on": home.inserted_on,
                    "home_sport": fixture.league,
                    "sport_type": f"{fixture.league._meta.app_label}.{fixture.league._meta.model_name}.{fixture.league._meta.object_name}",
                    "sport_uuid": fixture.league.uuid,
                    "object_uuid": home.uuid,
                    "object_type": f"{home._meta.app_label}.{home._meta.model_name}.{home._meta.object_name}"
                },
                "away": {
                    "id": away.participant_id,
                    "key": away_key,
                    "name": away.participant.name,
                    "country": getattr(away.participant, "country", None),
                    "bday": getattr(away.participant, "bday", None),
                    "logo": getattr(away.participant, "logo", None),
                    "mascot": away.participant.mascot,
                    "parent_team": away.fixture_participant_id,
                    "inserted_on": away.inserted_on,
                    "away_sport": fixture.league,
                    "sport_type": f"{fixture.league._meta.app_label}.{fixture.league._meta.model_name}.{fixture.league._meta.object_name}",
                    "sport_uuid": fixture.league.uuid,
                    "object_uuid": away.uuid,
                    "object_type": f"{away._meta.app_label}.{away._meta.model_name}.{away._meta.object_name}"
                }
            },
            "season_data": {
                "id": fixture.season.season_id,
                "season_key": fixture.season.abrv,
                "name": fixture.season.name,
                "inserted_on": fixture.season.inserted_on,
                "inserted_on_epoch": fixture.season.inserted_on_epoch,
                "object_uuid": fixture.season.uuid,
                "object_type": f"{fixture.season._meta.app_label}.{fixture.season._meta.model_name}.{fixture.season._meta.object_name}"
            },
            "match_data": self.fixture_format_match_sync(fixture),
        }
    
    def fixture_format_match_sync(self, fixture):
        """Return a dict representing match_data as in original code."""
        if fixture.routing_key == "{}.{}.{}.{}.{}.{}.{}":
            routing_key = None
        else:
            routing_key = fixture.routing_key
        if fixture.state:
            status_long = fixture.state.name
            status_short = fixture.state.abrv
        else:
            status_long = "Upcoming"
            status_short = "UP"
        return {
            "id": fixture.fixture_id,
            "routing_key": routing_key,
            "name": fixture.name,
            "commence_time": fixture.start_time,
            "status_long": status_long,
            "status_short": status_short,
            "object_uuid": fixture.uuid,
            "object_type": f"{fixture._meta.app_label}.{fixture._meta.model_name}.{fixture._meta.object_name}",
        }
    # -------------------------
    # Outcome / segment / team syncs (optimized concurrency)
    # -------------------------
    async def create_and_update_outcome_team(self, outcome, participant_objs,team_sync_map,match):
        """
        Create or update Sys_OutcomeTeams for each participant in parallel (bounded),
        using a pre-built team_sync_map to avoid repeated DB lookups.
        Preloads participant objects to prevent hanging on lazy attributes.
        """
        results = []
        sem = asyncio.Semaphore(10)

        # preload participants
        participants_with_objs = [(p, p.participant) for p in participant_objs]

        async def _process_participant(p_obj, participant,matchObj):
            async with sem:
                puuid = participant.uuid
                team_sync = team_sync_map.get(puuid)
                if not team_sync:
                    if self.verbose:
                        league = await sync_to_async(lambda:matchObj.sport,thread_sensitive=False)()
                        self.logger.info(f"Unable to find Participant match for {matchObj.uuid}, Participant: {puuid} Match name: {matchObj.name} @ League {league.name}/{league.uuid}")

                    # self.logger.info(team_sync_map.keys())
                    return None

                team = await sync_to_async(lambda: team_sync.team,thread_sensitive=False)()

                ckargs = {
                    "vhost": self.vhost,
                    "outcome": outcome,
                    "team": team,
                    "driver": "kiblio.fixture.Fixture",
                    "routing_key": p_obj.routing_key,
                }

                # get_or_create via ORM wrapper
                try:
                    sys_team_obj, created = await sync_to_async(lambda:self.models.Sys_OutcomeTeams.objects.get_or_create(**ckargs),thread_sensitive=False)()
                except self.models.Sys_OutcomeTeams.MultipleObjectsReturned:
                    sys_team_obj = await sync_to_async(lambda:self.models.Sys_OutcomeTeams.objects.filter(**ckargs).first(),thread_sensitive=False)()

                # update fields then save
                sys_team_obj.is_winner = p_obj.is_winner
                sys_team_obj.score = p_obj.score
                sys_match_home_team = await sync_to_async(lambda:match.home_team, thread_sensitive=False)()
                sys_match_away_team = await sync_to_async(lambda:match.away_team, thread_sensitive=False)()
                if sys_match_home_team == team:
                    outcome.last_home_score = p_obj.score
                elif sys_match_away_team == team:
                    outcome.last_away_score = p_obj.score
                await sync_to_async(lambda:outcome.save(),thread_sensitive=False)()
                await sync_to_async(lambda:sys_team_obj.save(),thread_sensitive=False)()

                # self.logger.info("Match Debug Stats",match,sys_match_home_team,sys_match_away_team,team)
                return sys_team_obj
        tasks = [asyncio.create_task(_process_participant(p_obj, participant,match)) for p_obj, participant in
                 participants_with_objs]
        if tasks:
            done = await asyncio.gather(*tasks,return_exceptions=True)
            results = [r for r in done if r is not None]

        return results

    async def create_and_update_outcome_segments(self, outcome, segment_objs,team_sync_map):
        """
        Create or update Sys_OutcomeSegmentScore for each segment in parallel (bounded),
        using a pre-built team_sync_map to avoid repeated DB lookups.
        Preloads participant objects to prevent hanging on lazy attributes.
        """
        results = []
        sem = asyncio.Semaphore(10)

        # preload participants
        segments_with_participants = await sync_to_async(lambda:[(s, s.participant) for s in segment_objs],thread_sensitive=False)()

        async def _process_segment(s, participant):
            async with sem:
                puuid = participant.uuid
                team_sync = team_sync_map.get(puuid)
                if not team_sync:
                    return None
                team = await sync_to_async(lambda: team_sync.team,thread_sensitive=False)()
                s_name = await sync_to_async(lambda:s.segment.name,thread_sensitive=False)()
                try:
                    sys_outcome_obj, created = await sync_to_async(lambda:
                        self.models.Sys_OutcomeSegmentScore.objects.using("default").get_or_create(
                        vhost=self.vhost,
                        outcome=outcome,
                        team=team,
                        driver="kiblio.fixture.Fixture",
                        segment=s_name),thread_sensitive=False)()

                except self.models.Sys_OutcomeSegmentScore.MultipleObjectsReturned:
                    sys_outcome_obj = await sync_to_async(lambda:self.models.Sys_OutcomeSegmentScore.using("default").objects.filter(
                        vhost=self.vhost,
                        outcome=outcome,
                        team=team,
                        driver="kiblio.fixture.Fixture",
                        segment=s_name).first(),thread_sensitive=False)()

                sys_outcome_obj.score = s.score
                sys_outcome_obj.is_winner = s.is_winner
                await sync_to_async(lambda:sys_outcome_obj.save(),thread_sensitive=False)()
                return sys_outcome_obj

        tasks = [asyncio.create_task(_process_segment(s, participant)) for s, participant in segments_with_participants]
        if tasks:
            done = await asyncio.gather(*tasks,return_exceptions=True)
            results = [r for r in done if r is not None]
        return results

    def _clear_existing_outcomes(self,match,outcome_obj):
        sys_out_objs = self.models.Sys_Outcome.objects.using("default").filter(
            vhost=self.vhost,
            match=match,
            driver="kiblio.fixture.Fixture",
            outcome_id=outcome_obj.outcome_id,

            routing_key=outcome_obj.routing_key,
        )
        for sys_out_obj in sys_out_objs:
            sys_out_obj.is_current = False
            sys_out_obj.save()



    def create_and_update_outcome(self, match, outcome_obj):
        """
        Synchronous by design, used via dbcall where necessary.
        """
        self._clear_existing_outcomes(match, outcome_obj)
        try:
            sys_out_obj, created = self.models.Sys_Outcome.objects.using("default").get_or_create(
                vhost=self.vhost,
                match=match,
                driver="kiblio.fixture.Fixture",
                outcome_id=outcome_obj.outcome_id,
                segment=outcome_obj.segment.name,
                routing_key=outcome_obj.routing_key,
            )
        except KeyError:
            self.logger.error("Outcomes KeyError")
            self.logger.error(outcome_obj)
            return None
        except self.models.Sys_Outcome.MultipleObjectsReturned:
            sys_out_obj = self.models.Sys_Outcome.objects.using("default").filter(
                vhost=self.vhost,
                match=match,
                driver="kiblio.fixture.Fixture",
                outcome_id=outcome_obj.outcome_id,
                segment=outcome_obj.segment.name,
                routing_key=outcome_obj.routing_key,
            ).first()

        sys_out_obj.clock = outcome_obj.clock
        sys_out_obj.is_current = True
        sys_out_obj.is_start_game = outcome_obj.is_start_game
        sys_out_obj.is_end_game = outcome_obj.is_end_game
        sys_out_obj.is_start_segment = outcome_obj.is_start_segment
        sys_out_obj.is_end_segment = outcome_obj.is_end_segment
        sys_out_obj.save()
        return sys_out_obj

    # -------------------------
    # Main per-fixture processing (optimized)
    # -------------------------
    async def process_fixture(self, fixture):
        """
        Process a single fixture:
         - find participants
         - create/update match (via find_sync_object or create_match)
         - sync ML markets
         - sync outcomes & outcome details (segments + teams) concurrently
        """
        if self.verbose:
            self.logger.info(f"Processing Fixture: {fixture.uuid}")
            # print(f"Processing Fixture: {fixture.uuid}")
        # Participants (parallel)
        hTeObj, aTeObj = await asyncio.gather(
            self.get_participant(fixture, self.constants.HOME),
            self.get_participant(fixture, self.constants.VISITOR)
        )

        if not (hTeObj and aTeObj):
            if self.verbose:
                self.logger.info(f"Can't Process Fixture: {fixture.uuid} - No Home and Away Teams.")
                print(f"Can't Process Fixture: {fixture.uuid} - No Home and Away Teams.")
            return

        # Step One: find or create match link
        sys_linkObj = await self.find_sync_object("match", f"kiblio.fixture.Fixture", fixture.uuid)
        if not sys_linkObj:
            # prepare args using fixture_format_sync via dbcall (pure-Python but wrap for thread-safety with related attributes)
            self.logger.info(f"Fixture is not linked: {fixture.uuid}")
            qmargs = await sync_to_async(lambda:self.fixture_format_sync(fixture, hTeObj, aTeObj),thread_sensitive=False)()
            # try:
            matchObj, sys_linkObj = await self.create_match(**qmargs)
            # except Exception as e:
                # if self.verbose:
                #     self.logger.info(f"Fixture Could not be created: {fixture.uuid}: {e}")
                #     traceback.print_exc()
                # return
            if not matchObj:
                if self.verbose:
                    self.logger.info(f"Fixture SKIPPED: {fixture.uuid}->Sport or Group is disabled.")
                return
            match_uuid = await sync_to_async(lambda:matchObj.uuid,thread_sensitive=False)()
            sys_link = await self.create_sync_object("match", matchObj,"kiblio.fixture.Fixture" , fixture.uuid)
            sys_link.match = matchObj
            await sync_to_async(lambda: sys_link.save(), thread_sensitive=False)()
            if self.verbose:
                self.logger.info(f"Fixture Linked: {fixture.uuid}->{match_uuid}")
        else:
            # Do not Sync Status
            matchObj = await sync_to_async(lambda: sys_linkObj.match,thread_sensitive=False)()
            match_data = await sync_to_async(self.fixture_format_match_sync,thread_sensitive=False)(fixture)
            if not matchObj.manual_data:
                await self._object_setattrs(matchObj, match_data, rows=["status_short", "status_long", "commence_time"])
                await sync_to_async(matchObj.save,thread_sensitive=False)()
                if self.verbose:
                    self.logger.info(f"Fixture {fixture.uuid} updated")

            else:
                self.logger.info(f"Fixture {fixture.uuid} is linked to Match {matchObj.uuid} which has manual data - ignoring.")
            

        # Step 2.1: ML Markets
        mlc = await sync_to_async(lambda:self.models.FixtureMarket.objects.using("default").filter(vhost=self.vhost, fixture=fixture, market_type=self.constants.TWML, segment=self.constants.FG).count(),thread_sensitive=False)()

        if mlc >= 2:
            try:
                try:
                    homeMLObj = await sync_to_async(lambda:self.models.FixtureMarket.objects.using("default").get(vhost=self.vhost, fixture=fixture, market_type=self.constants.TWML, segment=self.constants.FG, side=self.constants.HOME),thread_sensitive=False)()
                except self.models.FixtureMarket.MultipleObjectsReturned:
                    homeMLObj = await sync_to_async(lambda:self.models.FixtureMarket.objects.using("default").filter(vhost=self.vhost, fixture=fixture, market_type=self.constants.TWML, segment=self.constants.FG, side=self.constants.HOME).first(),thread_sensitive=False)()

                try:
                    awayMLObj = await sync_to_async(lambda:self.models.FixtureMarket.objects.using("default").get(vhost=self.vhost, fixture=fixture, market_type=self.constants.TWML, segment=self.constants.FG, side=self.constants.VISITOR),thread_sensitive=False)()
                except self.models.FixtureMarket.MultipleObjectsReturned:
                    awayMLObj = await sync_to_async(lambda:self.models.FixtureMarket.objects.using("default").filter(vhost=self.vhost, fixture=fixture, market_type=self.constants.TWML, segment=self.constants.FG, side=self.constants.VISITOR).first(),thread_sensitive=False)()

                await sync_to_async(lambda:self.sync_match_ml_markets(matchObj, homeMLObj, awayMLObj),thread_sensitive=False)()
            except self.models.FixtureMarket.DoesNotExist as e:
                print("EXCEPTION AS EEEEEEEE")
                print(f"Match Exception {matchObj.uuid}")
                pass
        # Step 2.2: 3WML Markets:
        mlc = await sync_to_async(lambda:self.models.FixtureMarket.objects.using("default").filter(vhost=self.vhost, fixture=fixture, market_type=self.constants.W3ML, segment=self.constants.FG).count(),thread_sensitive=False)()
        if mlc >= 3:
            try:
                try:
                    homeMLObj = await sync_to_async(lambda:self.models.FixtureMarket.objects.get(vhost=self.vhost, fixture=fixture, market_type=self.constants.W3ML, segment=self.constants.FG, side=self.constants.HOME),thread_sensitive=False)()
                except self.models.FixtureMarket.MultipleObjectsReturned:
                    homeMLObj = await sync_to_async(lambda:self.models.FixtureMarket.objects.filter(vhost=self.vhost, fixture=fixture, market_type=self.constants.W3ML, segment=self.constants.FG, side=self.constants.HOME).first(),thread_sensitive=False)()

                try:
                    awayMLObj = await sync_to_async(lambda:self.models.FixtureMarket.objects.get(vhost=self.vhost, fixture=fixture, market_type=self.constants.W3ML, segment=self.constants.FG, side=self.constants.VISITOR),thread_sensitive=False)()
                except self.models.FixtureMarket.MultipleObjectsReturned:
                    awayMLObj = await sync_to_async(lambda:self.models.FixtureMarket.objects.filter(vhost=self.vhost, fixture=fixture, market_type=self.constants.W3ML, segment=self.constants.FG, side=self.constants.VISITOR).first(),thread_sensitive=False)()

                try:
                    drawMLObj = await sync_to_async(lambda:self.models.FixtureMarket.objects.get(vhost=self.vhost, fixture=fixture, market_type=self.constants.W3ML, segment=self.constants.FG, side=self.constants.DRAW),thread_sensitive=False)()
                except self.models.FixtureMarket.MultipleObjectsReturned:
                    drawMLObj = await sync_to_async(lambda:self.models.FixtureMarket.objects.filter(vhost=self.vhost, fixture=fixture, market_type=self.constants.W3ML, segment=self.constants.FG, side=self.constants.DRAW).first(),thread_sensitive=False)()

                await sync_to_async(lambda:self.sync_match_ml_markets(matchObj, homeMLObj, awayMLObj,drawMLObj),thread_sensitive=False)()
            except self.models.FixtureMarket.DoesNotExist:
                pass
        # Step Three: Outcomes
        has_outcomes = await sync_to_async(lambda:self.models.Outcome.objects.using("default").filter(vhost=self.vhost, fixture=fixture).count(),thread_sensitive=False)()
        if has_outcomes > 0:
            is_finished = await sync_to_async(
                lambda:self.models.Outcome.objects.using("default").filter(vhost=self.vhost, fixture=fixture, is_end_game=True).exists(),thread_sensitive=False
            )()
            if is_finished:
                outcomeObj = await sync_to_async(
                    lambda:self.models.Outcome.objects.using("default").filter(vhost=self.vhost, fixture=fixture, is_end_game=True).first(),thread_sensitive=False
                )()
                # matchObj.finished = True
                await sync_to_async(lambda:matchObj.save(),thread_sensitive=False)()
            else:
                outcomeObj = await sync_to_async(
                    lambda:self.models.Outcome.objects.using("default").filter(vhost=self.vhost, fixture=fixture).order_by('-inserted_on').first()
                ,thread_sensitive=False)()

            if outcomeObj:
                # Fetch participants and segments in parallel
                outcomeSegmentObjs = await sync_to_async(lambda: list(self.models.OutcomeSegmentScore.objects.filter(vhost=self.vhost, outcome=outcomeObj)),thread_sensitive=False)()
                participantObjs = await sync_to_async(lambda: list(self.models.OutcomeParticipants.objects.filter(vhost=self.vhost, outcome=outcomeObj)),thread_sensitive=False)()


                # Build team_sync_map once
                team_sync_map = {}
                participant_uuids = [await sync_to_async(lambda: p.participant.uuid)() for p in participantObjs]
                if participant_uuids:
                    tasks = [
                        asyncio.create_task(
                            self.find_sync_object("team", "kiblio.participant.Participant", puuid)
                        ) for puuid in participant_uuids
                    ]
                    results = await asyncio.gather(*tasks)
                    for puuid, res in zip(participant_uuids, results):
                        if res:
                            team_sync_map[puuid] = res

                # Create/update Outcome object
                await sync_to_async(lambda:self._clear_existing_outcomes(matchObj,outcomeObj),thread_sensitive=False)()
                sys_outObj = await sync_to_async(lambda:self.create_and_update_outcome(matchObj, outcomeObj),thread_sensitive=False)()

                # Update segments and teams concurrently, using team_sync_map
                await asyncio.gather(
                    self.create_and_update_outcome_segments(sys_outObj, outcomeSegmentObjs, team_sync_map),
                    self.create_and_update_outcome_team(sys_outObj, participantObjs, team_sync_map,matchObj)
                )
                if self.verbose:
                    self.logger.info(f"Processed Fixture {fixture.uuid}.")


    async def sync_matches(self, **kwargs):
        """
        Fetch fixtures (batched), cache common DB objects, then process fixtures concurrently.
        Adds batch processing, per-fixture timeouts, and detailed stacktrace dumps
        for tasks that exceed PER_FIXTURE_TIMEOUT.
        """
        # print("SMA")
        # --- Fixture selection ---
        if "provider_match_objs" in kwargs:
            if self.verbose:
                self.logger.info("Syncing Active KIBL.io Fixtures with passed match (fixture) to System Database")
            fixture_objs = kwargs["provider_match_objs"]
        elif "after_time" in kwargs:
            if self.verbose:
                self.logger.info(f"Syncing KIBL.io Fixtures updated after {kwargs['after_time']} to System Database...")
            fixture_objs = await sync_to_async(lambda: list(self.models.Fixture.objects.using("default").filter(vhost=self.vhost, updated_at__gte=kwargs["after_time"])),thread_sensitive=False)()
        else:
            if self.verbose:
                self.logger.info("Synchronising Active KIBL.io Fixtures, Markets and Outcomes to System Database...")
            fixture_objs = await sync_to_async(lambda: list(self.models.Fixture.objects.using("default").filter(vhost=self.vhost)),thread_sensitive=False)()

        total_fixtures = len(fixture_objs)
        self.logger.info(f"Total Matches to Process: {total_fixtures}")
        try:
            await self.run_in_batches(fixture_objs,self.process_fixture,50,"process_fixture")
        except Exception as e:
            self.logger.info(f"Exception during Process Fixture: {e}")



    # -------------------------
    # Sync match markets (sync; used via dbcall when needed)
    # -------------------------
    # 2/3 Way Moneyline:
    def sync_match_ml_markets(self, match, home_side, away_side,draw_side = False):
        """
        Synchronous function that touches ORM; call via dbcall(...) when used.
        """
        margs = {
            "vhost": self.vhost,
            "match": match,
            "driver": "kiblio.fixture.Fixture",
            "home_team": match.home_team,
            "away_team": match.away_team,
            "juice_pct":0
        }
        if draw_side:
            if self.debug:
                self.logger.info(f"Validating 3-Way Line match to have legal odds, 0.99 > rho <= 1.01...")
            if not validate_three_way(home_side.price_american, away_side.price_american,draw_side.price_american):
                if self.debug:
                    self.logger.info(f"Invalid Odds for ML Match {match.uuid}")
                return False
        if self.debug:
            if self.verbose:
                self.logger.info(f"Synchronising Match {match.uuid} ML markets! Match: {match.name}, Home Team: {match.home_team.name}, Away Team: {match.away_team.name}, League: {match.sport.title}")
        _sys_odds_qs = self.models.MatchOddsSummary.objects.using("default").filter(**margs)
        if not _sys_odds_qs.exists():
            zero_sys_odds_obj, created = self.models.MatchOddsSummary.objects.using("default").get_or_create(**margs)
        else:
            zero_sys_odds_obj = _sys_odds_qs.first()
        zero_sys_odds_obj.home_price = home_side.price_american
        zero_sys_odds_obj.home_price_fraction = home_side.price_fraction
        zero_sys_odds_obj.away_price = away_side.price_american
        zero_sys_odds_obj.away_price_fraction = away_side.price_fraction
        if draw_side:
            zero_sys_odds_obj.away_price = draw_side.price_american
            zero_sys_odds_obj.away_price_fraction = draw_side.price_fraction
        zero_sys_odds_obj.save()
        # Juice the odds as they come in: 3% to 7.5%, 0.5% increments.
        try:
            for pct in np.arange(3,8,.5):
                margs["juice_pct"] = Decimal(pct/100)
                try:
                    if not draw_side:
                        hp,ap = self.american_juicer_v2(home_side.price_american,away_side.price_american,margs["juice_pct"])
                        dp = 0
                    else:
                        hp,ap,dp = self.three_way_juicer(home_side.price_american,away_side.price_american,draw_side.price_american,margs["juice_pct"])
                except decimal.DivisionByZero as e:
                    print(f"Division by Zero: {margs['juice_pct']}, HS: {home_side.price_american}, AS: {away_side.price_american}")
                    continue

                _sys_odds_qs = self.models.MatchOddsSummary.objects.using("default").filter(**margs)
                if not _sys_odds_qs.exists():
                    sys_odds_obj, created = self.models.MatchOddsSummary.objects.using("default").get_or_create(**margs)
                else:
                    sys_odds_obj = _sys_odds_qs.first()
                sys_odds_obj.home_price = hp
                sys_odds_obj.home_price_fraction = self.american_to_fraction_str(hp)
                sys_odds_obj.away_price = ap
                sys_odds_obj.away_price_fraction =self.american_to_fraction_str(ap)
                if dp != 0:
                    sys_odds_obj.draw_price = dp
                    sys_odds_obj.draw_price_fraction = self.american_to_fraction_str(dp)

                sys_odds_obj.save()

        except ValueError as e:
            print(f"Failing Object: {match.uuid}")
            raise e
        if self.debug:
            if self.verbose:
                self.logger.info(f"Created/synced ML lines for {match.uuid}! Match: {match.name}, Home Team: {match.home_team.name}, Away Team: {match.away_team.name} Sport: {match.sport.title} ")
        return zero_sys_odds_obj

    async def create_sports_sport(self, group_obj, sports_data):
        try:
            sys_sport_obj, created = await sync_to_async(lambda:
                self.models.Sport.objects.using("default").get_or_create(
                key=sports_data["key"],
                title=sports_data["title"],
                group=group_obj,
                vhost=self.vhost),thread_sensitive=False)()
            # await self._object_setattrs(sys_sport_obj, sports_data, rows=["logo", "sport_mask", "inserted_on", "updated_on"])
            sys_sport_obj.logo = sports_data["logo"]
            sys_sport_obj.sport_mask = sports_data["sport_mask"]
            sys_sport_obj.inserted_on = sports_data["inserted_on"]
            # sys_sport_obj.updated_on = sports_data["updated_on"]
            await sync_to_async(lambda:sys_sport_obj.save(),thread_sensitive=False)()
        except IntegrityError:
            sys_sport_obj = await sync_to_async(lambda:self.models.Sport.objects.using("default").get(key=sports_data["key"], vhost=self.vhost),thread_sensitive=False)()
        finally:
            if self.verbose:
                self.logger.info(f"Sport {sports_data['title']}: Created/Updated in System Database!")
        return sys_sport_obj

    async def create_sports_group(self, group_data):
        sys_group_obj, created = await sync_to_async(lambda:self.models.Group.objects.using("default").get_or_create(slug=group_data["slug"], name=group_data["name"], vhost=self.vhost),thread_sensitive=False)()
        await self._object_setattrs(sys_group_obj, group_data)
        await sync_to_async(lambda:sys_group_obj.save(),thread_sensitive=False)()
        if self.verbose:
            self.logger.info(f"Group {group_data['name']}: Created/Updated in System Database!")
        return sys_group_obj

    async def create_team(self, team_data, sport_obj):
        try:
            sys_team_obj, created = await sync_to_async(lambda:
                self.models.Team.objects.using("default").get_or_create(
                key=team_data["key"],
                name=team_data["name"],
                vhost=self.vhost
            ),thread_sensitive=False)()
        except self.models.Team.MultipleObjectsReturned:
            # Safely get first matching object
            qs = await sync_to_async(lambda:list(self.models.Team.objects.using("default").filter(
                    key=team_data["key"],
                    name=team_data["name"],
                    vhost=self.vhost
                )),thread_sensitive=False
            )()
            sys_team_obj = qs[0] if qs else None
            if sys_team_obj is None:
                raise Exception(f"Could not recover/create Team: {team_data}")

        await self._object_setattrs(sys_team_obj, team_data, rows=["country", "bday", "logo", "mascot", "parent_team", "inserted_on", "updated_on"])

        await sync_to_async(lambda:sys_team_obj.save(),thread_sensitive=False)()
        if self.verbose:
            self.logger.info(f"Team {team_data['name']}: Created/Updated in System Database!")
        ts_obj, created2 = await sync_to_async(lambda:self.models.TeamSport.objects.get_or_create(team=sys_team_obj, sport=sport_obj),thread_sensitive=False)()
        await sync_to_async(lambda:ts_obj.save(),thread_sensitive=False)()
        if created2:
            await sync_to_async(lambda:ts_obj.save(),thread_sensitive=False)()
        return sys_team_obj


    async def create_sports_season(self, season_data):
        sys_season_obj, created = await sync_to_async(lambda:self.models.Season.objects.get_or_create(season_key=season_data["season_key"], name=season_data["name"]),thread_sensitive=False)()
        await self._object_setattrs(sys_season_obj, season_data, rows=["season"])
        await sync_to_async(lambda:sys_season_obj.save(),thread_sensitive=False)()
        if self.verbose:
            self.logger.info(f"Season {season_data.get('title', season_data.get('name'))}: Created/Updated in System Database!")
        return sys_season_obj

    def get_or_create_match(self, vhost, match_data, teams, sport, season):
        """
        Synchronous wrapper (existing logic retained) — called via dbcall by callers.
        """
        try:
            return self.models.Match.objects.get_or_create(
                vhost=vhost,
                id=match_data["id"],
                routing_key=match_data["routing_key"],
                name=match_data["name"],
                home_team=teams["home"],
                away_team=teams["away"],
                sport=sport,
                season=season,
                commence_time=match_data["commence_time"]
            )
        except IntegrityError:
            return self.models.Match.objects.get(vhost=vhost, routing_key=match_data["routing_key"]), False

    async def create_match(self, group_data, sport_data, teams_data, season_data, match_data):
        """
        Safe and optimized async ORM wrapper using dbcall(...) for all ORM operations.
        Uses bulk prefetch for team syncs where possible.
        """
        if self.verbose:
            self.logger.info(f"Creating match: {match_data}.")
            self.logger.info(f"Creating match Data: {match_data}.")
        # GROUP
        groupLink = await self.find_sync_object("group", group_data["object_type"], group_data["object_uuid"])
        if groupLink:
            group = await sync_to_async(lambda: groupLink.group,thread_sensitive=False)()
        else:
            group = await self.create_sports_group(group_data)
            await self.create_sync_object("group", group, group_data["object_type"], group_data["object_uuid"])
        if group:
            if not group.active: return False, False
        # SPORT
        sportLink = await self.find_sync_object("sport", sport_data["object_type"], sport_data["object_uuid"])
        if sportLink:
            sport = await sync_to_async(lambda: sportLink.sport,thread_sensitive=False)()

        else:
            sport = await self.create_sports_sport(group, sport_data)
            await self.create_sync_object("sport", sport, sport_data["object_type"], sport_data["object_uuid"])
        if sport:
            if not sport.active: return False, False
        # TEAMS - batch by driver_object_type to utilize bulk_find_sync_objects
        teams = {}
        for key, tdata in teams_data.items():
            obj_type = tdata["object_type"]
            uuid = tdata["object_uuid"]
            # create team and sync mapping
            team = await self.create_team(tdata, sport)
            sync_obj = await self.create_sync_object("team", team, obj_type, uuid)
            teams[key] = team


        # SEASON
        seasonLink = await self.find_sync_object("season", season_data["object_type"], season_data["object_uuid"])
        if seasonLink:
            season = await sync_to_async(lambda: seasonLink.season,thread_sensitive=False)()
        else:
            season = await self.create_sports_season(season_data)
            await self.create_sync_object("season", season, season_data["object_type"], season_data["object_uuid"])

        # MATCH
        if self.debug:
            if self.verbose:
                self.logger.info(f"Match Teams: {teams}")
        if "home" in teams and "away" in teams:
            sys_MatchObj, created =await sync_to_async(lambda:self.get_or_create_match(self.vhost, match_data, teams, sport, season),thread_sensitive=False)()
            await sync_to_async(lambda:sys_MatchObj.save(),thread_sensitive=False)()
            return sys_MatchObj, created


    async def _sync_loop(self):
        while not self._shutdown_event.is_set():
            wait_seconds = 60
            try:
                # print("Syncing Matches.")
                await self.sync_matches(after_time=self.last_timestamp)
                self.last_timestamp = localtime()
            except Exception:
                self.logger.exception("Error in Sync job")
            self.logger.info(f"Sleeping {wait_seconds:.2f}s until next sync loop")
            try:
                await asyncio.wait_for(
                    self._shutdown_event.wait(),
                    timeout=wait_seconds,
                )
                # shutdown event fired
                self.logger.info("Shutdown event received, exiting Sync loop")
                break

            except asyncio.TimeoutError:
                # timeout == midnight reached
                self.logger.info("Timeout reached, running job!")



    def setup_loop(self):
        """
        Called once before the main loop begins.
        Starts the midnight loop in the background so it doesn't block continuous work.
        """
        loop_fn = type(self)._sync_loop  # ← unbound function
        self._sync_task = asyncio.create_task(loop_fn(self))

        self.logger.info("Sync loop started in background.")


    async def _work_cycle(self):
        # print("KIBLdV2 Tick")
        # self.logger.info("KIBLdV2 Tick .....")
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

        # print("BA'")
        # print("B")
        self.logger.info(f"KIBLdV2 Tick!!")