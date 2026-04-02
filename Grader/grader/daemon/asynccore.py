import asyncio
import importlib
import itertools
import math
import multiprocessing
import time
import traceback
from types import SimpleNamespace

from asgiref.sync import sync_to_async
from django.core.exceptions import ValidationError
from django.db import connections, close_old_connections
from django.db.models import Q, Exists, OuterRef
from django.forms import model_to_dict
from django.utils.timezone import localtime


from asynctools.abc import AsyncWorkerABC


from grader.daemon.const import GRADER_MATCH_FINISHED_STATUS_SHORT, GRADER_MATCH_FINISHED_STATUS_LONG, \
    GRADER_DAEMON_BASICWAGER_MODULES_ASYNC



class AsyncGraderDaemon(AsyncWorkerABC):
    def __init__(self, vhost=None, logger=None, name: str = "worker", interval: float = 120,
                 run_in_process: bool = True,loki_url=None,):
        AsyncWorkerABC.__init__(self, vhost, logger, name, interval, run_in_process,loki_url,)

    debug = False
    verbose = False
    module_kwargs = {}
    modules = {}
    def _child_init(self):
        """
        Runs inside the forked child *after* django.setup().
        Safe place for model imports.
        """
        super()._child_init()

        from matches.models import Match
        from outcomes.models import OutcomeFinalMatchScores
        from wager.models import Wager
        from account.models import Account
        from cashier.engine import Cashier
        from parameters.models import Timezone, VHostParameterRegistry
        self.last_timestamp = localtime()
        self.models = SimpleNamespace(
            Match=Match,
            OutcomeFinalMatchScores=OutcomeFinalMatchScores,
            Wager=Wager,
            Account=Account,
            Timezone=Timezone,
            VHostParameterRegistry=VHostParameterRegistry,
        )
        self.Cashier = Cashier

    def find_wager_nodes(self,wagerObj):
        nodes = []
        if "root_wager" in wagerObj.bet_data:
            root = wagerObj
        elif "parent" in wagerObj.bet_data:
            try:
                root = self.models.Wager.objects.get(uuid=wagerObj.bet_data["parent"])
            except self.models.Wager.DoesNotExist:
                print("KILL MEE WITH FIRE", wagerObj.bet_data["parent"], wagerObj.uuid)

        nodes.append(root)
        for _node in root.bet_data["nodes"]:
            try:
                nodeObj = self.models.Wager.objects.get(uuid=_node)
                nodes.append(nodeObj)
            except self.models.Wager.DoesNotExist:
                pass
        return nodes

    def _ungrade_wager(self, wagerObj, **kwargs):
        if not wagerObj.grade_outcome:
            self.logger.info(f"Wager {wagerObj.uuid} doesn't have a grade outcome.")
            return False
        nodes = self.find_wager_nodes(wagerObj)

        if wagerObj.status in ["W","L"]:
            cashier = Cashier(vhost=self.vhost, account=wagerObj.account)
            cashier.rollback_wager(wagerObj)
        risk_adj = wagerObj.risk
        bal_adj = 0
        if wagerObj.grade_outcome == "W":
            bal_adj = -wagerObj.win
        for node in nodes[1:]:
            node.grade_outcome = None
            node.status = "P"
            node.graded_at = None
            node.graded = False
            node.executed = False
            node.closed = False
            node.save()
            self.logger.info(f"Ungraded Node Wager {node.uuid}:{node.status}")
        wagerObj.grade_outcome = None
        wagerObj.status = "P"
        wagerObj.graded_at = None
        wagerObj.graded = False
        wagerObj.executed = False
        wagerObj.closed = False
        wagerObj.save()
        self.logger.info(f"Ungraded Root Wager {wagerObj.uuid}")
        return bal_adj,risk_adj

    async def _ungrade_match(self,matchObj,**kwargs):
        wagerObjects = await sync_to_async(list, thread_sensitive=False)(self.models.Wager.objects.filter(vhost=self.vhost,match=matchObj).filter( Q(grade_outcome__isnull=False) | Q(grade_outcome__in=["W", "L"])))
        for wagerObj in wagerObjects:
            acct = await sync_to_async(lambda:wagerObj.account,thread_sensitive=False)()
            cashier = self.Cashier(vhost=self.vhost, account=acct)
            await sync_to_async(self._ungrade_wager, thread_sensitive=False)(wagerObj, cashier)
        matchObj.wagers_graded = False
        matchObj.wagers_paid = False
        matchObj.winner = None
        matchObj.score = None
        matchObj.score_closed = False
        await sync_to_async(lambda: matchObj.save(), thread_sensitive=False)()
        self.logger.info(f"Ungraded Match {matchObj.uuid}")


    async def _ungrade_account_wagers(self, account, start, stop):
        wagerObjects = await sync_to_async(list, thread_sensitive=True)(
            self.models.Wager.objects.filter(
                vhost=self.vhost,
                account=account,
                graded_at__gte=start,
                graded_at__lte=stop,
                grade_outcome__in=["W", "L"],
                hide_in_reports=False,
            ))


        async def _run_ungrade(wager):
            try:
                return await sync_to_async(
                    self._ungrade_wager, thread_sensitive=True
                )(wager)
            except Exception:
                try:
                    wuuid = await sync_to_async(lambda: wager.uuid, thread_sensitive=True)()
                except Exception:
                    wuuid = "<unknown>"
                self.logger.error(
                    f"[grade_wagers] exception ungrading wager {wuuid}",
                    exc_info=True,
                )
                raise

        # run all ungrade operations concurrently
        results = await asyncio.gather(
            *(_run_ungrade(wager) for wager in wagerObjects)
        )

        # results is a list of (bal_adj, risk_adj)
        total_bal_adj = sum(bal for bal, _ in results)
        total_risk_adj = sum(risk for _, risk in results)
        total_ungrades = len(results)

        self.logger.info(
            f"Finished UnGrading Wagers!: Total {total_ungrades}."
            f"bal_adj={total_bal_adj}, risk_adj={total_risk_adj}"
        )
        cashier = self.Cashier(vhost=self.vhost, account=account)
        await sync_to_async(lambda:cashier.set_risk_bal(),thread_sensitive=True)()
        # balance_obj = await sync_to_async(lambda:cashier.get_balance_obj())()
        # balance_obj.available += total_bal_adj
        # balance_obj.at_risk += total_risk_adj
        # await sync_to_async(lambda:balance_obj.save(),thread_sensitive=False)()



    async def match_close_and_finish(self, matchObj, **kwargs):
        muuid = await sync_to_async(lambda: matchObj.uuid, thread_sensitive=False)()
        # print(type(matchObj))
        match_data = await sync_to_async(lambda: SimpleNamespace(**model_to_dict(matchObj)), thread_sensitive=False)()
        # if muuid == "a6c58f5d-eae0-4bc1-9cc3-bffcd8a6ef26":
        #     print(match_data)
        self.logger.info(f"Evaluating Match {muuid} for CnF")
        if match_data.wagers_graded:
            if self.verbose:
                self.logger.warn(
                    f"Match {muuid} has already had wagers qualified! Cowardly refusing to qualify.")
            return False
        if match_data.wagers_paid:
            if self.verbose:
                self.logger.warn(
                    f"Match {muuid} has already had wagers paid out! Cowardly refusing to qualify.")
            return False
        if match_data.in_play:
            if self.verbose:
                self.logger.warn(f"Match {muuid} is still in-play! Can't qualify match wagers!")
            return False
        if not match_data.finished:
            if self.verbose:
                self.logger.warn(f"Match {muuid} has not finished yet: Cowardly refusing to qualify.")
            return False
        try:
            finalMatchScores = await sync_to_async(lambda:self.models.OutcomeFinalMatchScores.objects.get(vhost=self.vhost,match=matchObj),thread_sensitive=False)()
        except self.models.OutcomeFinalMatchScores.DoesNotExist:
            if self.debug:
                if self.verbose:
                    self.logger.info(f"Match {muuid}: No OutcomeFinalMatchScores found - will not qualify.")
            return False
        except self.models.OutcomeFinalMatchScores.MultipleObjectsReturned:
            finalMatchScores = await sync_to_async(
                lambda: self.models.OutcomeFinalMatchScores.objects.filter(vhost=self.vhost, match=matchObj).first(),
                thread_sensitive=False)()
        matchObj.open = False
        if finalMatchScores.draw:
            matchObj.scoring_data = {"draw": True}
            matchObj.active = False
            matchObj.score_closed = True
            matchObj.draw = True
            matchObj.winner = None
            await sync_to_async(lambda: matchObj.save(),thread_sensitive=False)()
            self.logger.info(f"Match {muuid}: is a DRAW!")
            return True
        if finalMatchScores.home_team_score > finalMatchScores.away_team_score:
            matchObj.winner = await sync_to_async(lambda: matchObj.home_team, thread_sensitive=False)()
        else:
            matchObj.winner = await sync_to_async(lambda: matchObj.away_team, thread_sensitive=False)()
        matchObj.scoring_data = f"{finalMatchScores.home_team_score}-{finalMatchScores.away_team_score}"
        matchObj.score_closed = True
        winner_name = await sync_to_async(lambda: matchObj.winner.name, thread_sensitive=False)()
        self.logger.info(f"Match Ended: {muuid} Winner {winner_name}")
        await sync_to_async(lambda: matchObj.save(),thread_sensitive=False)()
        return True

    async def _load_wager_module(self, wagerObj):
        # Default to Application grader if enabled!
        module = False
        application_type = await sync_to_async(lambda: wagerObj.application_type, thread_sensitive=False)()
        wager_type = await sync_to_async(lambda: wagerObj.type, thread_sensitive=False)()
        if application_type:
            if application_type.grader:
                module = application_type.grader
        # Not found? Okay. Try the default types:
        if not module:
            if wager_type in GRADER_DAEMON_BASICWAGER_MODULES_ASYNC.keys():
                module = GRADER_DAEMON_BASICWAGER_MODULES_ASYNC[wager_type]
        if not module:
            wuuid = await sync_to_async(lambda:wagerObj.uuid, thread_sensitive=False)()
            self.logger.warning(f"Unable to find module for Wager {wuuid}, Application type {application_type} - Wager Type: {wager_type}")
            return False
        # Dont Import Twice:
        if module in self.modules.keys():
            return self.modules[module],module
        else:
            grader_module = importlib.import_module(module)
            self.modules[module] = grader_module.GRADER_MODULE(self.vhost, **self.module_kwargs)
            self.modules[module].logger = self.logger
            self.modules[module].debug = self.debug
            self.modules[module].verbose = self.verbose
            return self.modules[module],module

    async def grade_and_close_wager(self, wagerObj, **kwargs):
        module,modname = await self._load_wager_module(wagerObj)
        wuuid = await sync_to_async(lambda:wagerObj.uuid, thread_sensitive=False)()

        if not module:
            self.logger.warning(f"No module found; cannot qualify wager {wuuid}")
            return False
        if self.debug:
            self.logger.info(f"Grading Wager {wuuid}: Using Module module {modname}...")

        result = await module.grade_wager(wagerObj, **kwargs)
        self.logger.info(f"Graded Wager {wuuid}!")
        return result

    async def grade_matches(self):
        mOrm = self.models.Match.objects.filter(final_score_consensus=True,finished=True, score_closed=False,vhost=self.vhost)
        matchObjects = await sync_to_async(list, thread_sensitive=False)(mOrm)


        async def handler(m):
            return await self.match_close_and_finish(m)

        await self.run_in_batches(
            matchObjects,
            handler,
            batch_size=50,
            label="grade_matches"
        )
        self.logger.info("Finished Grading Matches!")
        return True

    async def grade_wagers(self):
        wagerObjects = await sync_to_async(list, thread_sensitive=False)(
            self.models.Wager.objects.filter(vhost=self.vhost, match__finished=True, match__score_closed=True,graded=False).exclude(status='C')
        )
        if self.debug:
            self.logger.info(f"Grading {len(wagerObjects)} Wagers!")
        async def handler(w):
            # wrap to ensure any exception gets full logging context (uuid included)
            try:
                return await self.grade_and_close_wager(w)
            except Exception:
                try:
                    wuuid = await sync_to_async(lambda: w.uuid, thread_sensitive=False)()
                except Exception:
                    wuuid = "<unknown>"
                self.logger.error(f"[grade_wagers] exception grading wager {wuuid}", exc_info=True)
                raise

        await self.run_in_batches(
            wagerObjects,
            handler,
            batch_size=50,
            label="grade_wagers"
        )
        self.logger.info("Finished Grading Wagers!")
        return True

    def execute_account_wagers(self,account):
        wagers = self.models.Wager.objects.filter(
                vhost=self.vhost,
                match__finished=True, match__score_closed=True,
                graded=True, executed=False,
                bet_data__root_wager=True,
                grade_outcome__isnull=False,
                hide_in_reports=False,
                account=account,
            )
        self.logger.info(f"Executing {len(wagers)} Wagers for  Account {account.uuid}...")
        cashier = self.Cashier(vhost=self.vhost, account=account)
        for wager in wagers:
            if self.debug:
                if self.verbose:
                    self.logger.info(f"Executing Wager {wager.uuid}...")
            wager.execute_close(cashier)
        # cashier.set_risk_bal()
        self.logger.info("Finished Executing Cashier!")
        return True


    async def ungrade_wagers(self,start,stop):
        wagers_subquery = self.models.Wager.objects.filter(vhost=self.vhost,account=OuterRef('pk')).filter(graded_at__gte=start,graded_at__lte=stop).filter(Q(grade_outcome__isnull=False)|Q(grade_outcome__in=["L","W"]))
        # Filter accounts that have at least one matching wager - process one account at the time for Cashier  balancing purposes
        accounts_with_matching_wagers = await sync_to_async(lambda:list(self.Account.objects.annotate(
            has_wager=Exists(wagers_subquery)
        ).filter(has_wager=True)),thread_sensitive=False)()
        for account in accounts_with_matching_wagers:
            await self._ungrade_account_wagers(account,start,stop)
        self.logger.info("Finished Ungrading Wagers!")
        return True

    async def ungrade_matches(self,start,stop):
        matchObjs = await sync_to_async(lambda:list(self.models.Match.objects.filter(finished=True, vhost=self.vhost,commence_time__gte=start,commence_time__lte=stop).all()),thread_sensitive=False)()
        for matchObj in matchObjs:
            await self._ungrade_match(matchObj)
        self.logger.info("Finished Ungrading Matches!")
        return True

    async def execute_wagers(self):

        wagers_subquery = self.models.Wager.objects.filter(
            account=OuterRef('pk'),
            vhost=self.vhost,
            match__finished=True,
            match__score_closed=True,
            graded=True,
            executed=False,
            bet_data__root_wager=True,
            grade_outcome__isnull=False,
            hide_in_reports=False,
        )

        # Filter accounts that have at least one matching wager - process one account at the time for Cashier  balancing purposes
        accounts_with_matching_wagers = await sync_to_async(lambda:list(self.models.Account.objects.annotate(
            has_wager=Exists(wagers_subquery)
        ).filter(has_wager=True)),thread_sensitive=False)()
        for account in accounts_with_matching_wagers:
            await sync_to_async(self.execute_account_wagers,thread_sensitive=False)(account)
        self.logger.info("Finished Executing Wagers!")
        return True

    def exec_account_rebalance(self,account):
        cashier = self.Cashier(vhost=self.vhost, account=account)
        cashier.set_risk_bal()
        if self.debug:
            self.logger.info(f"Executed Rebalance for {account.uuid}/{account.acctnum}!")

    async def rebalance_accounts_risk(self):
        accountObjs = await sync_to_async(lambda:list(self.models.Account.objects.filter(vhost=self.vhost)),thread_sensitive=False)()
        for account in accountObjs:
            self.logger.info(f"Executing Rebalance for {account.uuid}/{account.acctnum}...")
            await sync_to_async(self.exec_account_rebalance, thread_sensitive=False)(account)
        if self.debug:
            self.logger.info("Finished Rebalancing Accounts!")
        return True


    async def _work_cycle(self):
        # run each stage; allow exceptions to bubble so they show up in logs and stop the cycle
        await self.grade_matches()
        await self.grade_wagers()
        await self.execute_wagers()
        await self.rebalance_accounts_risk()
        self.last_timestamp = localtime()
        await sync_to_async(lambda: close_old_connections(), thread_sensitive=False)()
        self.logger.info(f"Async Grader Tick.")
