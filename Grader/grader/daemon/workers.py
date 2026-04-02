import copy
import importlib
import json
import time
from abc import ABC
from logging import getLogger
from threading import Thread
from multiprocessing import Process, Queue
from uuid import UUID

from django.db import connections
from django.db.models import Q
from django.utils.timezone import localtime

from grader.daemon.const import GRADER_DAEMON_BASICWAGER_MODULES, GRADER_DAEMON_OUTCOME_FILTER_Q, \
    GRADER_MATCH_FINISHED_STATUS_SHORT, GRADER_MATCH_FINISHED_STATUS_LONG
from outcomes.engine import OutcomesEngine
from outcomes.models import Outcome
from wager.models import Wager


class MatchWorkerThread(Thread):
    vhost = None
    verbose = False
    logger = False
    matches = []
    wagers = []
    kwargs = []
    modules = {}

    def __init__(self, vhost,logger,**kwargs):
        self.kwargs = copy.deepcopy(kwargs)
        self.vhost = vhost
        self.logger = logger
        self.outcomeEngine = OutcomesEngine(vhost=vhost)
        if "matchObjs" in kwargs:
            self.matches = kwargs["matchObjs"]
        if "wagerObjs" in kwargs:
            self.wagers = kwargs["wagerObjs"]

        for key in self.kwargs.keys():
            if key not in ['group','target','name','args','kwargs','daemon']:
                del kwargs[key]
        Thread.__init__(self, **kwargs)
    def match_upd_by_outcome(self,matchObj,**kwargs):
        matchOutcomes = self.outcomeEngine.get_final_scores(matchObj)
        match_ended = False
        data = []
        driver = None
        home_score = 0
        away_score = 0
        for driver,data in matchOutcomes.items():
            # print(data["score"])
            # First make sure the match has ended:
            if "status_short" in data["status"] and data["status"]["status_short"] != None:
                if data["status"]["status_short"] in GRADER_MATCH_FINISHED_STATUS_SHORT:
                    match_ended = True
            elif "status_long" in data["status"] and data["status"]["status_long"] != None:
                if data["status"]["status_long"] in GRADER_MATCH_FINISHED_STATUS_LONG:
                    match_ended = True
            elif "is_end_game" in data["status"]:
                if data["status"]["is_end_game"] == True:
                    match_ended = True
            if match_ended and "score" in data:
                score = data["score"]
                matchObj.in_play = False
                matchObj.scoring_data = score
                if score["home"] >= home_score:
                    home_score = score["home"]
                if score["away"] >= away_score:
                    away_score = score["away"]
        # Final Computations:
        if not match_ended:
            return False
        if home_score > away_score:
            # print("Greater Than")
            matchObj.winner = matchObj.home_team
        elif home_score < away_score:
            matchObj.winner = matchObj.away_team
        elif home_score ==  away_score:
            matchObj.draw = True
            matchObj.scoring_data["draw"] = True
        matchObj.active = False
        matchObj.score_closed = True
        self.logger.info(f"Match Ended: {matchObj.uuid}")
        self.logger.info(f"Winner {matchObj.winner}")
        matchObj.save()
        self.logger.info(f"Match {matchObj.uuid} declared final in driver {driver}")
        # print(score)
        return match_ended

    def run(self):
        if len(self.matches) > 0:
            self.logger.info(f"Starting worker thread: For {len(self.matches)} matches...")
            for matchObj in self.matches:
                # print(matchObj)
                if self.verbose:
                    self.logger.info(f"Grading Match: {matchObj.uuid}...")
                self.match_upd_by_outcome(matchObj)


        connections.close_all()
        self.logger.info("Match Thread Completed.")
class GraderWorkerThread(Thread):
    vhost = None
    verbose = False
    logger = False
    wagers = []
    kwargs = []
    modules = {}

    def __init__(self, vhost,logger,**kwargs):
        self.kwargs = copy.deepcopy(kwargs)
        self.vhost = vhost
        self.logger = logger
        self.outcomeEngine = OutcomesEngine(vhost=vhost)
        if "wagerObjs" in kwargs:
            self.wagers = kwargs["wagerObjs"]

        for key in self.kwargs.keys():
            if key not in ['group','target','name','args','kwargs','daemon']:
                del kwargs[key]
        Thread.__init__(self, **kwargs)



    def _load_wager_module(self,wagerObj):
        # Default to Application grader if enabled!
        module = False
        if wagerObj.application_type:
            if wagerObj.application_type.grader:
                module = wagerObj.application_type.grader
        # Not found? Okay. Try the default types:
        if not module:
            if wagerObj.type in GRADER_DAEMON_BASICWAGER_MODULES.keys():
                module = GRADER_DAEMON_BASICWAGER_MODULES[wagerObj.type]
        if not module:
            self.logger.warning(f"Unable to find module for Wager {wagerObj.uuid}, Application type {wagerObj.application_type} - Wager Type: {wagerObj.type}")
            return False
        # Don't import twice:
        if module in self.modules.keys():
            return self.modules[module]
        else:
            grader_module = importlib.import_module(module)
            self.modules[module] = grader_module.GRADER_MODULE(self.vhost,**self.kwargs)
            self.modules[module].logger = self.logger
            return self.modules[module]


    def _grade(self, wagerObj, matchObj, **kwargs):
        module = self._load_wager_module(wagerObj)
        if not module:
            self.logger.warning(f"No module found; cannot qualify wager {wagerObj.uuid}")
            return False
        return module.grade_wager(wagerObj,matchObj,**kwargs)



    def run(self):
        if len(self.wagers) > 0:
            self.logger.info(f"Starting worker thread: For {len(self.wagers)} wagers...")
            total_wagers = len(self.wagers)
            qualified = 0
            for wager in self.wagers:
                self.logger.info(f"Grading Wager {wager.uuid} in match {wager.match.uuid}...")
                result = self._grade(wager, wager.match)
        self.logger.info(" Wager Thread Completed.")
        connections.close_all()
        return True