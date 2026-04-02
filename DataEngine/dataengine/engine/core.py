import importlib
import logging
from datetime import datetime
from multiprocessing import Process,Event
from types import SimpleNamespace
from uuid import UUID

import pytz
from django.conf import settings
from django.core.exceptions import MultipleObjectsReturned
from django.db import IntegrityError
from django.db.models import Q
from django.forms import model_to_dict
from django.utils.timezone import now, localtime
from logging import getLogger


from grader.daemon.const import GRADER_MATCH_FINISHED_STATUS_SHORT, GRADER_MATCH_FINISHED_STATUS_LONG
from .abc import ABCDataEngineObj



class DataEngine(ABCDataEngineObj,Process):

    def _child_init(self):
        """
        Runs inside the forked child *after* django.setup().
        Safe place for model imports.
        """
        super()._child_init()
        from dataengine.models import DataEngineVHostConfig, GroupSyncStatus, SeasonSyncStatus, SportSyncStatus, \
            TeamSyncStatus, \
            MatchSyncStatus, OddsSyncStatus, SegmentSyncStatus, OutcomeSyncStatus, OutcomeSegmentScoreSyncStatus, \
            OutcomeTeamsSyncStatus
        from dataengine.drivers.goalserve.models.baseball import BaseBallScore, BaseBallFixture
        from odds.models import MatchOddsSummary, Bookmaker
        from outcomes.engine import OutcomesEngine
        from outcomes.models import Outcome, Segment, OutcomeSegmentScore, OutcomeTeams
        from sports.models import Group, Sport, Season
        from teams.models import Team, TeamSport
        from ..drivers.kiblio.models import OutcomeParticipants
        from matches.models import Match

        self.last_timestamp = localtime()
        self.models = SimpleNamespace(
            DataEngineVHostConfig=DataEngineVHostConfig,
            GroupSyncStatus=GroupSyncStatus,
            SeasonSyncStatus=SeasonSyncStatus,
            SportSyncStatus=SportSyncStatus,
            TeamSyncStatus=TeamSyncStatus,
            MatchSyncStatus=MatchSyncStatus,
            OddsSyncStatus=OddsSyncStatus,
            SegmentSyncStatus=SegmentSyncStatus,
            OutcomeSyncStatus=OutcomeSyncStatus,
            OutcomeSegmentScoreSyncStatus=OutcomeSegmentScoreSyncStatus,
            OutcomeTeamsSyncStatus=OutcomeTeamsSyncStatus,
            BaseBallScore=BaseBallScore,
            BaseBallFixture=BaseBallFixture,
            MatchOddsSummary=MatchOddsSummary,
            Bookmaker=Bookmaker,
            OutcomesEngine=OutcomesEngine,
            Outcome=Outcome,
            Segment=Segment,
            OutcomeSegmentScore=OutcomeSegmentScore,
            OutcomeTeams=OutcomeTeams,
            Group=Group,
            Sport=Sport,
            Season=Season,
            Team=Team,
            TeamSport=TeamSport,
            OutcomeParticipants=OutcomeParticipants,
            Match=Match

        )
        self.sync_type_table = {
            "group": GroupSyncStatus,
            "sport": SportSyncStatus,
            "season": SeasonSyncStatus,
            "team": TeamSyncStatus,
            "match": MatchSyncStatus,
            "segment": SegmentSyncStatus,
            "odds": OddsSyncStatus,
            "outcome_teams_sync": OutcomeTeamsSyncStatus,
        }


        self.logger.debug("APITennisAsyncDaemon: Django models bound in child")
    def __init__(self, vhost, verbose=False, interval_between_runs=60, **kwargs):
        Process.__init__(self,**kwargs)
        ABCDataEngineObj.__init__(self,vhost,**kwargs)
        self.logger = logging.getLogger(f"dataengine.dataengine.engine.core.{self.__class__.__name__}")
        self.verbose = verbose
        self.interval_between_runs = interval_between_runs
        self.last_update = None
        # exit signal for clean shutdown
        self._stop_event = Event()
        self.outcomeEngine = self.models.OutcomesEngine(vhost=self.vhost)

    def stop(self):
        """Signal the process to stop on next loop."""
        self._stop_event.set()

    def create_sync_object(self,sync_type,system_object,driver_object_type,driver_object_uuid):
        qkwargs = {sync_type:system_object,'driver_object_uuid':driver_object_uuid,'driver_object_type':driver_object_type,
                   'system_object_type':system_object._meta.model_name,'system_object_uuid':system_object.uuid}
        obj,_ = self.sync_type_table[sync_type].objects.get_or_create(**qkwargs)
        obj.save()
        return obj

    def find_sync_objects(self,sync_type,object_type,system_obj):

        qkwargs = {sync_type: system_obj, "driver_object_type": object_type}
        return self.sync_type_table[sync_type].objects.filter(**qkwargs)


    def find_sync_object(self,sync_type,object_type,object_uuid,system_obj=False):
        try:
            if not system_obj:
                try:
                    return self.sync_type_table[sync_type].objects.get(driver_object_type=object_type, driver_object_uuid=object_uuid)
                except self.sync_type_table[sync_type].MultipleObjectsReturned:
                    return self.sync_type_table[sync_type].objects.filter(driver_object_type=object_type,
                                                                       driver_object_uuid=object_uuid)[0]
            else:
                qkwargs = {sync_type:system_obj,"driver_object_type":object_type}
                try:
                    return self.sync_type_table[sync_type].objects.get(**qkwargs)
                except self.sync_type_table[sync_type].MultipleObjectsReturned:
                    return self.sync_type_table[sync_type].objects.filter(**qkwargs)[0]
        except self.sync_type_table[sync_type].DoesNotExist:
            return None

    def create_segment(self,segment_data):
        sys_segmentObj, scr = self.models.Segment.objects.get_or_create(
            segment_id=segment_data["id"],
            name=segment_data["name"],
            vhost=self.vhost,
        )
        self._object_setattrs(sys_segmentObj,segment_data)
        sys_segmentObj.save()
        self.logger.info(f"Segment {segment_data['name']}: Linked in System Database!")
        return sys_segmentObj

    def create_sports_group(self,group_data):
        sys_groupObj,_ = self.models.Group.objects.get_or_create(
            slug=group_data["slug"],
            name=group_data["name"],
            vhost=self.vhost,
        )
        self._object_setattrs(sys_groupObj, group_data)
        sys_groupObj.save()
        self.logger.info(f"Group {group_data['name']}: Created in System Database!")
        return sys_groupObj

    def create_sports_season(self,season_data):
        sys_seasonObj, scr = self.models.Season.objects.get_or_create(
            season_key=season_data["season_key"],
            name=season_data["name"],
        )
        self._object_setattrs(sys_seasonObj, season_data,rows=["season"])
        sys_seasonObj.save()
        self.logger.info(f"Season {season_data['title']}: Created in System Database!")
        return sys_seasonObj

    def create_sports_sport(self,groupObj,sports_data):
        try:
            sys_sportObj,_ = self.models.Sport.objects.get_or_create(
                                    key=sports_data["key"],
                                    title=sports_data["title"],
                                    group=groupObj,
                                    vhost=self.vhost,
            )
            self._object_setattrs(sys_sportObj, sports_data,rows=["logo","sport_mask","inserted_on","updated_on"])
            sys_sportObj.save()
        except IntegrityError:
            sys_sportObj = self.models.Sport.objects.get(key=sports_data["key"],vhost=self.vhost)
        self.logger.info(f"Sport {sports_data['title']}: Created in System Database!")
        return sys_sportObj

    def create_team(self,team_data,sportObj):
        sys_TeamObj,_ = self.models.Team.objects.get_or_create(
            key=team_data["key"],
            name=team_data["name"],
            vhost=self.vhost,
        )
        self._object_setattrs(sys_TeamObj, team_data,rows=["country","bday","logo","mascot","parent_team","inserted_on","updated_on"])
        sys_TeamObj.save()
        self.logger.info(f"Team {team_data['name']}: Created in System Database!")
        tsObj,_ = self.models.TeamSport.objects.get_or_create(team=sys_TeamObj, sport=sportObj)
        tsObj.save()
        return sys_TeamObj

    def create_and_update_outcome(self,match,driver,outcome_data):
        # print(outcome_data["id"])
        try:
            sys_OutObj, scr = self.models.Outcome.objects.get_or_create(
                vhost=self.vhost,
                match=match,
                driver=driver,
                outcome_id=outcome_data["id"],
                segment=outcome_data["segment"]
                )
        except KeyError:
            print("KeyError")
            print(outcome_data)
            return False
        self._object_setattrs(sys_OutObj, outcome_data,rows=["status_long","status_short","clock","is_current","is_start_game","is_end_game","is_start_segment","is_end_segment"])
        sys_OutObj.save()
        return sys_OutObj

    def create_and_update_ml_odds_summary(self,match,driver,summary_data,**kwargs):
        margs = {
                "vhost":self.vhost,
                "match":match,
                "driver":driver,
                "home_team":match.home_team,
                "away_team":match.away_team,
                }
        if "bookmaker" in summary_data:
            bookmaker = self.create_and_update_bookmaker(summary_data["bookmaker"])
            margs["bookmaker"] = bookmaker
        # print(margs)
        _sys_OddsObj = self.models.MatchOddsSummary.objects.filter(**margs)
        if (len(_sys_OddsObj) < 1):
            sys_OddsObj, scr = self.models.MatchOddsSummary.objects.get_or_create(**margs)
        else:
            sys_OddsObj = _sys_OddsObj[0]
        self._object_setattrs(sys_OddsObj, summary_data,rows=["home_price","home_price_fraction","away_price","away_price_fraction","draw_price","draw_price_fraction"])
        sys_OddsObj.save()
        return sys_OddsObj


    def create_and_update_outcome_team(self,outcome,team,driver,outcome_data):
        ckargs = {
            "vhost":self.vhost,
            "outcome":outcome,
            "team":team,
            "driver":driver,
            "routing_key":outcome_data["routing_key"],
        }
        _sys_teamObj = self.models.OutcomeTeams.objects.filter(**ckargs)
        if (len(_sys_teamObj) < 1):
            sys_teamObj,_ = self.models.OutcomeTeams.objects.get_or_create(**ckargs)
        else:
            sys_teamObj = _sys_teamObj[0]
        self._object_setattrs(sys_teamObj,outcome_data,rows=["score","is_winner"])
        return sys_teamObj

    def create_and_update_bookmaker(self,bookmaker_data):
        ckargs = {
            "vhost":self.vhost,
            "key":bookmaker_data["tag"],
            "name": bookmaker_data["name"],
        }
        _sys_teamObj = self.models.Bookmaker.objects.filter(**ckargs)
        if (len(_sys_teamObj) < 1):
            sys_teamObj, scr = self.models.Bookmaker.objects.get_or_create(**ckargs)
        else:
            sys_teamObj = _sys_teamObj[0]
        self._object_setattrs(sys_teamObj,bookmaker_data,rows=["card_logo","large_logo","feed_source_id","feed_type_id"])
        return sys_teamObj

    def create_and_update_outcome_segment(self,outcome,team,driver,segment_data):
        ckargs = {
            "vhost":self.vhost,
            "outcome":outcome,
            "team": team,
            "driver":driver,
            "segment":segment_data["segment"],
            "state_id": segment_data["state_id"],
        }
        _sys_teamObj = self.models.OutcomeSegmentScore.objects.filter(**ckargs)
        if (len(_sys_teamObj) < 1):
            sys_teamObj, scr = self.models.OutcomeSegmentScore.objects.get_or_create(**ckargs)
        else:
            sys_teamObj = _sys_teamObj[0]
        self._object_setattrs(sys_teamObj,segment_data,rows=["score","is_winner","routing_key"])
        return sys_teamObj

    def create_match(self,match_data):
        # Get Group first:
        groupLink = self.find_sync_object("group",match_data["group"]["object_type"],match_data["group"]["object_uuid"])
        if groupLink:
            group = groupLink.group
        else:
            group = self.create_sports_group(match_data["group"])
            groupLink = self.create_sync_object("group",group,match_data["group"]["object_type"],match_data["group"]["object_uuid"])
        # Now get the Sports:
        sportLink = self.find_sync_object("sport",match_data["sport"]["object_type"],match_data["sport"]["object_uuid"])
        if sportLink:
            sport = sportLink.sport
        else:
            sport = self.create_sports_sport(group,match_data["sport"])
            sportLink = self.create_sync_object("sport",sport,match_data["sport"]["object_type"],match_data["sport"]["object_uuid"])
        # The teams next:
        teams  = {}
        for key in match_data["teams"]:
            teamLink = self.find_sync_object("team", match_data["teams"][key]["object_type"],match_data["teams"][key]["object_uuid"])
            if teamLink:
                team = teamLink.team
            else:
                team = self.create_team(match_data["teams"][key],sport)
                teamLink = self.create_sync_object("team", team,match_data["teams"][key]["object_type"],match_data["teams"][key]["object_uuid"])
            teams[key] = [team,teamLink]
        # Finally, the season:
        seasonLink = self.find_sync_object("season", match_data["season"]["object_type"],
                                          match_data["season"]["object_uuid"])
        if seasonLink:
            season = seasonLink.season
        else:
            season = self.create_sports_season(match_data["season"])
            seasonLink = self.create_sync_object("season", sport, match_data["season"]["object_type"],
                                                match_data["season"]["object_uuid"])

        # And now, make the match:
        try:
            sys_MatchObj,cc = self.models.Match.objects.get_or_create(
                vhost=self.vhost,
                id=match_data["match"]["id"],
                routing_key=match_data["match"]["routing_key"],
                name=match_data["match"]["name"],
                home_team=teams['home'][0],
                away_team=teams['away'][0],
                sport=sport,
                season=season,
                commence_time=match_data["match"]["commence_time"]
            )

        except IntegrityError:
            sys_MatchObj = self.models.Match.objects.get(vhost=self.vhost,routing_key=match_data["match"]["routing_key"])

        sys_MatchObj.save()
        matchLink = self.create_sync_object("match",sys_MatchObj,match_data["match"]["object_type"],match_data["match"]["object_uuid"])
        return sys_MatchObj,matchLink


    def create_and_sync_matches(self, **kwargs):
        # print(f"Sync Matches {kwargs}...")
        matches = self.auth_driver.get_matches(**kwargs)
        for match in matches:
            # print(match)
            # print("***************")
            sys_linkObj = self.find_sync_object("match",match["match"]["object_type"],match["match"]["object_uuid"])
            if not sys_linkObj:
                self.logger.info(f"Match {match['match']['id']} no link found - creating match.")
                matchObj,sys_linkObj = self.create_match(match)
            else:
                matchObj = sys_linkObj.match
            self._object_setattrs(matchObj, match["match"],rows=["apiid", "status_short", "status_long", "status_timer","clock","commence_time"])

            # Now for all non-authoritative drivers; let's find matches, if any:
            for curr_driver in self.drivers:
                find_args = {"commence_time":matchObj.commence_time}
                groupLink = self.find_sync_object("group", curr_driver.dbobj_name["group"],
                                               None,matchObj.sport.group)
                if not groupLink:
                    find_args["group_name"] = matchObj.sport.group.name
                    find_args["group_slug"] = matchObj.sport.group.slug
                else:
                    find_args["group_obj"] = groupLink.driver_object_uuid
                sportLink = self.find_sync_object("sport", curr_driver.dbobj_name["sport"],
                                               None,matchObj.sport)
                if not sportLink:
                    find_args["sport_name"] = matchObj.sport.title
                    find_args["sport_key"] = matchObj.sport.key
                else:
                    find_args["sport_obj"] = sportLink.driver_object_uuid
                htLink = self.find_sync_object("team", curr_driver.dbobj_name["team"],None,matchObj.home_team)
                atLink = self.find_sync_object("team", curr_driver.dbobj_name["team"],None,matchObj.away_team)
                if not htLink:
                    find_args["home_team_name"] = matchObj.home_team.name
                    find_args["home_team_key"] = matchObj.home_team.key
                else:
                    find_args["home_team_obj"] = htLink.driver_object_uuid
                if not atLink:
                    find_args["away_team_name"] = matchObj.away_team.name
                    find_args["away_team_key"] = matchObj.away_team.key
                else:
                    find_args["away_team_obj"] = atLink.driver_object_uuid
                success,data = curr_driver.find_match(**find_args)
                # print(kwargs)
                if success:
                    # Gotta setup sync updates:
                    home_team_sync = self.create_sync_object("team",matchObj.home_team,curr_driver.dbobj_name["team"],data["home_team"]["object_uuid"])
                    away_team_sync = self.create_sync_object("team", matchObj.away_team,curr_driver.dbobj_name["team"],data["away_team"]["object_uuid"])
                    if "sport" in data:
                        sport_team_sync = self.create_sync_object("sport",matchObj.sport,curr_driver.dbobj_name["sport"],data["sport"]["object_uuid"])
                    match_sync = self.create_sync_object("match",matchObj,curr_driver.dbobj_name["match"],data["match"]["object_uuid"])
                    self.logger.info(f"Linked Successfully: {matchObj} from {curr_driver}.")

    def get_secondary_fixture_updates(self):
        self.logger.info(f"Starting Secondary Fixture updates since last run: {self.last_update}")
        for curr_driver in self.drivers:
            # print(curr_driver)
            matches = curr_driver.get_updated_synced_matches_index(self.last_update)
            for match in matches:
                # print(match)
                sys_linkObj = self.find_sync_object("match",curr_driver.dbobj_name["match"],match["object_uuid"])
                if sys_linkObj:
                    # print("Link!!!")
                    matchObj = sys_linkObj.match
                    # print(matchObj)
                    self.logger.info(f"Updating Secondary Provider Data for {curr_driver} and match {matchObj}")
                    self.get_match_outcomes(matchObj)
                # else:
                #     print("No Link?!")

                    # print("**********")


    def get_match_outcomes(self,matchObj,**kwargs):
        self.logger.info(f"Getting Match Outcomes for {matchObj}...")
        print(f"Getting Match Outcomes for {matchObj.uuid}...")
        for curr_driver in [self.auth_driver]+self.drivers:
            match_links = self.find_sync_objects("match", curr_driver.dbobj_name["match"],matchObj)
            for match_link in match_links:
                # print(match_link)
                outcomes = curr_driver.get_outcomes(provider_match_uuid=match_link.driver_object_uuid)
                for outcome in outcomes:
                    # print(outcome)
                    for key in ["status_short","status_long","is_current","is_start_game","is_end_game","is_start_segment","is_end_segment","clock","finished"]:
                        if key in outcome:
                            setattr(matchObj,key,outcome[key])
                            # print(f'Keyout {key}: {outcome[key]}')

                    outcomeObj = self.create_and_update_outcome(matchObj,match_link.driver_object_type,outcome)
                    for segment in outcome["segments"]:
                        teamObj = self.find_sync_object("team",curr_driver.dbobj_name["team"],segment["team_uuid"])
                        if teamObj:
                            segmentObj = self.create_and_update_outcome_segment(outcomeObj,teamObj.team,match_link.driver_object_type,segment)
                        # print(teamObj)
                        # print("****")
                    for team in outcome["teams"]:
                        teamObj = self.find_sync_object("team", curr_driver.dbobj_name["team"],team["team_uuid"])
                        if teamObj:
                            teamOutcomeObj = self.create_and_update_outcome_team(outcomeObj,teamObj.team,match_link.driver_object_type,team)
                    outcomeObj.save()
        if matchObj.status_short in GRADER_MATCH_FINISHED_STATUS_SHORT:
            matchObj.finished = True
        elif matchObj.status_long in GRADER_MATCH_FINISHED_STATUS_LONG:
            matchObj.finished = True
        matchObj.save()



        # print("--------------")

    def update_match_markets(self, matchObj, **kwargs):
        match_links = self.find_sync_objects("match", self.auth_driver.dbobj_name["match"],matchObj)
        for match_link in match_links:
            markets = self.auth_driver.get_match_odds_ml(provider_match_uuid=match_link.driver_object_uuid)
            # print(markets)
            for market in markets:
                marketObj = self.create_and_update_ml_odds_summary(match_link.match,self.auth_driver.dbobj_name["mkt_summary"],market)
                # print(marketObj)


    def update_all_match_outcomes(self,**kwargs):
        _matchObjs = self.models.Match.objects.filter(vhost=self.vhost,active=True,finished=False)
        if "after_time" in kwargs:
            _matchObjs = _matchObjs.filter(updated__gte=kwargs["after_time"])
        for matchObj in _matchObjs:
            self.get_match_outcomes(matchObj,**kwargs)

    def update_all_markets(self,**kwargs):
        _matchObjs = self.models.Match.objects.filter(vhost=self.vhost,active=True,finished=False)
        if "after_time" in kwargs:
            _matchObjs = _matchObjs.filter(updated__gte=kwargs["after_time"])
        for matchObj in _matchObjs:
            self.update_match_markets(matchObj, **kwargs)


    def test(self):
        self.logger.info("Started DataEngineV2")
        print(self.auth_driver)
        print("***************")
        print(self.drivers)
        print("***************")
        # self.create_and_sync_matches()
        # self.update_all_match_outcomes()
        self.update_all_markets()

    def full_run(self):
        if self.last_update:
            qwk = {"after_time":self.last_update}
        else:
            qwk = {}
        self.create_and_sync_matches(**qwk)


        if self.last_update:
            qwk = {"updated__gte":self.last_update,"vhost":self.vhost,"active":True,"finished":False}
        else:
            qwk = {"vhost":self.vhost,"active":True,"finished":False}
            self.last_update = localtime()
        self.get_secondary_fixture_updates()
        _matchObjs = self.models.Match.objects.filter(**qwk)
        for matchObj in _matchObjs:
            self.update_match_markets(matchObj)
            self.get_match_outcomes(matchObj)
            matchObj.last_update = localtime()
            matchObj.save()
        self.last_update = localtime()


    def run(self):

        try:
            while not self._stop_event.is_set():
                try:
                    self.logger.info("Synchronising data...")
                    self.full_run()
                except Exception as e:
                    self.logger.exception(f"Data Engine Sync run failed: {e}")
                print("Sync done")
                self.logger.info(f"Sleeping {self.interval_between_runs}s")
                self._stop_event.wait(self.interval_between_runs)

        except Exception as e:
            self.logger.exception(f"Fatal error in {self.__class__.__name__}: {e}")
        finally:
            self.logger.info(f"{self.__class__.__name__} shutting down")

