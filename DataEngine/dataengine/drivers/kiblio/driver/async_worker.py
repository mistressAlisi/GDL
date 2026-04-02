import asyncio
import decimal
import os
import time
from datetime import timedelta
from decimal import Decimal
from types import SimpleNamespace
from typing import List, Dict, Optional

import numpy as np
from asgiref.sync import sync_to_async
from django.db import IntegrityError
from django.utils.text import slugify
from django.utils.timezone import localtime

from asynctools.abc import AsyncWorkerABC

from grader.toolkit.parlays import american_juicer_v2, american_to_fraction_str

class KIBLIOAsyncWorker(AsyncWorkerABC):

    def _child_init(self):
        """
        Runs inside the forked child *after* django.setup().
        Safe place for model imports.
        """
        super()._child_init()
        from dataengine.drivers.kiblio.models import (
            Fixture, Sides, FixtureParticipants, OutcomeParticipants,
            MarketType, Segment, FixtureMarket, Outcome, OutcomeSegmentScore
        )
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

        self.last_timestamp = localtime() - timedelta(days=5)
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

        )

        self.logger.debug("APITennisAsyncDaemon: Django models bound in child")
    # Tuning knobs
    ORM_CONCURRENCY_LIMIT = 20  # number of concurrent synchronous ORM workers
    PER_FIXTURE_SEM_LIMIT = 10   # inner concurrency for per-fixture participant/segment tasks
    BATCH_LOG_EVERY = 500        # log progress every N fixtures
    verbose = False
    # -------------------------
    # ORM wrapper with semaphore
    # -------------------------
    async def dbcall(self, fn, *args, **kwargs):
        """
        Run synchronous ORM call in threadpool, but limit concurrency globally using a semaphore.
        Always uses sync_to_async(thread_sensitive=False).
        """
        if not hasattr(self, "_orm_semaphore") or self._orm_semaphore is None:
            limit = getattr(self, "ORM_CONCURRENCY_LIMIT", 20)
            self._orm_semaphore = asyncio.Semaphore(limit)

        async with self._orm_semaphore:
            return await sync_to_async(lambda: fn(*args, **kwargs), thread_sensitive=False)()

    # -------------------------
    # Run-level sync cache helpers
    # -------------------------
    def _cache_key(self, sync_type: str, driver_uuid: str):
        return f"{sync_type}:{driver_uuid}"

    def _init_run_cache(self):
        # call at start of sync_matches
        self._sync_cache: Dict[str, object] = {}

    def _cache_get(self, sync_type: str, driver_uuid: str):
        return self._sync_cache.get(self._cache_key(sync_type, driver_uuid))

    def _cache_set(self, sync_type: str, driver_uuid: str, obj):
        self._sync_cache[self._cache_key(sync_type, driver_uuid)] = obj

    # -------------------------
    # Basic helpers (ORM via dbcall)
    # -------------------------
    async def get_participant(self, fixture, side_obj):
        """Return the first FixtureParticipants for a fixture and side, or None."""
        return await sync_to_async(
            lambda: self.models.FixtureParticipants.objects.filter(
                vhost=self.vhost,
                fixture=fixture,
                side=side_obj
            ).first(),thread_sensitive=False)()
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
                        self.logger.info(f"Unable to find Participant match for {matchObj.uuid}, Participant: {puuid}")
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
                    sys_team_obj, created = await self.dbcall(self.models.Sys_OutcomeTeams.objects.get_or_create, **ckargs)
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
                await self.dbcall(outcome.save)
                await self.dbcall(sys_team_obj.save)
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
                team = await self.dbcall(lambda: team_sync.team)
                s_name = await self.dbcall(lambda:s.segment.name)
                try:
                    sys_outcome_obj, created = await self.dbcall(
                        self.models.Sys_OutcomeSegmentScore.objects.get_or_create,
                        vhost=self.vhost,
                        outcome=outcome,
                        team=team,
                        driver="kiblio.fixture.Fixture",
                        segment=s_name
                    )
                except self.models.Sys_OutcomeSegmentScore.MultipleObjectsReturned:
                    sys_outcome_obj = await sync_to_async(lambda:self.models.Sys_OutcomeSegmentScore.objects.filter(
                        vhost=self.vhost,
                        outcome=outcome,
                        team=team,
                        driver="kiblio.fixture.Fixture",
                        segment=s_name).first(),thread_sensitive=False)()

                sys_outcome_obj.score = s.score
                sys_outcome_obj.is_winner = s.is_winner
                await self.dbcall(sys_outcome_obj.save)
                return sys_outcome_obj

        tasks = [asyncio.create_task(_process_segment(s, participant)) for s, participant in segments_with_participants]
        if tasks:
            done = await asyncio.gather(*tasks,return_exceptions=True)
            results = [r for r in done if r is not None]
        return results


    async def mark_notcurr_previous_outcomes(self,match):
        _ss = self.models.Sys_Outcome.objects.filter(
            vhost=self.vhost,
            match=match,
            driver="kiblio.fixture.Fixture")
        ss = await sync_to_async(lambda:list(_ss),thread_sensitive=False)()


        async def _process_entry(obj):
            obj.is_current = False
            await sync_to_async(lambda:obj.save(),thread_sensitive=False)()

        # tasks = [asyncio.create_task(_process_entry(s)) for s in ss]
        for s in ss:
            await _process_entry(s)
        # if tasks:
        #     done = await asyncio.await(*tasks)
        return True



    def _clear_existing_outcomes(self,match,outcome_obj):
        sys_out_objs = self.models.Sys_Outcome.objects.filter(
            vhost=self.vhost,
            match=match,
            driver="kiblio.fixture.Fixture",
            outcome_id=outcome_obj.outcome_id,
            routing_key=outcome_obj.routing_key,
        )
        for sys_out_obj in sys_out_objs:
            sys_out_obj.is_current = False
            sys_out_obj.save()


    # -------------------------
    # Outcome object creation/update (synchronous; called via dbcall where needed)
    # -------------------------
    def create_and_update_outcome(self, match, outcome_obj):
        """
        Synchronous by design, used via dbcall where necessary.
        """
        self._clear_existing_outcomes(match, outcome_obj)
        try:
            sys_out_obj, created = self.models.Sys_Outcome.objects.get_or_create(
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
            sys_out_obj = self.models.Sys_Outcome.objects.filter(
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
    # Sports / teams / match creation (ORM via dbcall)
    # -------------------------
    async def create_sports_group(self, group_data):
        sys_group_obj, created = await self.dbcall(self.models.Group.objects.get_or_create, slug=group_data["slug"], name=group_data["name"], vhost=self.vhost)
        await self._object_setattrs(sys_group_obj, group_data)
        await self.dbcall(sys_group_obj.save)
        if self.verbose:
            self.logger.info(f"Group {group_data['name']}: Created/Updated in System Database!")
        return sys_group_obj

    async def create_sports_season(self, season_data):
        sys_season_obj, created = await self.dbcall(self.models.Season.objects.get_or_create, season_key=season_data["season_key"], name=season_data["name"])
        await self._object_setattrs(sys_season_obj, season_data, rows=["season"])
        await self.dbcall(sys_season_obj.save)
        if self.verbose:
            self.logger.info(f"Season {season_data.get('title', season_data.get('name'))}: Created/Updated in System Database!")
        return sys_season_obj

    async def create_sports_sport(self, group_obj, sports_data):
        try:
            sys_sport_obj, created = await self.dbcall(
                self.models.Sport.objects.get_or_create,
                key=sports_data["key"],
                title=sports_data["title"],
                group=group_obj,
                vhost=self.vhost
            )
            # await self._object_setattrs(sys_sport_obj, sports_data, rows=["logo", "sport_mask", "inserted_on", "updated_on"])
            sys_sport_obj.logo = sports_data["logo"]
            sys_sport_obj.sport_mask = sports_data["sport_mask"]
            sys_sport_obj.inserted_on = sports_data["inserted_on"]
            # sys_sport_obj.updated_on = sports_data["updated_on"]
            await self.dbcall(sys_sport_obj.save)
        except IntegrityError:
            sys_sport_obj = await self.dbcall(self.models.Sport.objects.get, key=sports_data["key"], vhost=self.vhost)
        finally:
            if self.verbose:
                self.logger.info(f"Sport {sports_data['title']}: Created/Updated in System Database!")
        return sys_sport_obj

    async def create_team(self, team_data, sport_obj):
        try:
            sys_team_obj, created = await self.dbcall(
                self.models.Team.objects.get_or_create,
                key=team_data["key"],
                name=team_data["name"],
                vhost=self.vhost
            )
        except self.models.Team.MultipleObjectsReturned:
            # Safely get first matching object
            qs = await self.dbcall(
                lambda: list(self.models.Team.objects.filter(
                    key=team_data["key"],
                    name=team_data["name"],
                    vhost=self.vhost
                ))
            )
            sys_team_obj = qs[0] if qs else None
            if sys_team_obj is None:
                raise Exception(f"Could not recover/create Team: {team_data}")

        await self._object_setattrs(sys_team_obj, team_data, rows=["country", "bday", "logo", "mascot", "parent_team", "inserted_on", "updated_on"])
        await self.dbcall(sys_team_obj.save)
        if self.verbose:
            self.logger.info(f"Team {team_data['name']}: Created/Updated in System Database!")
        ts_obj, created2 = await self.dbcall(self.models.TeamSport.objects.get_or_create, team=sys_team_obj, sport=sport_obj)
        await self.dbcall(ts_obj.save)
        if created2:
            await self.dbcall(ts_obj.save)
        return sys_team_obj

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
        _sys_odds_qs = self.models.MatchOddsSummary.objects.filter(**margs)
        if not _sys_odds_qs.exists():
            zero_sys_odds_obj, created = self.models.MatchOddsSummary.objects.get_or_create(**margs)
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
                    hp,ap = american_juicer_v2(home_side.price_american,away_side.price_american,margs["juice_pct"])
                except decimal.DivisionByZero as e:
                    print(f"Division by Zero: {margs['juice_pct']}, HS: {home_side.price_american}, AS: {away_side.price_american}")
                    raise e
                _sys_odds_qs = self.models.MatchOddsSummary.objects.filter(**margs)
                if not _sys_odds_qs.exists():
                    sys_odds_obj, created = self.models.MatchOddsSummary.objects.get_or_create(**margs)
                else:
                    sys_odds_obj = _sys_odds_qs.first()
                sys_odds_obj.home_price = hp
                sys_odds_obj.home_price_fraction = american_to_fraction_str(hp)
                sys_odds_obj.away_price = ap
                sys_odds_obj.away_price_fraction =american_to_fraction_str(ap)

                sys_odds_obj.save()
        except ValueError as e:
            print(f"Failing Object: {match.uuid}")
            raise e
        return zero_sys_odds_obj

    # -------------------------
    # Match creation helper (synchronous; called through dbcall)
    # -------------------------
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
                home_team=teams["home"][0],
                away_team=teams["away"][0],
                sport=sport,
                season=season,
                commence_time=match_data["commence_time"]
            )
        except IntegrityError:
            return self.models.Match.objects.get(vhost=vhost, routing_key=match_data["routing_key"]), False

    # -------------------------
    # Fixture formatting (pure-Python; no ORM)
    # -------------------------
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

    # -------------------------
    # Main per-fixture processing (optimized)
    # -------------------------
    async def process_fixture(self, fixture, hside, aside, ml_type=None, seg=None):
        """
        Process a single fixture:
         - find participants
         - create/update match (via find_sync_object or create_match)
         - sync ML markets
         - sync outcomes & outcome details (segments + teams) concurrently
        """
        t0_fixture = time.perf_counter()

        # Participants (parallel)
        hTeObj, aTeObj = await asyncio.gather(
            self.get_participant(fixture, hside),
            self.get_participant(fixture, aside)
        )

        if not (hTeObj and aTeObj):
            return

        # Step One: find or create match link
        sys_linkObj = await self.find_sync_object("match", f"kiblio.fixture.Fixture", fixture.uuid)
        if not sys_linkObj:
            # prepare args using fixture_format_sync via dbcall (pure-Python but wrap for thread-safety with related attributes)
            self.logger.info(f"Fixture is not linked: {fixture.uuid}")
            qmargs = await self.dbcall(self.fixture_format_sync, fixture, hTeObj, aTeObj)
            matchObj, sys_linkObj = await self.create_match(**qmargs)
            if not matchObj:
                if self.verbose:
                    self.logger.info(f"Fixture SKIPPED: {fixture.uuid}->Sport or Group is disabled.")
                return t0_fixture - time.perf_counter()
            match_uuid = await sync_to_async(lambda:matchObj.uuid,thread_sensitive=False)()
            sys_link = await self.create_sync_object("match", matchObj,"kiblio.fixture.Fixture" , fixture.uuid)
            sys_link.match = matchObj
            await sync_to_async(lambda: sys_link.save(), thread_sensitive=False)()
            if self.verbose:
                self.logger.info(f"Fixture Linked: {fixture.uuid}->{match_uuid}")
        else:
            # Do not Sync Status
            matchObj = await self.dbcall(lambda: sys_linkObj.match)
            match_data = await self.dbcall(self.fixture_format_match_sync, fixture)
            if not matchObj.manual_data:
                await self._object_setattrs(matchObj, match_data, rows=["status_short", "status_long", "commence_time"])
                await self.dbcall(matchObj.save)
                if self.verbose:
                    self.logger.info(f"Fixture {fixture.uuid} updated")

            else:
                self.logger.info(f"Fixture {fixture.uuid} is linked to Match {matchObj.uuid} which has manual data - ignoring.")
                await self.dbcall(matchObj.save)

        # Step 2.1: ML Markets
        mlMrObj = ml_type if ml_type is not None else await self.dbcall(self.models.MarketType.objects.get, abrv="2WML", vhost=self.vhost)
        segObj = seg if seg is not None else await self.dbcall(self.models.Segment.objects.get, abrv="FG", vhost=self.vhost)
        hSideObj = await self.dbcall(self.models.Sides.objects.get, abrv="HOME", vhost=self.vhost)
        aSideObj = await self.dbcall(self.models.Sides.objects.get, abrv="VISITOR", vhost=self.vhost)

        mlc = await self.dbcall(self.models.FixtureMarket.objects.filter(vhost=self.vhost, fixture=fixture, market_type=mlMrObj, segment=segObj).count)
        if mlc == 2:
            try:
                try:
                    homeMLObj = await self.dbcall(self.models.FixtureMarket.objects.get, vhost=self.vhost, fixture=fixture, market_type=mlMrObj, segment=segObj, side=hSideObj)
                except self.models.FixtureMarket.MultipleObjectsReturned:
                    homeMLObj = await self.dbcall(self.models.FixtureMarket.objects.filter(vhost=self.vhost, fixture=fixture, market_type=mlMrObj, segment=segObj, side=hSideObj).first)

                try:
                    awayMLObj = await self.dbcall(self.models.FixtureMarket.objects.get, vhost=self.vhost, fixture=fixture, market_type=mlMrObj, segment=segObj, side=aSideObj)
                except self.models.FixtureMarket.MultipleObjectsReturned:
                    awayMLObj = await self.dbcall(self.models.FixtureMarket.objects.filter(vhost=self.vhost, fixture=fixture, market_type=mlMrObj, segment=segObj, side=aSideObj).first)

                await self.dbcall(self.sync_match_ml_markets, matchObj, homeMLObj, awayMLObj)
            except self.models.FixtureMarket.DoesNotExist:
                pass
        # Step 2.2: 3WML Markets:
        m3lMrObj = ml_type if ml_type is not None else await self.dbcall(self.models.MarketType.objects.get, abrv="3WML", vhost=self.vhost)
        dSideObj = await self.dbcall(self.models.Sides.objects.get, abrv="DRAW", vhost=self.vhost)
        mlc = await self.dbcall(self.models.FixtureMarket.objects.filter(vhost=self.vhost, fixture=fixture, market_type=m3lMrObj, segment=segObj).count)
        # if mlc == 3:
        #     try:
        #         try:
        #             homeMLObj = await self.dbcall(FixtureMarket.objects.get, vhost=self.vhost, fixture=fixture, market_type=mlMrObj, segment=segObj, side=hSideObj)
        #         except FixtureMarket.MultipleObjectsReturned:
        #             homeMLObj = await self.dbcall(FixtureMarket.objects.filter(vhost=self.vhost, fixture=fixture, market_type=mlMrObj, segment=segObj, side=hSideObj).first)
        #
        #         try:
        #             awayMLObj = await self.dbcall(FixtureMarket.objects.get, vhost=self.vhost, fixture=fixture, market_type=mlMrObj, segment=segObj, side=aSideObj)
        #         except FixtureMarket.MultipleObjectsReturned:
        #             awayMLObj = await self.dbcall(FixtureMarket.objects.filter(vhost=self.vhost, fixture=fixture, market_type=mlMrObj, segment=segObj, side=aSideObj).first)
        #
        #         try:
        #             drawMLObj = await self.dbcall(FixtureMarket.objects.get, vhost=self.vhost, fixture=fixture, market_type=mlMrObj, segment=segObj, side=dSideObj)
        #         except FixtureMarket.MultipleObjectsReturned:
        #             drawMLObj = await self.dbcall(FixtureMarket.objects.filter(vhost=self.vhost, fixture=fixture, market_type=mlMrObj, segment=segObj, side=dSideObj).first)
        #
        #         await self.dbcall(self.sync_match_ml_markets, matchObj, homeMLObj, awayMLObj,drawMLObj)
        #     except FixtureMarket.DoesNotExist:
        #         pass
        # Step Three: Outcomes
        has_outcomes = await self.dbcall(self.models.Outcome.objects.filter(vhost=self.vhost, fixture=fixture).count)
        if has_outcomes > 0:
            is_finished = await self.dbcall(
                self.models.Outcome.objects.filter(vhost=self.vhost, fixture=fixture, is_end_game=True).exists
            )
            if is_finished:
                outcomeObj = await self.dbcall(
                    self.models.Outcome.objects.filter(vhost=self.vhost, fixture=fixture, is_end_game=True).first
                )
                # matchObj.finished = True
                await self.dbcall(matchObj.save)
            else:
                outcomeObj = await self.dbcall(
                    self.models.Outcome.objects.filter(vhost=self.vhost, fixture=fixture).order_by('-inserted_on').first
                )

            if outcomeObj:
                # Fetch participants and segments in parallel
                outcomeSegmentObjs, participantObjs = await asyncio.gather(
                    self.dbcall(lambda: list(self.models.OutcomeSegmentScore.objects.filter(vhost=self.vhost, outcome=outcomeObj))),
                    self.dbcall(lambda: list(self.models.OutcomeParticipants.objects.filter(vhost=self.vhost, outcome=outcomeObj)))
                )

                # Build team_sync_map once
                team_sync_map = {}
                participant_uuids = [await self.dbcall(lambda: p.participant.uuid) for p in participantObjs]
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
                await self.mark_notcurr_previous_outcomes(matchObj)
                sys_outObj = await self.dbcall(self.create_and_update_outcome, matchObj, outcomeObj)

                # Update segments and teams concurrently, using team_sync_map
                await asyncio.gather(
                    self.create_and_update_outcome_segments(sys_outObj, outcomeSegmentObjs, team_sync_map),
                    self.create_and_update_outcome_team(sys_outObj, participantObjs, team_sync_map,matchObj)
                )

        # done fixture
        t1_fixture = time.perf_counter()
        # return elapsed for the caller to aggregate if needed
        return t1_fixture - t0_fixture

    # -------------------------
    # High-level orchestration
    # -------------------------
    async def create_match(self, group_data, sport_data, teams_data, season_data, match_data):
        """
        Safe and optimized async ORM wrapper using dbcall(...) for all ORM operations.
        Uses bulk prefetch for team syncs where possible.
        """
        self.logger.info(f"Creating match: {match_data}.")
        print(f"Creating match: {match_data}.")
        # GROUP
        groupLink = await self.find_sync_object("group", group_data["object_type"], group_data["object_uuid"])
        if groupLink:
            group = await self.dbcall(lambda: groupLink.group)
        else:
            group = await self.create_sports_group(group_data)
            await self.create_sync_object("group", group, group_data["object_type"], group_data["object_uuid"])
        if group:
            if not group.active: return False, False
        # SPORT
        sportLink = await self.find_sync_object("sport", sport_data["object_type"], sport_data["object_uuid"])
        if sportLink:
            sport = await self.dbcall(lambda: sportLink.sport)

        else:
            sport = await self.create_sports_sport(group, sport_data)
            await self.create_sync_object("sport", sport, sport_data["object_type"], sport_data["object_uuid"])
        if sport:
            if not sport.active: return False, False
        # TEAMS - batch by driver_object_type to utilize bulk_find_sync_objects
        teams = {}
        uuids_by_type: Dict[str, List[str]] = {}
        for key, tdata in teams_data.items():
            obj_type = tdata["object_type"]
            uuids_by_type.setdefault(obj_type, []).append(tdata["object_uuid"])

        # perform bulk finds for each object_type
        bulk_results_by_type: Dict[str, Dict[str, object]] = {}
        for obj_type, uuids in uuids_by_type.items():
            try:
                bulk_results_by_type[obj_type] = await self.bulk_find_sync_objects("team", obj_type, uuids)
            except Exception:
                bulk_results_by_type[obj_type] = {}

        # now resolve each team
        for key, tdata in teams_data.items():
            obj_type = tdata["object_type"]
            uuid = tdata["object_uuid"]
            found = bulk_results_by_type.get(obj_type, {}).get(uuid)
            if found:
                team = await self.dbcall(lambda: found.team)
                teams[key] = [team, found]
                self._cache_set("team", uuid, found)
            else:
                # create team and sync mapping
                team = await self.create_team(tdata, sport)
                sync_obj = await self.create_sync_object("team", team, obj_type, uuid)
                teams[key] = [team, sync_obj]
                self._cache_set("team", uuid, sync_obj)

        # SEASON
        seasonLink = await self.find_sync_object("season", season_data["object_type"], season_data["object_uuid"])
        if seasonLink:
            season = await self.dbcall(lambda: seasonLink.season)
        else:
            season = await self.create_sports_season(season_data)
            await self.create_sync_object("season", season, season_data["object_type"], season_data["object_uuid"])

        # MATCH
        sys_MatchObj, created = await self.dbcall(self.get_or_create_match, self.vhost, match_data, teams, sport, season)
        await self.dbcall(sys_MatchObj.save)
        return sys_MatchObj, created

    async def sync_matches(self, **kwargs):
        """
        Fetch fixtures (batched), cache common DB objects, then process fixtures concurrently.
        Adds batch processing, per-fixture timeouts, and detailed stacktrace dumps
        for tasks that exceed PER_FIXTURE_TIMEOUT.
        """
        self._init_run_cache()

        t_start_run = time.perf_counter()

        # --- Fixture selection ---
        if "provider_match_objs" in kwargs:
            if self.verbose:
                self.logger.info("Syncing Active KIBL.io Fixtures with passed match (fixture) to System Database")
            fixture_objs = kwargs["provider_match_objs"]
        elif "after_time" in kwargs:
            if self.verbose:
                self.logger.info(f"Syncing KIBL.io Fixtures updated after {kwargs['after_time']} to System Database...")
            fixture_objs = await self.dbcall(
                lambda: list(self.models.Fixture.objects.filter(vhost=self.vhost, updated_at__gte=kwargs["after_time"]))
            )
        else:
            if self.verbose:
                self.logger.info("Synchronising Active KIBL.io Fixtures, Markets and Outcomes to System Database...")
            fixture_objs = await self.dbcall(lambda: list(self.models.Fixture.objects.filter(vhost=self.vhost)))

        total_fixtures = len(fixture_objs)
        self.logger.info(f"Total Matches to Process: {total_fixtures}")

        # --- Cache shared DB objects ---
        ml_type_task = asyncio.create_task(self.dbcall(self.models.MarketType.objects.get, abrv="2WML", vhost=self.vhost))
        seg_task = asyncio.create_task(self.dbcall(self.models.Segment.objects.get, abrv="FG", vhost=self.vhost))
        h_side_task = asyncio.create_task(self.dbcall(self.models.Sides.objects.get, abrv="HOME", vhost=self.vhost))
        a_side_task = asyncio.create_task(self.dbcall(self.models.Sides.objects.get, abrv="VISITOR", vhost=self.vhost))

        ml_type = await ml_type_task
        seg_obj = await seg_task
        h_side_obj = await h_side_task
        a_side_obj = await a_side_task

        # --- Execution parameters ---
        max_workers = min(self.max_workers, max(4, (os.cpu_count() or 2) * 5))
        BATCH_SIZE = getattr(self, "BATCH_SIZE", 1000)
        PER_FIXTURE_TIMEOUT = getattr(self, "PER_FIXTURE_TIMEOUT", 30.0)

        processed = 0
        processed_start_time = time.perf_counter()

        # --- Helper for stacktrace capture ---
        async def dump_asyncio_stacktrace(reason="Timeout"):
            """
            Log a traceback of all currently running asyncio tasks.
            """
            import traceback

            self.logger.warning(f"=== Asyncio stack dump triggered ({reason}) ===")
            all_tasks = asyncio.all_tasks()
            current = asyncio.current_task()

            for t in all_tasks:
                if t is current:
                    continue
                self.logger.warning(f"\n--- Task {t.get_name()} ({id(t)}) ---")
                self.logger.warning(f"Status: {'done' if t.done() else 'running'}, cancelled={t.cancelled()}")

                # Print exception if task is done with exception
                if t.done() and not t.cancelled():
                    exc = t.exception()
                    if exc:
                        self.logger.warning(f"Task raised exception: {exc}")
                        tb_lines = traceback.format_exception(type(exc), exc, exc.__traceback__)
                        for l in "".join(tb_lines).rstrip().splitlines():
                            self.logger.warning(f"    {l}")

                # Print stack for running or pending tasks
                stack = t.get_stack()
                if not stack:
                    self.logger.warning("    (no stack available)")
                    continue
                for frame in stack:
                    for line in traceback.format_stack(frame):
                        for l in line.rstrip().splitlines():
                            self.logger.warning(f"    {l}")

            self.logger.warning("=== End of asyncio stack dump ===")

        # --- Process fixtures in batches ---
        for batch_start in range(0, total_fixtures, BATCH_SIZE):
            batch = fixture_objs[batch_start: batch_start + BATCH_SIZE]
            if not batch:
                break

            self.logger.info(f"Processing batch {batch_start // BATCH_SIZE + 1} "
                             f"- fixtures {batch_start + 1}..{batch_start + len(batch)}")

            semaphore = asyncio.Semaphore(max_workers)

            async def run_one(idx_in_batch, fixture):
                nonlocal processed
                async with semaphore:
                    try:
                        elapsed = await asyncio.wait_for(
                            self.process_fixture(
                                fixture, h_side_obj, a_side_obj,
                                ml_type=ml_type, seg=seg_obj
                            ),
                            timeout=PER_FIXTURE_TIMEOUT
                        )
                        processed += 1
                        return ("ok", fixture, elapsed)
                    except asyncio.TimeoutError:
                        # Timeout hit: dump stack traces
                        try:
                            self.logger.warning(
                                f"Fixture timeout ({PER_FIXTURE_TIMEOUT}s): "
                                f"uuid={getattr(fixture, 'uuid', None)}, "
                                f"id={getattr(fixture, 'fixture_id', None)}"
                            )
                            await dump_asyncio_stacktrace("Fixture Timeout")
                        except Exception as ex_dump:
                            self.logger.error(f"Error dumping stacktrace: {ex_dump}")
                        return ("timeout", fixture, None)
                    except Exception as e:
                        fid = getattr(fixture, "uuid", None)
                        self.logger.exception(f"Error processing fixture {fid}: {e}")
                        return ("error", fixture, e)

            tasks = [asyncio.create_task(run_one(i, f)) for i, f in enumerate(batch)]
            if not tasks:
                continue

            results = await asyncio.gather(*tasks, return_exceptions=True)

            # --- Progress logging ---
            if processed % self.BATCH_LOG_EVERY == 0 or processed == total_fixtures:
                elapsed_batch = time.perf_counter() - processed_start_time
                avg = elapsed_batch / processed if processed else 0.0
                self.logger.info(f"Progress: {processed}/{total_fixtures} fixtures processed — "
                                 f"elapsed {elapsed_batch:.2f}s, avg {avg:.3f}s/fixture")

            await asyncio.sleep(0)

        total_elapsed = time.perf_counter() - t_start_run
        avg_total = total_elapsed / total_fixtures if total_fixtures else 0.0
        self.logger.info(f"Sync cycle completed: {total_fixtures} fixtures in {total_elapsed:.2f}s "
                         f"(avg {avg_total:.3f}s/fixture)")

    async def _work_cycle(self):
        if not self.last_timestamp:
            await self.sync_matches()
        else:
            await self.sync_matches(after_time=self.last_timestamp)
        self.last_timestamp = localtime()
        self.logger.info(f"KIBLd worker tick.")
