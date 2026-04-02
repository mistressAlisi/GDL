import json
import re
import unicodedata

from asgiref.sync import sync_to_async
from django.forms import model_to_dict
from zope.interface.declarations import ObjectSpecification

from dataengine.drivers.kiblio.api.constants import KIBL_MARKET_UPDATE_FIELDS

from dataengine.drivers.kiblio.models import Participant, Sides, MarketType, Segment, BetType, MarketStatus, \
    FixtureMarket, League, Season, Location, FixtureType, Fixture, FixtureParticipants, Outcome, OutcomeSegmentScore, \
    OutcomeParticipants, State


async def object_setattrs(obj, entry, **kwargs):
    keys = model_to_dict(obj, entry.keys()).keys()
    # print(keys)
    for k in keys:
        # print(k)
        if "rows" in kwargs:
            if hasattr(obj, k) and k in kwargs["rows"]:
                setattr(obj, k, entry[k])
        elif hasattr(obj, k):
            setattr(obj, k, entry[k])
    await sync_to_async(lambda:obj.save(),thread_sensitive=False)()


async def aprocess_fixture_data(entry, vhost,logger=False,spam=False):
    league = await sync_to_async(lambda:League.objects.get(league_id=entry["league_id"],vhost=vhost),thread_sensitive=False)()
    season = await sync_to_async(lambda:Season.objects.get(season_id=entry["season_id"],vhost=vhost),thread_sensitive=False)()
    location = await sync_to_async(lambda:Location.objects.get(location_id=entry["location_id"],vhost=vhost),thread_sensitive=False)()
    fixture_type = await sync_to_async(lambda:FixtureType.objects.get(fixture_type_id=entry["fixture_type_id"],vhost=vhost),thread_sensitive=False)()
    # try:
    #     fixtureObj = Fixture.objects.get(vhost=vhost, routing_key=entry["routing_key"])
    # except Fixture.DoesNotExist:
    try:
        fixtureObj = await sync_to_async(lambda:Fixture.objects.get(fixture_id=entry["fixture_id"],vhost=vhost),thread_sensitive=False)()
    except Fixture.DoesNotExist:
        fixtureObj, fcc = await sync_to_async(lambda:Fixture.objects.get_or_create(vhost=vhost, league=league, season=season, location=location,
                                                        fixture_type=fixture_type, fixture_id=entry["fixture_id"],
                                                        parent_fixture_id=entry["parent_fixture_id"],
                                                        routing_key=entry["routing_key"]),thread_sensitive=False)()
        if fcc:
            await sync_to_async(lambda:fixtureObj.save(),thread_sensitive=False)()

    await object_setattrs(fixtureObj, entry)
    # print(entry["participants"])
    # print("*****")

    league_name = unicodedata.normalize("NFKD", league.name or "").casefold()
    league_sport = await sync_to_async(lambda:league.sport.abrv.casefold(),thread_sensitive=False)()
    if re.search(r"\bwomen('?s)?\b", league_name) and league_sport != "tn":
        morphed = True
    else:
        morphed = False
    for p in entry["participants"]:
        # Women Leagues special handling:
        if morphed:
            team_name = f"{p["name"]} W "
            if logger:
                logger.info(f"Team name Morphed for Women's sport: {team_name}")
        else:
            team_name = p["name"]
        del(p["name"])
        p["morphed"] = morphed
        # print("Going to create...")
        try:
            participantObj, c = await sync_to_async(lambda:Participant.objects.get_or_create(vhost=vhost, participant_id=p["participant_id"],name=team_name,
                                                                  league=league,), thread_sensitive=False)()
            # print("Successfully created participant")
            if c:
                await object_setattrs(participantObj, p)
            if c or morphed:
                await sync_to_async(lambda:participantObj.save(),thread_sensitive=False)()
        except Participant.MultipleObjectsReturned:
            participantObj = await sync_to_async(
                lambda: Participant.objects.filter(vhost=vhost, participant_id=p["participant_id"],name=team_name,
                                                          league=league).first(), thread_sensitive=False)()
        # print(f"Participant Object created: {participantObj.uuid} with name {team_name}")
        try:
            sideObj = await sync_to_async(lambda:Sides.objects.get(side_id=p["side_id"], vhost=vhost), thread_sensitive=False)()
        except Sides.MultipleObjectsReturned:
            sideObj = await sync_to_async(lambda: Sides.objects.filter(side_id=p["side_id"], vhost=vhost).first(),
                                          thread_sensitive=False)()
        try:
            fpObj,_ = await sync_to_async(lambda:FixtureParticipants.objects.get_or_create(vhost=vhost, fixture=fixtureObj, participant=participantObj,side=sideObj, fixture_participant_id=p["fixture_participant_id"]),thread_sensitive=False)()
        except FixtureParticipants.MultipleObjectsReturned:
            fpObj = await sync_to_async(
                lambda: FixtureParticipants.objects.filter(vhost=vhost, fixture=fixtureObj,
                                                                  participant=participantObj, side=sideObj,
                                                                  fixture_participant_id=p["fixture_participant_id"]).first(),
                thread_sensitive=False)()
        if spam:
            if logger:
                logger.info(f"Team P Objects: {p}")
        await  object_setattrs(fpObj, p)
        # print(fpObj)
    # print("*****")
    if morphed:
        fixtureObj.teams_morphed = True
        await sync_to_async(lambda:fixtureObj.save(),thread_sensitive=False)()
    return fixtureObj


async def aprocess_fixture_outcomes_data(entry, vhost, **kwargs):
    segments = []
    participants = []
    segObj = await sync_to_async(lambda:Segment.objects.get(segment_id=entry["segment_id"], vhost=vhost),thread_sensitive=False)()
    try:
        fixture = await sync_to_async(lambda:Fixture.objects.get(fixture_id=entry["fixture_id"], vhost=vhost),thread_sensitive=False)()
    except Fixture.DoesNotExist:
        return False, False, False
    try:
        outcomeObj = await sync_to_async(lambda:Outcome.objects.get(routing_key=entry["routing_key"], vhost=vhost,fixture=fixture,outcome_id=entry["outcome_id"],segment=segObj),thread_sensitive=False)()
        # outcomeObj.segment = segObj
        await sync_to_async(lambda:outcomeObj.save(),thread_sensitive=False)()
    except Outcome.DoesNotExist:
        outcomeObj,_ = await sync_to_async(lambda:Outcome.objects.get_or_create(fixture=fixture, outcome_id=entry["outcome_id"], segment=segObj, vhost=vhost),thread_sensitive=False)()
    except Outcome.MultipleObjectsReturned:
        outcomeObj = await sync_to_async(
            lambda: Outcome.objects.filter(routing_key=entry["routing_key"], vhost=vhost, fixture=fixture,
                                        outcome_id=entry["outcome_id"], segment=segObj).first(), thread_sensitive=False)()
    await object_setattrs(outcomeObj, entry)
    await sync_to_async(lambda:outcomeObj.save(),thread_sensitive=False)()

    for ssc in entry["outcomes_segments_scores"]:
        # print(json.dumps(ssc))
        osegObj = await sync_to_async(lambda:Segment.objects.get(segment_id=ssc["segment_id"], vhost=vhost),thread_sensitive=False)()
        try:
            oPObj = await sync_to_async(lambda:FixtureParticipants.objects.get(fixture_participant_id=ssc["fixture_participant_id"],
                                                    vhost=vhost,participant__morphed=fixture.teams_morphed),thread_sensitive=False)()
        except FixtureParticipants.DoesNotExist:
            return False, False, False
        except FixtureParticipants.MultipleObjectsReturned:
            oPObj = await sync_to_async(
                lambda: FixtureParticipants.objects.filter(fixture_participant_id=ssc["fixture_participant_id"],
                                                        vhost=vhost,participant__morphed=fixture.teams_morphed).first(), thread_sensitive=False)()
        try:
            ossObj = await sync_to_async(lambda:OutcomeSegmentScore.objects.get(routing_key=ssc["routing_key"],segment=osegObj, vhost=vhost),thread_sensitive=False)()
            # ossObj.segment = osegObj
            await sync_to_async(lambda:ossObj.save(),thread_sensitive=False)()
        except OutcomeSegmentScore.DoesNotExist:
            ossObj, ossCC = await sync_to_async(lambda:OutcomeSegmentScore.objects.get_or_create(outcome=outcomeObj, segment=osegObj,
                                                                      participant=oPObj.participant,
                                                                      vhost=vhost), thread_sensitive=False)()
        except OutcomeSegmentScore.MultipleObjectsReturned:
            ossObj = await sync_to_async(
                lambda: OutcomeSegmentScore.objects.filter(routing_key=ssc["routing_key"], segment=osegObj, vhost=vhost).first(),
                thread_sensitive=False)()
            # print("I'm creating a new OSS...")

        await object_setattrs(ossObj, ssc)
        await sync_to_async(lambda:ossObj.save(),thread_sensitive=False)()
        segments.append(ossObj)
    # print("-----")
    for ssp in entry["outcomes_participants"]:
        oPObj = False
        # print(json.dumps(ssp,indent=4))
        # oPObj = FixtureParticipants.objects.get(fixture_participant_id=ssc["fixture_participant_id"],vhost=vhost)
        try:
            oPObj = await sync_to_async(lambda:FixtureParticipants.objects.get(fixture_participant_id=ssp["fixture_participant_id"],
                                                    vhost=vhost,participant__morphed=fixture.teams_morphed),thread_sensitive=False)()
        except FixtureParticipants.DoesNotExist:
            return False
        except FixtureParticipants.MultipleObjectsReturned:
            oPObj = await sync_to_async(
                lambda: FixtureParticipants.objects.filter(fixture_participant_id=ssp["fixture_participant_id"],
                                                        vhost=vhost,participant__morphed=fixture.teams_morphed).first(), thread_sensitive=False)()
        try:
            opoObj = await sync_to_async(lambda:OutcomeParticipants.objects.get(outcome=outcomeObj, participant=oPObj.participant, vhost=vhost,participant__morphed=fixture.teams_morphed), thread_sensitive=False)()
        except OutcomeParticipants.DoesNotExist:
            opoObj,_ = await sync_to_async(lambda:OutcomeParticipants.objects.get_or_create(outcome=outcomeObj, participant=oPObj.participant, vhost=vhost,participant__morphed=fixture.teams_morphed), thread_sensitive=False)()
        except OutcomeParticipants.MultipleObjectsReturned:
            opoObj = await sync_to_async(
                lambda: OutcomeParticipants.objects.filter(outcome=outcomeObj, participant=oPObj.participant,
                                                                  vhost=vhost,participant__morphed=fixture.teams_morphed).first(), thread_sensitive=False)()
        await object_setattrs(opoObj, ssp)
        await sync_to_async(lambda:opoObj.save(),thread_sensitive=False)()
        # print(opoObj)
        participants.append(opoObj)
    # print("-----")
    if "fixtures_states" in entry:
        for state in entry["fixtures_states"]:
            stateObj = await sync_to_async(lambda:State.objects.get(state_id=state["state_id"], vhost=vhost),thread_sensitive=False)()
            stateFixObj = await sync_to_async(lambda:Fixture.objects.get(fixture_id=state["fixture_id"], vhost=vhost),thread_sensitive=False)()
            if stateObj != await sync_to_async(lambda:stateFixObj.state,thread_sensitive=False)():
                stateFixObj.state = stateObj
                await sync_to_async(lambda:stateFixObj.save(),thread_sensitive=False)()
                # print(f"Fixture {stateFixObj.fixture_id}: State updated to {stateObj.abrv}")
    return outcomeObj, segments, participants


async def aprocess_fixture_market_data(entry, vhost, fixtureObj, sbkObj,leagueObj):
    if entry["participant_id"] == 0 and entry["side_id"] != 5: return False
    partObj = False
    try:
        partObj = await sync_to_async(lambda:Participant.objects.get(participant_id=entry["participant_id"], vhost=vhost, league=fixtureObj.league,morphed=fixtureObj.teams_morphed),thread_sensitive=False)()
    except Participant.MultipleObjectsReturned:
        partObj = await sync_to_async(
            lambda: Participant.objects.filter(participant_id=entry["participant_id"], vhost=vhost,
                                            league=fixtureObj.league,morphed=fixtureObj.teams_morphed).first(), thread_sensitive=False)()
    except Participant.DoesNotExist:
        # Handle Draws:
        if entry["side_id"] == 5:
            partObj,_ = await sync_to_async( lambda: Participant.objects.get_or_create(participant_id=entry["participant_id"], vhost=vhost,league=fixtureObj.league,name="DRAW",abrv="DRAW",morphed=fixtureObj.teams_morphed),thread_sensitive=False)()
            await sync_to_async(lambda:partObj.save(),thread_sensitive=False)()
            return False
    # if debug:
    #     await sync_to_async(lambda:print(partObj),thread_sensitive=False)()
    #     print(entry)
    if not partObj:
        await sync_to_async(lambda:print(f"Participant not found for {fixtureObj}"),thread_sensitive=False)()
        return False
    sideObj = await sync_to_async(lambda:Sides.objects.get(side_id=entry["side_id"], vhost=vhost),thread_sensitive=False)()
    mktTObj = await  sync_to_async(lambda:MarketType.objects.get(market_type_id=entry["market_type_id"], vhost=vhost),thread_sensitive=False)()
    segObj = await  sync_to_async(lambda:Segment.objects.get(segment_id=entry["segment_id"], vhost=vhost),thread_sensitive=False)()
    bttObj = await  sync_to_async(lambda:BetType.objects.get(betting_type_id=entry["betting_type_id"], vhost=vhost),thread_sensitive=False)()
    statObj = await  sync_to_async(lambda:MarketStatus.objects.get(market_status_id=entry["market_status_id"], vhost=vhost),thread_sensitive=False)()
    fmxObj =  await sync_to_async(lambda:FixtureMarket.objects.filter(vhost=vhost, market_id=entry["market_id"], participant=partObj,
                                          side=sideObj,league=leagueObj,
                                          sportsbook=sbkObj, fixture=fixtureObj,
                                          market_type=mktTObj, segment=segObj, market_status=statObj,
                                          betting_type=bttObj),thread_sensitive=False)()
    if await sync_to_async(lambda:fmxObj.count(),thread_sensitive=False)() == 0:
        fmxObj,_ = await sync_to_async(lambda:FixtureMarket.objects.get_or_create(vhost=vhost, market_id=entry["market_id"], participant=partObj,
                                                side=sideObj,league=leagueObj,
                                                sportsbook=sbkObj, fixture=fixtureObj,
                                                market_type=mktTObj, segment=segObj, market_status=statObj,
                                                betting_type=bttObj),thread_sensitive=False)()
        await sync_to_async(lambda:fmxObj.save(),thread_sensitive=False)()
    else:
        fmxObj = await sync_to_async(lambda:fmxObj.first(),thread_sensitive=False)()
    await object_setattrs(fmxObj, entry, rows=KIBL_MARKET_UPDATE_FIELDS)

    return fmxObj