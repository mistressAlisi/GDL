from abc import ABC, abstractmethod

from asgiref.sync import sync_to_async

from grader.daemon.const import GRADER_MATCH_FINISHED_STATUS_SHORT
from wager.models import Wager
from logging import getLogger

class GraderModuleABCAsync(ABC):
    vhost = False
    logger = None
    debug = False

    async def _find_parlay_nodes(self,wagerObj):
        """
        Return the entire set of nodes composing a parlay wager. The Root node is always the first member of the dict.
        :param wagerObj: Wager Object to work on
        :return:  List of nodes composing the parlay wager.
        """
        nodes = []
        root = False
        bet_data = await sync_to_async(lambda:wagerObj.bet_data,thread_sensitive=False)()
        if "root_wager" in bet_data:
            root = wagerObj
        elif "parent" in bet_data:
            try:
                root = await sync_to_async(lambda:Wager.objects.get(uuid=bet_data["parent"]),thread_sensitive=False)()
            except Wager.DoesNotExist:
                wuuid = await sync_to_async(wagerObj.wuuid,thread_sensitive=False)()
                self.logger.error(f"KILL MEE WITH FIRE: This WagerObj does not exist: {bet_data['parent']},{wuuid}")
        if not root: return False
        nodes.append(root)
        root_data = await sync_to_async(lambda:root.bet_data,thread_sensitive=False)()
        for _node in root_data["nodes"]:
            try:
                nodeObj =  await sync_to_async(lambda:Wager.objects.get(uuid=_node),thread_sensitive=False)()
                nodes.append(nodeObj)
            except Wager.DoesNotExist:
                pass
        return nodes

    def _find_parlay_nodes_sync(self,wagerObj):
        """
        Return the entire set of nodes composing a parlay wager. The Root node is always the first member of the dict.
        :param wagerObj: Wager Object to work on
        :return:  List of nodes composing the parlay wager.
        """
        nodes = []
        root = False
        bet_data = wagerObj.bet_data
        if "root_wager" in bet_data:
            root = wagerObj
        elif "parent" in bet_data:
            try:
                root = Wager.objects.using('default').get(uuid=bet_data["parent"])
            except Wager.DoesNotExist:
                wuuid = wagerObj.wuuid
                self.logger.error(f"KILL MEE WITH FIRE: This WagerObj does not exist: {bet_data['parent']},{wuuid}")
        if not root: return False
        nodes.append(root)
        root_data = root.bet_data
        for _node in root_data["nodes"]:
            try:
                nodeObj =  Wager.objects.using('default').get(uuid=_node)
                nodes.append(nodeObj)
            except Wager.DoesNotExist:
                pass
        return nodes

    async def _check_wager_stat(self,wagerObj):

        if await sync_to_async(lambda:wagerObj.executed,thread_sensitive=False)():
            self.logger.warning(f"Wager has already been executed.")
            return False
        if await sync_to_async(lambda:wagerObj.closed,thread_sensitive=False)():
            self.logger.warning(f"Wager is closed.")
            return False
        if await sync_to_async(lambda:wagerObj.cancelled,thread_sensitive=False)():
            self.logger.warning(f"Wager has already been cancelled.")
            return False
        return True


    def __init__(self, vhost,**kwargs):
        self.vhost = vhost
        self.logger = getLogger(f"grader.modules.{self.__class__.__name__}")
        if "debug" in kwargs:
            self.debug = kwargs["debug"]

    @abstractmethod
    async def _grade_wager_func(self, wagerObj, matchObj, **kwargs):
        pass

    @abstractmethod
    async def _close_wager_func(self, wagerObj, matchObj, **kwargs):
        pass

    async def grade_wager(self, wagerObj, **kwargs):
        if "skip_status_check" not in kwargs:
            if not await self._check_wager_stat(wagerObj):
                return None
        wuuid = await sync_to_async(lambda:wagerObj.uuid,thread_sensitive=False)()
        self.logger.info(f"Grading wager {wuuid}...")
        qualify = await self._grade_wager_func(wagerObj, **kwargs)
        self.logger.info(f"...Results: {qualify}")
        self.logger.info(f"Closing wager {wuuid}...")
        close = await self._close_wager_func(wagerObj, **kwargs)
        self.logger.info(f"...Close Results: {close}")
        return qualify,close

