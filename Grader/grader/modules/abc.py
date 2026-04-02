from abc import ABC, abstractmethod

from grader.daemon.const import GRADER_MATCH_FINISHED_STATUS_SHORT
from wager.models import Wager
from logging import getLogger

class GraderModuleABC(ABC):
    vhost = False
    logger = None
    debug = False

    def _find_parlay_nodes(self,wagerObj):
        """
        Return the entire set of nodes composing a parlay wager. The Root node is always the first member of the dict.
        :param wagerObj: Wager Object to work on
        :return:  List of nodes composing the parlay wager.
        """
        nodes = []
        if "root_wager" in wagerObj.bet_data:
            root = wagerObj
        elif "parent" in wagerObj.bet_data:
            try:
                root = Wager.objects.get(uuid=wagerObj.bet_data["parent"])
            except Wager.DoesNotExist:
                print("KILL MEE WITH FIRE",wagerObj.bet_data["parent"],wagerObj.uuid)

        nodes.append(root)
        for _node in root.bet_data["nodes"]:
            try:
                nodeObj = Wager.objects.get(uuid=_node)
                nodes.append(nodeObj)
            except Wager.DoesNotExist:
                pass
        return nodes

    def _check_wager_stat(self,wagerObj):
        # Is this even needed?
        # if wagerObj.match.status_short  not in GRADER_MATCH_FINISHED_STATUS_SHORT or not wagerObj.match.finished:
        #     self.logger.warning(f"Match: {wagerObj.match.uuid}  status is not FINAL: {wagerObj.match.status_short}/{wagerObj.match.status_long}")
        #     return False
        if wagerObj.executed:
            self.logger.warning(f"Wager has already been executed.")
            return False
        if wagerObj.closed:
            self.logger.warning(f"Wager is closed.")
            return False
        if wagerObj.cancelled:
            self.logger.warning(f"Wager has already been cancelled.")
            return False
        return True


    def __init__(self, vhost,**kwargs):
        self.vhost = vhost
        self.logger = getLogger(f"grader.modules.{self.__class__.__name__}")
        if "debug" in kwargs:
            self.debug = kwargs["debug"]

    @abstractmethod
    def _grade_wager_func(self, wagerObj, matchObj, **kwargs):
        pass

    @abstractmethod
    def _close_wager_func(self, wagerObj, matchObj, **kwargs):
        pass

    def grade_wager(self, wagerObj, matchObj, **kwargs):
        if "skip_status_check" not in kwargs:
            if not self._check_wager_stat(wagerObj):
                return None
        self.logger.info(f"Grading wager {wagerObj.uuid}...")
        qualify = self._grade_wager_func(wagerObj, matchObj, **kwargs)
        self.logger.info(f"...Results: {qualify}")
        self.logger.info(f"Closing wager {wagerObj.uuid}...")
        close = self._close_wager_func(wagerObj, matchObj, **kwargs)
        self.logger.info(f"...Close Results: {close}")
        return qualify,close

