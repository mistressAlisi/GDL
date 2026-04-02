from collections import Counter
from datetime import timedelta
from types import SimpleNamespace
from asgiref.sync import sync_to_async

from django.utils.timezone import localtime, now
from asynctools.abc import AsyncWorkerABC




# -------------------------
# Main Worker
# -------------------------
class AsyncConsensusDaemon(AsyncWorkerABC):
    verbose = False
    verbose_spam = False

    def __init__(self, vhost=None, logger=None, name: str = "ConsensusD", interval: float = 120,
                 run_in_process: bool = True,loki_url=None,):
        AsyncWorkerABC.__init__(self, vhost, logger, name, interval, run_in_process, loki_url)

    def _child_init(self):
        """
        Runs inside the forked child *after* django.setup().
        Safe place for model imports.
        """
        super()._child_init()
        from matches.models import Match
        from outcomes.models import Outcome, OutcomeFinalMatchScores, OutcomeTeamsLatestScoreView, OutcomeSegmentScore
        from dataengine.drivers.apisports.models import BABGame, BASEGame, HOCKGame, AMFGame, FBALLGame
        from dataengine.drivers.goalserve.models import BasketBallFixture, BaseBallFixture, HockeyFixture, \
            SoccerFixture, \
            AmericanFBallFixture
        from dataengine.drivers.kiblio.models import Fixture
        from dataengine.models import MatchSyncStatus
        from dataengine.drivers.apitennis.models.fixtures import Fixture as TennisFixture

        self.last_timestamp = localtime()
        self.models = SimpleNamespace(
            Match=Match,
            Outcome=Outcome,
            OutcomeFinalMatchScores=OutcomeFinalMatchScores,
            OutcomeTeamsLatestScoreView=OutcomeTeamsLatestScoreView,
            OutcomeSegmentScore=OutcomeSegmentScore,
            BABGame=BABGame,
            BASEGame=BASEGame,
            HOCKGame=HOCKGame,
            AMFGame=AMFGame,
            FBALLGame=FBALLGame,
            BasketBallFixture=BasketBallFixture,
            BaseBallFixture=BaseBallFixture,
            HockeyFixture=HockeyFixture,
            SoccerFixture=SoccerFixture,
            AmericanFBallFixture=AmericanFBallFixture,
            Fixture=Fixture,
            MatchSyncStatus=MatchSyncStatus,
            TennisFixture=TennisFixture
        )
        self.DRIVER_TABLE = {
            # "kiblio.fixture.Fixture":Fixture,
            "apisports.match.babgame": BABGame,
            "apisports.match.basegame": BASEGame,
            "apisports.match.hockgame": HOCKGame,
            "apisports.match.amfgame": AMFGame,
            "apisports.match.fballgame": FBALLGame,
            "goalserve.match.basketballfixture": BasketBallFixture,
            "goalserve.match.baseballfixture": BaseBallFixture,
            "goalserve.match.hockgame": HockeyFixture,
            "goalserve.match.soccerfixture": SoccerFixture,
            "goalserve.match.amfgame": AmericanFBallFixture,
            "goalserve.match.TennisFixture": TennisFixture,
            "apitennis.fixture.Fixture":TennisFixture,
        }

    # -------------------------
    # Consensus helpers
    # -------------------------
    def has_consensus(self, values, threshold=2, target=None):
        """
        Returns:

        - If target is provided:
            * target if its count >= threshold
            * None otherwise

        - If target is None:
            * the value that reached consensus (count >= threshold)
            * list of values if multiple reached consensus
            * None if no consensus
        """

        counts = Counter(values)

        # ───── Specific-value consensus check ─────
        if target is not None:
            return target if counts.get(target, 0) >= threshold else None

        # ───── Generic consensus ─────
        consensus = [val for val, count in counts.items() if count >= threshold]

        if not consensus:
            return None
        if len(consensus) == 1:
            return consensus[0]
        return consensus
    # -------------------------
    # PPD detector
    # -------------------------
    def match_detect_and_declare_ppd(self,matchObj):
        if self.debug and self.verbose:
            self.logger.info(f"PPD detector function for Match {matchObj}")
        syncObjs = self.models.MatchSyncStatus.objects.using("default").filter(match=matchObj)
        status_short = []
        status_long = []
        for syncObj in syncObjs:
            if syncObj.driver_object_type in self.DRIVER_TABLE:
                try:
                    obj = self.DRIVER_TABLE[syncObj.driver_object_type].objects.using("default").get(uuid=syncObj.driver_object_uuid)
                except self.DRIVER_TABLE[syncObj.driver_object_type].DoesNotExist:
                    return False
                if hasattr(obj,"status_short"):
                    status_short.append(obj.status_short)
                    status_long.append(obj.status_long)
                elif hasattr(obj,"status"):
                    status_short.append(obj.status)
                    status_long.append(obj.status)
                elif hasattr(obj,"state"):
                    status_short.append(obj.state)
                    status_long.append(obj.state)
        is_ppd = self.has_consensus(status_short,target="PPD")
        is_canceled = self.has_consensus(status_short,target="CANC")
        if is_ppd or is_canceled:
            if is_ppd:
                matchObj.status_short = "PPD"
                matchObj.status_long = "Postponed"
            if is_canceled:
                matchObj.status_short = "CANC"
                matchObj.status_long = "Cancelled"
            matchObj.final_score_consensus = True
            matchObj.finished = True
            matchObj.save()
            self.logger.info(f"Consensus Reached!! {matchObj.uuid} → Status {matchObj.status_short}")
            return True
        else:
            return False





    # -------------------------
    # Consensus builder
    # -------------------------
    def match_build_consensus(self, matchObj):
        from dataengine.consensus.daemon.builder import consensus_build_data_table
        consensus_table = consensus_build_data_table(matchObj)
        if self.verbose:
            self.logger.info(f"Attempting to Build Consensus for Match {matchObj.uuid}...")
            if self.verbose_spam:
                self.logger.info(f"Consensus table: {consensus_table}")


        home_scores = []
        away_scores = []
        statuses = []
        for driver in consensus_table:
            if consensus_table[driver]["home_score"] is not None and consensus_table[driver]["home_score"] > -1:
                home_scores.append(consensus_table[driver]["home_score"])


            if consensus_table[driver]["away_score"] is not None and consensus_table[driver]["away_score"] > -1:
                away_scores.append(consensus_table[driver]["away_score"])
            statuses.append(consensus_table[driver]["status_long"])
            statuses.append(consensus_table[driver]["status_short"])
        home_score = self.has_consensus(home_scores)
        away_score = self.has_consensus(away_scores)
        if self.verbose:
            self.logger.info(f"Match: {matchObj.uuid}, {home_score}, {away_score}, {statuses}")
        if home_score != None and away_score != None:
            if home_score == away_score:
                draw = True
                winner = None
            elif home_score > away_score:
                winner = matchObj.home_team
                draw = False
            else:
                winner = matchObj.away_team
                draw = False

            ofMObj, _ = self.models.OutcomeFinalMatchScores.objects.using("default").get_or_create(
                vhost=matchObj.vhost,
                match=matchObj,
                home_team_score=home_score,
                away_team_score=away_score,
                draw=draw,
                winner=winner,
                consensus_data=consensus_table
            )
            ofMObj.save()
            matchObj.status_short = "FT"
            matchObj.status_long = "Finished"
            # print(statuses)
            for special in ["Cancelled", "Walk Over","Retired","Postponed","PPD","Canc"]:
                if special in statuses:
                    matchObj.status_short =  special
                    matchObj.status_long = special
            # print(matchObj.status_long)
            matchObj.final_score_consensus = True
            matchObj.finished = True
            matchObj.save()

            self.logger.info(f"Consensus Reached!! {matchObj.uuid} → Home {home_score}, Away {away_score}")


    async def _work_cycle(self):
        cutoff = now() - timedelta(days=10)
        cutoff_fut = now() + timedelta(days=3)
        matches = self.models.Match.objects.using("default").filter(vhost=self.vhost,  commence_time__gte=cutoff, commence_time__lte=cutoff_fut, final_score_consensus=False,manual_data=False)
        matchObjects = await sync_to_async(list, thread_sensitive=False)(matches)

        # Detect PPD and then Build consensus
        async def handler(m):
            dppd = await sync_to_async(self.match_detect_and_declare_ppd,thread_sensitive=False)(m)
            if dppd: return True
            return await sync_to_async(self.match_build_consensus, thread_sensitive=False)(m)

        await self.run_in_batches(
            matchObjects,
            handler,
            batch_size=50,
            label="match_build_consensus"
        )

        self.logger.info(f"{self.name} tick...")
