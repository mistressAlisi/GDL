import json
import re
import unicodedata

from django import db
from django.forms import model_to_dict
from django.utils.timezone import now
from zope.interface.declarations import ObjectSpecification

from dataengine.drivers.kiblio.api.constants import KIBL_MARKET_UPDATE_FIELDS

from dataengine.drivers.kiblio.models import Participant, Sides, MarketType, Segment, BetType, MarketStatus, \
    FixtureMarket, League, Season, Location, FixtureType, Fixture, FixtureParticipants, Outcome, OutcomeSegmentScore, \
    OutcomeParticipants, State


def object_setattrs(obj, entry, **kwargs):
    keys = model_to_dict(obj, entry.keys()).keys()
    # print(keys)
    for k in keys:
        # print(k)
        if "rows" in kwargs:
            if hasattr(obj, k) and k in kwargs["rows"]:
                setattr(obj, k, entry[k])
        elif hasattr(obj, k):
            setattr(obj, k, entry[k])
    obj.save()

def process_fixture_data(entry,vhost):
    league = League.objects.get(league_id=entry["league_id"],vhost=vhost)
    season = Season.objects.get(season_id=entry["season_id"],vhost=vhost)
    location = Location.objects.get(location_id=entry["location_id"],vhost=vhost)
    fixture_type = FixtureType.objects.get(fixture_type_id=entry["fixture_type_id"],vhost=vhost)
    # try:
    #     fixtureObj = Fixture.objects.get(vhost=vhost, routing_key=entry["routing_key"])
    # except Fixture.DoesNotExist:
    try:
        fixtureObj,fcc = Fixture.objects.get_or_create(vhost=vhost, league=league, season=season, location=location,
                                                       fixture_type=fixture_type, fixture_id=entry["fixture_id"],
                                                       parent_fixture_id=entry["parent_fixture_id"],routing_key=entry["routing_key"])
        if fcc:
            fixtureObj.save()
    except db.utils.IntegrityError:
        fixtureObj = Fixture.objects.get(vhost=vhost,fixture_id=entry["fixture_id"])
    object_setattrs(fixtureObj, entry)

    league_name = unicodedata.normalize("NFKD", league.name or "").casefold()
    league_sport = league.sport.abrv.casefold()
    for p in entry["participants"]:
        # Women Leagues special handling:
        if re.search(r"\bwomen('?s)?\b", league_name) and league_sport != "tn":
            p["name"] += " W "
            print(f"Team name Morphed for Women's sport: {p['name']}")

        try:
            participantObj, c = Participant.objects.get_or_create(vhost=vhost, participant_id=p["participant_id"],
                                                                  league=league)
            if c:
                object_setattrs(participantObj, p)
        except Participant.MultipleObjectsReturned:
            participantObj = Participant.objects.filter(vhost=vhost, participant_id=p["participant_id"],
                                                        league=league).first()
        sideObj = Sides.objects.get(side_id=p["side_id"], vhost=vhost)
        fpObj = \
        FixtureParticipants.objects.get_or_create(vhost=vhost, fixture=fixtureObj, participant=participantObj,
                                                  side=sideObj, fixture_participant_id=p["fixture_participant_id"])[0]
        # print(p)
        object_setattrs(fpObj, p)
        # print(fpObj)
    # print("*****")
    return fixtureObj

def process_fixture_outcomes_data(entry,vhost,**kwargs):
    segments = []
    participants = []
    segObj = Segment.objects.get(segment_id=int(entry["segment_id"]), vhost=vhost)
    try:
        fixture = Fixture.objects.get(fixture_id=int(entry["fixture_id"]), vhost=vhost)
    except Fixture.DoesNotExist:
        return False,False,False
    try:
        outcomeObj = Outcome.objects.get(routing_key=entry["routing_key"], vhost=vhost,outcome_id=int(entry["outcome_id"]))
        outcomeObj.segment = segObj
        outcomeObj.save()
    except Outcome.DoesNotExist:
        outcomeObj = Outcome.objects.get_or_create(fixture=fixture, outcome_id=int(entry["outcome_id"]), segment=segObj, vhost=vhost)[0]
    except Outcome.MultipleObjectsReturned:
        outcomeObj = Outcome.objects.get(routing_key=entry["routing_key"],outcome_id=int(entry["outcome_id"]), vhost=vhost,segment=segObj)

    object_setattrs(outcomeObj, entry)
    outcomeObj.save()

    for ssc in entry["outcomes_segments_scores"]:
        # print(json.dumps(ssc))
        osegObj = Segment.objects.get(segment_id=ssc["segment_id"], vhost=vhost)

        _oPObj = FixtureParticipants.objects.filter(fixture_participant_id=ssc["fixture_participant_id"],
                                                    vhost=vhost)
        if not (_oPObj.exists()):
            from dataengine.drivers.kiblio.api.http import KiblHttpAPI
            http_api = KiblHttpAPI(vhost)
            _oPObj = http_api.fetch_fixture_participants(fixture)
            oPObj = _oPObj[0]
        else:
            oPObj = _oPObj[0]

        try:
            ossObj = OutcomeSegmentScore.objects.get(routing_key=ssc["routing_key"], vhost=vhost,segment=osegObj, participant=oPObj.participant)
            ossObj.save()
        except OutcomeSegmentScore.DoesNotExist:
            ossObj,ossCC = OutcomeSegmentScore.objects.get_or_create(outcome=outcomeObj, segment=osegObj, participant=oPObj.participant,vhost=vhost)
            # print("I'm creating a new OSS...")
            if ossCC: ossObj.save()
        except OutcomeSegmentScore.MultipleObjectsReturned:
            ossObj = OutcomeSegmentScore.objects.filter(routing_key=ssc["routing_key"], vhost=vhost, segment=osegObj,
                                                     participant=oPObj.participant).first()

        object_setattrs(ossObj, ssc)
        ossObj.save()
        segments.append(ossObj)
    # print("-----")
    for ssp in entry["outcomes_participants"]:
        oPObj = False
        # print(json.dumps(ssp,indent=4))
        # oPObj = FixtureParticipants.objects.get(fixture_participant_id=ssc["fixture_participant_id"],vhost=vhost)
        _oPObj = FixtureParticipants.objects.filter(fixture_participant_id=ssp["fixture_participant_id"],
                                                    vhost=vhost)
        if not (_oPObj.exists()):
            http_api = KiblHttpAPI(vhost)
            _oPObj = http_api.fetch_fixture_participants(fixture)
            oPObj = _oPObj[0]
        else:
            oPObj = _oPObj[0]


        try:
            opoObj = OutcomeParticipants.objects.get(outcome=outcomeObj, participant=oPObj.participant, vhost=vhost)
        except OutcomeParticipants.DoesNotExist:
            opoObj = OutcomeParticipants.objects.get_or_create(outcome=outcomeObj, participant=oPObj.participant, vhost=vhost)[0]
        object_setattrs(opoObj, ssp)
        opoObj.save()
        # print(opoObj)
        participants.append(opoObj)
    # print("-----")
    if "fixtures_states" in entry:
        for state in entry["fixtures_states"]:
            stateObj = State.objects.get(state_id=state["state_id"], vhost=vhost)
            stateFixObj = Fixture.objects.get(fixture_id=state["fixture_id"], vhost=vhost)
            if stateObj != stateFixObj.state:
                stateFixObj.state = stateObj
                stateFixObj.save()
                # print(f"Fixture {stateFixObj.fixture_id}: State updated to {stateObj.abrv}")
    return outcomeObj, segments, participants
    

def process_fixture_market_data(entry, vhost, fixtureObj, sbkObj):
    if entry["participant_id"] == 0: return False

    try:
        partObj = Participant.objects.get(participant_id=entry["participant_id"], vhost=vhost, league=fixtureObj.league)
    except Participant.DoesNotExist:
        # print("DNI")
        from dataengine.drivers.kiblio.api.http import KiblHttpAPI
        http_api = KiblHttpAPI(vhost)
        partObj = http_api.fetch_participants(league=fixtureObj.league, participant_id=entry["participant_id"])[0]
        # print(partObj)
    except Participant.MultipleObjectsReturned:
        partObj = Participant.objects.filter(participant_id=entry["participant_id"], vhost=vhost, league=fixtureObj.league).first()
    sideObj = Sides.objects.get(side_id=entry["side_id"], vhost=vhost)
    mktTObj = MarketType.objects.get(market_type_id=entry["market_type_id"], vhost=vhost)
    segObj = Segment.objects.get(segment_id=entry["segment_id"], vhost=vhost)
    bttObj = BetType.objects.get(betting_type_id=entry["betting_type_id"], vhost=vhost)
    statObj = MarketStatus.objects.get(market_status_id=entry["market_status_id"], vhost=vhost)
    fmxObj = FixtureMarket.objects.filter(vhost=vhost, market_id=entry["market_id"], participant=partObj,
                                          side=sideObj,
                                          sportsbook=sbkObj, fixture=fixtureObj,
                                          market_type=mktTObj, segment=segObj, market_status=statObj,
                                          betting_type=bttObj)
    if (fmxObj.exists()):
        fmxObj = \
        FixtureMarket.objects.get_or_create(vhost=vhost, market_id=entry["market_id"], participant=partObj,
                                            side=sideObj,
                                            sportsbook=sbkObj, fixture=fixtureObj,
                                            market_type=mktTObj, segment=segObj, market_status=statObj,
                                            betting_type=bttObj)[0]
        fmxObj.save()
    else:
        fmxObj = fmxObj[0]
    fixtureObj.updated_at = now()
    fixtureObj.save()
    object_setattrs(fmxObj, entry, rows=KIBL_MARKET_UPDATE_FIELDS)
    return fmxObj