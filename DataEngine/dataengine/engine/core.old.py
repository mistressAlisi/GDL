import importlib

from django.db import IntegrityError
from django.db.models import Q
from django.forms import model_to_dict
from django.utils.timezone import now
from logging import getLogger

from dataengine.models import DataEngineVHostConfig, GroupSyncStatus, SeasonSyncStatus, SportSyncStatus, TeamSyncStatus, \
    MatchSyncStatus, OddsSyncStatus, SegmentSyncStatus, OutcomeSyncStatus, OutcomeSegmentScoreSyncStatus, \
    OutcomeTeamsSyncStatus
from matches.models import Match
from odds.models import MatchOddsSummary
from outcomes.models import Outcome, Segment, OutcomeSegmentScore, OutcomeTeams
from sports.models import Group, Sport, Season
from teams.models import Team, TeamSport

from . import const as _const
from .abc import ABCDataEngineObj
from ..drivers.kiblio.models import OutcomeParticipants


class DataEngine(ABCDataEngineObj):
    def sync_sports_groups(self,auth=False,**kwargs):
        for group in self.currentDriverObject.get_sports_groups():
            try:
                groupObj = GroupSyncStatus.objects.get(
                    vhost=self.vhost,
                    driver_object_type=group["object_type"],
                    driver_object_uuid=group["object_uuid"],
                )
                update = True
            except GroupSyncStatus.DoesNotExist:
                # Only create the link if we're in authoritative mode:
                if auth:
                    groupObj = GroupSyncStatus.objects.get_or_create(
                        vhost=self.vhost,
                        driver_object_type=group["object_type"],
                        driver_object_uuid=group["object_uuid"],
                    )[0]
                    groupObj.save()
                    update = True
                else:
                    self.logger.warning(f"For Driver {self.currentDriverObject.name}, Object {group["object_type"]}/{group["object_uuid"]} is not linked to the System database and we're not in authoritative mode: This item will be skipped. ")
                    update = False
            # ONLY update the record if we're in auth mode, or the record was previously created:
            if update:
                # If we don't have a system uuid set, it means no link exists:
                if not groupObj.system_object_uuid:
                    try:
                        sys_groupObj = Group.objects.get(
                        Q(slug=group["slug"])|
                        Q(name=group["name"])
                        )
                        scr = False
                    except Group.DoesNotExist:
                        sys_groupObj,scr = Group.objects.get_or_create(
                            slug=group["slug"],
                            name=group["name"],
                        )
                        if scr:
                            self.logger.info(f"Group {group['name']}: Created in System Database!")
                    self._object_setattrs(sys_groupObj,group)
                    sys_groupObj.save()
                    groupObj.system_object_uuid = sys_groupObj.uuid
                    groupObj.system_object_type = f"{sys_groupObj._meta.app_label}.{sys_groupObj._meta.model_name}.{sys_groupObj._meta.object_name}"
                    groupObj.group = sys_groupObj
                    groupObj.last_sync = now()
                    groupObj.save()
                    self.logger.info(f"Group {group['name']}: Linked in System Database!")

                else:
                    sys_groupObj = Group.objects.get(uuid=groupObj.system_object_uuid)
                self.logger.info(f"Group {group['name']}: Updated in System Database!")
                self._object_setattrs(sys_groupObj, group)


    def sync_sports_seasons(self, auth=False, **kwargs):
        for season in self.currentDriverObject.get_sports_seasons():
            # print(season)
            try:
                seasonObj = SeasonSyncStatus.objects.get(
                    vhost=self.vhost,
                    driver_object_type=season["object_type"],
                    driver_object_uuid=season["object_uuid"],
                )
                update = True
            except SeasonSyncStatus.DoesNotExist:
                # Only create the link if we're in authoritative mode:
                if auth:
                    seasonObj = SeasonSyncStatus.objects.get_or_create(
                        vhost=self.vhost,
                        driver_object_type=season["object_type"],
                        driver_object_uuid=season["object_uuid"],
                    )[0]
                    seasonObj.save()
                    update = True
                else:
                    self.logger.warning(
                        f"For Driver {self.currentDriverObject.name}, Object {season["object_type"]}/{season["object_uuid"]} is not linked to the System database and we're not in authoritative mode: This item will be skipped. ")
                    update = False
            # ONLY update the record if we're in auth mode, or the record was previously created:
            if update:
                # If we don't have a system uuid set, it means no link exists:
                if not seasonObj.system_object_uuid:
                    sys_seasonObj, scr = Season.objects.get_or_create(
                        season_key=season["season_key"],
                        name=season["name"],
                    )
                    if scr:
                        self.logger.info(f"Season {season['name']}: Created in System Database!")
                    sys_seasonObj.save()
                    # seasonObj.system_object_uuid = sys_seasonObj.uuid
                    # seasonObj.system_object_type = f"{sys_seasonObj._meta.app_label}.{sys_seasonObj._meta.model_name}.{sys_seasonObj._meta.object_name}"
                    # seasonObj.season = sys_seasonObj
                    # seasonObj.last_sync = now()
                    self._set_systemObj_attr(seasonObj,sys_seasonObj,"season")
                    self.logger.info(f"Season {season['name']}: Linked in System Database!")
                    # seasonObj.save()

                else:
                    sys_seasonObj = Season.objects.get(uuid=seasonObj.system_object_uuid)
                self.logger.info(f"Season {season['name']}: Updated in System Database!")
                self._object_setattrs(sys_seasonObj, season)



    def get_link_obj(self,type,driver_object_type,driver_object_uuid):
            if type not in _const.SYSTEM_DATATYPE_MAP.keys():
                self.logger.warning(f"Type {type} is not supported by get_link_obj! Not registered in SYSTEM_DATATYPE_MAP.")
                return False
            try:
                return _const.SYSTEM_DATATYPE_MAP[type].objects.get(driver_object_uuid=driver_object_uuid,driver_object_type=driver_object_type)
            except:
                return False

    def sync_sports_sport(self, auth=False, **kwargs):
        for sport in self.currentDriverObject.get_sports_sports():
            # print(sport)
            try:
                sportObj = SportSyncStatus.objects.get(
                    vhost=self.vhost,
                    driver_object_type=sport["object_type"],
                    driver_object_uuid=sport["object_uuid"],
                )
                update = True
            except SportSyncStatus.DoesNotExist:
                # Only create the link if we're in authoritative mode:
                if auth:
                    sportObj = SportSyncStatus.objects.get_or_create(
                        vhost=self.vhost,
                        driver_object_type=sport["object_type"],
                        driver_object_uuid=sport["object_uuid"],
                    )[0]
                    sportObj.save()
                    update = True
                else:
                    self.logger.warning(
                        f"For Driver {self.currentDriverObject.name}, Object {sport["object_type"]}/{sport["object_uuid"]} is not linked to the System database and we're not in authoritative mode: This item will be skipped. ")
                    update = False
            # ONLY update the record if we're in auth mode, or the record was previously created:
            if update:
                # If we don't have a system uuid set, it means no link exists:
                if not sportObj.system_object_uuid:
                    # Get the group mapping so we can link the Sport correctly:
                    groupObj = self.get_link_obj('group',sport["group_type"],sport["group_uuid"])
                    if groupObj:
                        try:
                            sys_sportObj, scr = Sport.objects.get_or_create(
                                key=sport["key"],
                                title=sport["title"],
                                group=groupObj.group,
                            )
                        except IntegrityError:
                            sys_sportObj = Sport.objects.get(key=sport["key"])
                            scr = False
                        if scr:
                            self.logger.info(f"Sport {sport['title']}: Created in System Database!")
                        sys_sportObj.save()
                        # sportObj.system_object_uuid = sys_sportObj.uuid
                        # sportObj.system_object_type = f"{sys_sportObj._meta.app_label}.{sys_sportObj._meta.model_name}.{sys_sportObj._meta.object_name}"
                        # sportObj.sport = sys_sportObj
                        # sportObj.last_sync = now()
                        self._set_systemObj_attr(sportObj, sys_sportObj, "sport")
                        self.logger.info(f"Sport {sport['title']}: Linked in System Database!")
                        # print(f"Sport {sport['title']}: Linked in System Database!")
                        # sportObj.save()

                else:
                    sys_sportObj = Sport.objects.get(uuid=sportObj.system_object_uuid)
                self.logger.info(f"Sport {sport['title']}: Updated in System Database!")
                self._object_setattrs(sys_sportObj, sport,rows=["inserted_on"])



    def sync_teams(self, auth=False, **kwargs):
        for team in self.currentDriverObject.get_teams():
            # print(sport)
            try:
                teamObj = TeamSyncStatus.objects.get(
                    vhost=self.vhost,
                    driver_object_type=team["object_type"],
                    driver_object_uuid=team["object_uuid"],
                )
                update = True
            except TeamSyncStatus.DoesNotExist:
                # Only create the link if we're in authoritative mode:
                if auth:
                    teamObj = TeamSyncStatus.objects.get_or_create(
                        vhost=self.vhost,
                        driver_object_type=team["object_type"],
                        driver_object_uuid=team["object_uuid"],
                    )[0]
                    teamObj.save()
                    update = True
                else:
                    self.logger.warning(
                        f"For Driver {self.currentDriverObject.name}, Object {team["object_type"]}/{team["object_uuid"]} is not linked to the System database and we're not in authoritative mode: This item will be skipped. ")
                    update = False
            # ONLY update the record if we're in auth mode, or the record was previously created:
            if update:
                # If we don't have a system uuid set, it means no link exists:
                if not teamObj.system_object_uuid:
                    # Get the group mapping so we can link the Sport correctly:
                    sportObj = self.get_link_obj('sport',team["sport_type"],team["sport_uuid"])
                    if sportObj:
                        try:
                            sys_TeamObj, scr = Team.objects.get_or_create(
                                key=team["key"],
                                name=team["name"],
                            )
                        except IntegrityError:
                            sys_TeamObj = Team.objects.get(key=team["key"])
                            scr = False
                        if scr:
                            sys_TeamObj.save()
                            self.logger.info(f"Team {team['name']}: Created in System Database!")
                            tsObj = TeamSport.objects.get_or_create(team=sys_TeamObj,sport=sportObj.sport)[0]
                            tsObj.save()
                        sys_TeamObj.save()
                        # teamObj.system_object_uuid = sys_TeamObj.uuid
                        # teamObj.system_object_type = f"{sys_TeamObj._meta.app_label}.{sys_TeamObj._meta.model_name}.{sys_TeamObj._meta.object_name}"
                        # teamObj.team = sys_TeamObj
                        # teamObj.last_sync = now()
                        self._set_systemObj_attr(teamObj, sys_TeamObj, "team")
                        self.logger.info(f"Sport {team['name']}: Linked in System Database!")
                        # print(f"Team {team['name']}: Linked in System Database!")
                        # teamObj.save()

                else:
                    sys_TeamObj = Team.objects.get(uuid=teamObj.system_object_uuid)
                self.logger.info(f"Team {team['name']}: Updated in System Database!")
                self._object_setattrs(sys_TeamObj, team,rows=["inserted_on","parent_team","mascot"])

    def sync_segments(self, auth=False, **kwargs):
        for segment in self.currentDriverObject.get_segments():
            # print(season)
            try:
                segmentObj = SegmentSyncStatus.objects.get(
                    vhost=self.vhost,
                    driver_object_type=segment["object_type"],
                    driver_object_uuid=segment["object_uuid"],
                )
                update = True
            except SegmentSyncStatus.DoesNotExist:
                # Only create the link if we're in authoritative mode:
                if auth:
                    segmentObj = SegmentSyncStatus.objects.get_or_create(
                        vhost=self.vhost,
                        driver_object_type=segment["object_type"],
                        driver_object_uuid=segment["object_uuid"],
                    )[0]
                    segmentObj.save()
                    update = True
                else:
                    self.logger.warning(
                        f"For Driver {self.currentDriverObject.name}, Object {segment["object_type"]}/{segment["object_uuid"]} is not linked to the System database and we're not in authoritative mode: This item will be skipped. ")
                    update = False
            # ONLY update the record if we're in auth mode, or the record was previously created:
            if update:
                # If we don't have a system uuid set, it means no link exists:
                if not segmentObj.system_object_uuid:
                    sys_segmentObj, scr = Segment.objects.get_or_create(
                        segment_id=segment["id"],
                        name=segment["name"],
                        vhost=self.vhost,
                    )
                    if scr:
                        self.logger.info(f"Segment {segment['name']}: Created in System Database!")
                    segmentObj.system_object_uuid = sys_segmentObj.uuid
                    segmentObj.system_object_type = f"{sys_segmentObj._meta.app_label}.{sys_segmentObj._meta.model_name}.{sys_segmentObj._meta.object_name}"
                    segmentObj.segment = sys_segmentObj
                    segmentObj.last_sync = now()
                    sys_segmentObj.save()
                    self._set_systemObj_attr(segmentObj,sys_segmentObj,"segment")
                    self.logger.info(f"Segment {segment['name']}: Linked in System Database!")
                    segmentObj.save()

                else:
                    sys_segmentObj = Segment.objects.get(uuid=segmentObj.system_object_uuid)
                self.logger.info(f"Segment {segment['name']}: Updated in System Database!")
                self._object_setattrs(sys_segmentObj, segment)


    def sync_matches(self, auth=False, **kwargs):
        # print(f"Sync Matches {kwargs}...")
        matches = self.currentDriverObject.get_matches(**kwargs)
        for match in matches:
            sys_MatchObj = False
            try:
                matchObj = MatchSyncStatus.objects.get(
                    vhost=self.vhost,
                    driver_object_type=match["object_type"],
                    driver_object_uuid=match["object_uuid"],
                )
                update = True
            except MatchSyncStatus.DoesNotExist:
                # Only create the link if we're in authoritative mode:
                if auth:
                    matchObj = MatchSyncStatus.objects.get_or_create(
                        vhost=self.vhost,
                        driver_object_type=match["object_type"],
                        driver_object_uuid=match["object_uuid"],
                    )[0]
                    matchObj.save()
                    update = True
                else:
                    self.logger.warning(
                        f"For Driver {self.currentDriverObject.name}, Object {match["object_type"]}/{match["object_uuid"]} is not linked to the System database and we're not in authoritative mode: This item will be skipped. ")
                    update = False
                # ONLY update the record if we're in auth mode, or the record was previously created:
            if update:
                # If we don't have a system uuid set, it means no link exists:
                if not matchObj.system_object_uuid:
                    # Get the group mapping so we can link the Sport correctly:
                    sportObj = self.get_link_obj('sport', match["sport_type"], match["sport_uuid"])
                    seasonObj = self.get_link_obj('season', match["season_type"], match["season_uuid"])
                    hTObj = self.get_link_obj("team", match["home_team_type"], match["home_team_uuid"])
                    aTObj = self.get_link_obj("team", match["away_team_type"], match["away_team_uuid"])

                    if sportObj and seasonObj and hTObj and aTObj:
                        scr = False
                        _sys_matchObj = Match.objects.filter(vhost=self.vhost,id=match["id"],routing_key=match["routing_key"])
                        if len(_sys_matchObj) > 0:
                            sys_MatchObj = _sys_matchObj[0]
                            self.logger.info(f"Match {match['name']}: Found in System Database!")
                        else:
                            try:
                                sys_MatchObj, scr = Match.objects.get_or_create(
                                    vhost=self.vhost,
                                    id = match["id"],
                                    routing_key=match["routing_key"],
                                    name = match["name"],
                                    home_team = hTObj.team,
                                    away_team = aTObj.team,
                                    sport = sportObj.sport,
                                    season = seasonObj.season,
                                    commence_time=match["commence_time"],
                                    )
                                if scr:
                                    self.logger.info(f"Match {match['name']}: Updated in System Database!")
                                    sys_MatchObj.save()
                            except IntegrityError:
                                sys_MatchObj = Match.objects.get(id=match["id"], vhost=self.vhost)


                        sys_MatchObj.save()
                        matchObj.system_object_uuid = sys_MatchObj.uuid
                        matchObj.system_object_type = f"{sys_MatchObj._meta.app_label}.{sys_MatchObj._meta.model_name}.{sys_MatchObj._meta.object_name}"
                        matchObj.match = sys_MatchObj
                        matchObj.last_sync = now()
                        self._set_systemObj_attr(matchObj, sys_MatchObj, "match")
                        self.logger.info(f"Sport {match['name']}: Linked in System Database!")
                        # print(f"Team {team['name']}: Linked in System Database!")
                        # matchObj.save()

                else:
                    sys_MatchObj = Match.objects.get(uuid=matchObj.system_object_uuid,vhost=self.vhost)
                    self.logger.info(f"Match {match['name']}: Updated in System Database!")
                    # print(f"Match {match['name']}: Updated in System Database!")
                if sys_MatchObj and match:
                    sys_MatchObj.set_status(short=match['status_short'],long=match['status_long'])
                    self._object_setattrs(sys_MatchObj, match,rows=["commence_time"])
                    # print("Copied copied")


    def sync_markets(self, auth=False, **kwargs):
        self.sync_markets_ml(auth=auth, **kwargs)

    def sync_markets_ml(self, auth=False, **kwargs):
        matchodds = self.currentDriverObject.get_match_odds_ml(**kwargs)
        # print(matchodds)
        for match in matchodds:
            matchObj = self.get_link_obj("match", match["object_type"], match["object_uuid"])
            try:
                oddSyncStatus = OddsSyncStatus.objects.get(
                    vhost=self.vhost,
                    driver_object_type=match["object_type"],
                    driver_object_uuid=match["object_uuid"],
                )
                update = True
            except OddsSyncStatus.DoesNotExist:
                # Only create the link if we're in authoritative mode:
                if auth:
                    oddSyncStatus = OddsSyncStatus.objects.get_or_create(
                        vhost=self.vhost,
                        driver_object_type=match["object_type"],
                        driver_object_uuid=match["object_uuid"],
                    )[0]
                    oddSyncStatus.save()
                    update = True
                else:
                    self.logger.warning(
                        f"For Driver {self.currentDriverObject.name}, Object {match["object_type"]}/{match["object_uuid"]} is not linked to the System database and we're not in authoritative mode: This item will be skipped. ")
                    update = False
                # ONLY update the record if we're in auth mode, or the record was previously created:
            if update:
                # If we don't have a system uuid set, it means no link exists:
                if not oddSyncStatus.system_object_uuid:
                    # Get the team mapping so we can link the Sport correctly:
                    hTObj = self.get_link_obj("team", match["home_team_type"], match["home_team_uuid"])
                    aTObj = self.get_link_obj("team", match["away_team_type"], match["away_team_uuid"])

                    # print(hTObj.team,aTObj.team)
                    # print(matchObj,matchObj.match)
                    # print(hTObj,aTObj)
                    if hTObj and aTObj:
                        sys_OddsObj,scr = MatchOddsSummary.objects.get_or_create(
                            match=matchObj.match,
                            home_team=hTObj.team,
                            away_team=aTObj.team,

                        )
                        if scr:
                            sys_OddsObj.save()
                            self.logger.info(f"Match Odds Summary (ML)  for match {match['id']}: Created in System Database!")

                        sys_OddsObj.save()
                        # oddSyncStatus.system_object_uuid = sys_OddsObj.uuid
                        # oddSyncStatus.system_object_type = f"{sys_OddsObj._meta.app_label}.{sys_OddsObj._meta.model_name}.{sys_OddsObj._meta.object_name}"
                        # oddSyncStatus.matchOdds = sys_OddsObj
                        # oddSyncStatus.last_sync = now()
                        self._set_systemObj_attr(oddSyncStatus, sys_OddsObj, "season")
                        self._object_setattrs(sys_OddsObj, match, rows=["home_price","home_price_fraction","away_price","away_price_fraction","draw_price","draw_price_fraction"])
                        self.logger.info(f"Match Odds for match  {match['id']}: Linked in System Database!")
                        # print(f"Team {team['name']}: Linked in System Database!")
                        # matchObj.save()

                else:
                    sys_OddsObj = MatchOddsSummary.objects.get(uuid=oddSyncStatus.system_object_uuid)
                    self.logger.info(f"Match  Odds in M# {match['id']}: Updated in System Database!")
                    self._object_setattrs(sys_OddsObj, match, rows=["home_price","home_price_fraction","away_price","away_price_fraction","draw_price","draw_price_fraction"])
                # print(f"Match Moneyline Odds in M# {match['id']}: Updated in System Database!")

    def sync_outcomes(self, auth=False, **kwargs):
        # print(f"Syncing Outcomes {kwargs}...")
        outcomes = self.currentDriverObject.get_outcomes(**kwargs)
        # print(outcomes)
        for od in outcomes:
            # print(od)
            # Do we have a mapping key set? Else use data to match:
            sys_OutObj = False
            segmObj = self.get_link_obj("segment", od["outcome"]["segment_type"], od["outcome"]["segment_uuid"])
            matchObj = self.get_link_obj("match", od["outcome"]["fixture_type"], od["outcome"]["fixture_uuid"])

            if "outcome" in self.currentDriverObject.PKEY_MODEL_MAPPINGS:
                key_name = self.currentDriverObject.PKEY_MODEL_MAPPINGS["outcome"]
                # Try to use the key listed on both ends:

                key_val = od["outcome"][key_name]
                # print(key_name, key_val)
                try:
                    sys_OutObj = Outcome.objects.get(**{key_name: key_val})
                except Outcome.DoesNotExist:
                    sys_OutObj = False
                    if not sys_OutObj and auth:
                        sys_OutObj,scr = Outcome.objects.get_or_create(
                            vhost=self.vhost,
                            match=matchObj.match,
                            segment=segmObj.segment,
                            outcome_id=od["outcome"]["id"],
                        )
                        if scr:
                            sys_OutObj.save()

                            self.logger.info(f"Outcome {od['outcome']['id']}: Created in System Database!")
                    else:

                        self.logger.warning(
                            f"For Driver {self.currentDriverObject.name}, Object {od["outcome"]["object_type"]}/{od["outcome"]["object_uuid"]} is not linked to the System database and we're not in authoritative mode: This item will be skipped. ")
            else:
                sys_OutObj, scr = Outcome.objects.get_or_create(
                    vhost=self.vhost,
                    match=matchObj.match,
                    segment=segmObj.segment,
                    outcome_id=od["outcome"]["id"],
                )
                if scr:
                    sys_OutObj.save()
                    self.logger.info(f"Outcome {od['outcome']['id']}: Created in System Database!")
            try:
                outObj = OutcomeSyncStatus.objects.get(
                    vhost=self.vhost,
                    driver_object_type=od["outcome"]["object_type"],
                    driver_object_uuid=od["outcome"]["object_uuid"],
                )
            except OutcomeSyncStatus.DoesNotExist:
                # Only create the link if we're in authoritative mode:
                if auth:
                    outObj = OutcomeSyncStatus.objects.get_or_create(
                        vhost=self.vhost,
                        driver_object_type=od["outcome"]["object_type"],
                        driver_object_uuid=od["outcome"]["object_uuid"],
                    )[0]
                    outObj.save()

                else:
                    self.logger.warning(
                        f"For Driver {self.currentDriverObject.name}, Object {od["outcome"]["object_type"]}/{od["outcome"]["object_uuid"]} is not linked to the System database and we're not in authoritative mode: This item will be skipped. ")

                # ONLY update the record if we're in auth mode, or the record was previously created:
            if auth and sys_OutObj:
                # If we don't have a system uuid set, it means no link exists:

                if not outObj.system_object_uuid:
                        outObj.system_object_uuid = sys_OutObj.uuid
                        outObj.system_object_type = f"{sys_OutObj._meta.app_label}.{sys_OutObj._meta.model_name}.{sys_OutObj._meta.object_name}"
                        outObj.outcome = sys_OutObj
                        outObj.save()
                self.logger.info(f"Outcomes {od['outcome']["id"]}: Updated in System Database!")
                # print(f"Outcomes {od['outcome']["id"]}: Updated in System Database!")
                self._object_setattrs(sys_OutObj, od["outcome"])
            if "teams" in od and sys_OutObj:
                for tea in od["teams"]:
                    sys_teamObj = None
                    teamObj = self.get_link_obj("team", tea["team_type"],
                                                tea["team_uuid"])
                    if "outcome_participant" in self.currentDriverObject.PKEY_MODEL_MAPPINGS:
                        key_name = self.currentDriverObject.PKEY_MODEL_MAPPINGS["outcome_segment"]
                        # Try to use the key listed on both ends:
                        key_val = tea[key_name]
                        # print(key_name, key_val)
                        try:
                            sys_teamObj = OutcomeTeams.objects.get(**{key_name: key_val})
                        except OutcomeTeams.DoesNotExist:
                            sys_teamObj = False

                            if not sys_teamObj and auth:

                                sys_teamObj, scr = OutcomeTeams.objects.get_or_create(
                                    vhost=self.vhost,
                                    outcome=sys_OutObj,
                                    team=teamObj.team,

                                )
                                if scr:
                                    sys_teamObj.save()
                                    self.logger.info(f"Outcome Team/Participant {tea['id']}: Created in System Database!")
                            else:
                                self.logger.warning(
                                    f"For Driver {self.currentDriverObject.name}, Object {tea["object_type"]}/{tea["object_uuid"]} is not linked to the System database and we're not in authoritative mode: This item will be skipped. ")
                    else:
                        sys_teamObj, scr = OutcomeTeams.objects.get_or_create(
                            vhost=self.vhost,
                            outcome=sys_OutObj,
                            team=teamObj.team,

                        )
                        if scr:
                            sys_teamObj.save()
                            self.logger.info(f"Outcome Segment {tea['id']}: Created in System Database!")
                    try:
                        outSegObj = OutcomeTeamsSyncStatus.objects.get(
                            vhost=self.vhost,
                            driver_object_type=tea["object_type"],
                            driver_object_uuid=tea["object_uuid"],
                        )
                    except OutcomeTeamsSyncStatus.DoesNotExist:
                        # Only create the link if we're in authoritative mode:
                        if auth:
                            outSegObj = OutcomeTeamsSyncStatus.objects.get_or_create(
                                vhost=self.vhost,
                                driver_object_type=tea["object_type"],
                                driver_object_uuid=tea["object_uuid"],
                            )[0]
                            outSegObj.save()

                        else:
                            self.logger.warning(
                                f"For Driver {self.currentDriverObject.name}, Object {tea["object_type"]}/{tea["object_uuid"]} is not linked to the System database and we're not in authoritative mode: This item will be skipped. ")

                        # ONLY update the record if we're in auth mode, or the record was previously created:
                    # print(sys_teamObj)
                    if auth and sys_teamObj:
                        # If we don't have a system uuid set, it means no link exists:

                        if not outSegObj.system_object_uuid:
                            outSegObj.system_object_uuid = sys_teamObj.uuid
                            outSegObj.system_object_type = f"{sys_teamObj._meta.app_label}.{sys_teamObj._meta.model_name}.{sys_teamObj._meta.object_name}"
                            outSegObj.team = sys_teamObj
                            outSegObj.save()
                        self.logger.info(f"Outcome Team {tea["id"]}: Updated in System Database!")
                        # print(f"Outcome Team {tea["id"]}: Updated in System Database!")
                        self._object_setattrs(sys_teamObj, tea)

    def update_driver(self):
        self.currentDriverObject.update_all()

    def call_driver_update(self):
        """
        Update all drivers installed and enabled in the VHost: Pull data from their respective sources.
        :return:
        """
        self.logger.info("Updating all drivers...")
        for driver in self.drivers:
            self.logger.info(f"Updating Driver {driver}")
            self._load_driver(driver.driver)
            self.update_driver()

    def sync_authoritative_drivers(self):
        """
        Sync Authoritative drivers TO the database. Ie, Populate/update the system database for the given vHost,
        All Authoritative drivers will be synced in order of priority..
        :return:
        """
        auth = True
        self.logger.info("Syncing authoritative drivers...")
        for driver in self.drivers:
            if driver.authoritative:
                self.logger.info(f"Syncing Driver {driver}")
                self._load_driver(driver.driver)
                self.logger.info(f"Syncing Groups...")
                self.sync_sports_groups(auth)
                self.logger.info(f"Syncing Seasons...")
                self.sync_sports_seasons(auth)
                self.logger.info(f"Syncing Sports...")
                self.sync_sports_sport(auth)
                self.logger.info(f"Syncing Teams...")
                self.sync_teams(auth)
                self.logger.info(f"Syncing Segments")
                self.sync_segments(auth)
                self.logger.info(f"Syncing Matches...")
                self.sync_matches(auth)
                self.logger.info(f"Syncing Markets...")
                self.sync_markets(auth)
                self.logger.info(f"Syncing Outcomes...")
                self.sync_outcomes(auth)