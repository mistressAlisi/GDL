import asyncio
from datetime import timedelta
from types import SimpleNamespace
from uuid import UUID

from asgiref.sync import sync_to_async
from django.db import IntegrityError
from django.db.models import Q, Exists, OuterRef, Func, Value, F, CharField
from django.db.models.functions import Lower
from django.contrib.postgres.search import TrigramSimilarity
from django.utils.timezone import now

from rapidfuzz import fuzz

from asynctools.abc import AsyncWorkerABC




FUZZ_RATIO_THRESHOLD = 65
FUZZ_PARTIAL_THRESHOLD = 75
SQL_TRIGRAM_THRESHOLD = 0.45


# ------------------------------------------------------------
# REGEXP REPLACE (Postgres)
# ------------------------------------------------------------
class RegexReplace(Func):
    function = "REGEXP_REPLACE"
    arg_joiner = ", "
    arity = 4


class AsyncTeamLinkerDaemon(AsyncWorkerABC):
    verbose = False

    def _child_init(self):
        """
        Runs inside the forked child *after* django.setup().
        Safe place for model imports.
        """
        super()._child_init()
        from teams.models import Team
        from dataengine.drivers.apisports.models import Team as APISportTeam
        from dataengine.drivers.apitennis.models.players import Players as APITennisPlayer
        from dataengine.drivers.goalserve.models.base import Team as GoalserveTeam
        from dataengine.drivers.kiblio.models.base import Participant as KiblioTeam
        from dataengine.models import TeamSyncStatus

        self.last_timestamp = now() - timedelta(seconds=1900)
        self.models = SimpleNamespace(
            Team=Team,
            APISportTeam=APISportTeam,
            APITennisPlayer=APITennisPlayer,
            GoalserveTeam=GoalserveTeam,
            KiblioTeam=KiblioTeam,
            TeamSyncStatus=TeamSyncStatus



        )
    # ------------------------------------------------------------
    # NORMALISATION
    # ------------------------------------------------------------
    def _remove_noise(self, s: str) -> str:
        return s.lower().strip()

    def _flatten_name(self, s: str) -> str:
        return "".join(ch for ch in s if ch.isalnum() or ch == " ")

    def _normalise(self, name: str) -> str:
        name = self._remove_noise(name)
        name = self._flatten_name(name)
        name = ''.join(ch for ch in name if not ch.isdigit())
        return name.strip()

    # ------------------------------------------------------------
    # FUZZ
    # ------------------------------------------------------------
    def _score(self, a: str, b: str):
        ratio = fuzz.ratio(a, b)
        pratio = fuzz.partial_ratio(a, b)
        weighted = (ratio * 0.6) + (pratio * 0.4)
        return weighted, ratio, pratio

    # ------------------------------------------------------------
    # MODEL NAME FIELD
    # ------------------------------------------------------------
    def _get_name_field(self, model):
        return "player_name" if model is self.models.APITennisPlayer else "name"

    # ------------------------------------------------------------
    # CANDIDATE QUERYSET
    # ------------------------------------------------------------
    def _get_candidate_queryset(self, model, system_norm_name):
        name_field = self._get_name_field(model)

        cleaned = RegexReplace(
            RegexReplace(F(name_field), Value(r"[^A-Za-z ]"), Value(" "), Value("g")),
            Value(r"\s+"),
            Value(" "),
            Value("g"),
            output_field=CharField()
        )

        return (
            model.objects.using("default").filter(vhost=self.vhost)
            .annotate(norm_name=Lower(cleaned))
            .annotate(sim=TrigramSimilarity("norm_name", system_norm_name))
            .filter(sim__gte=SQL_TRIGRAM_THRESHOLD)
            .order_by("-sim")
        )

    # ------------------------------------------------------------
    # MATCH DRIVER TEAM
    # ------------------------------------------------------------
    async def _match_driver_team(self, model, system_team_name: str):
        sys_norm = self._normalise(system_team_name)

        qs = self._get_candidate_queryset(model, sys_norm)
        candidates = await sync_to_async(list, thread_sensitive=False)(qs)

        matched = []
        best_score = -1
        # print(candidates)
        for obj in candidates:
            db_name = getattr(obj, self._get_name_field(model))
            db_norm = self._normalise(db_name)
            if self.verbose:
                self.logger.debug(f"Match Linking {model}{db_name} -> {db_norm}")
            score, r, pr = self._score(sys_norm, db_norm)

            if r >= FUZZ_RATIO_THRESHOLD and pr >= FUZZ_PARTIAL_THRESHOLD:
                matched.append(obj)
                if score > best_score:
                    best_score = score

        # APISPORT → return ALL matches (sports mask differentiation)
        if model is self.models.APISportTeam:
            return matched

        # Tennis / Goalserve → return single best OR None
        return matched[0] if matched else None

    # ------------------------------------------------------------
    # PROCESS TEAM
    # ------------------------------------------------------------
    async def _process_team_data(self, team, **kwargs):
        sys_name = await sync_to_async(lambda:team.name,thread_sensitive=False)()
        if sys_name is None or sys_name == "": return False
        # print(sys_name)
        if self.verbose:
            self.logger.info(f"[TeamLinker] Processing team: '{team.name}' (uuid={team.uuid}) {sys_name}")
        if not await self.find_sync_object("team","kiblio.participant.Participant",False,team):
            participant = await sync_to_async(lambda:self.models.KiblioTeam.objects.using("default").filter(vhost=self.vhost,name=sys_name).first(),thread_sensitive=False)()
            if participant:
                cso = await self.create_sync_object("team",team,"kiblio.participant.Participant",participant.uuid)
                await sync_to_async(lambda:cso.save(),thread_sensitive=False)()
                if self.verbose:
                    self.logger.info(f"Re-linked System Team {sys_name} to KIBLio.")
        if self.verbose:
            self.logger.info(f"[TeamLinker] Match results for '{sys_name}':")

        # ------------------------------------------------------------
        # Create SyncStatus rows
        # ------------------------------------------------------------
        async def create_sync(obj):
            if not obj:
                return
            try:
                obj, c =  await sync_to_async(
                    self.models.TeamSyncStatus.objects.using("default").get_or_create,
                    thread_sensitive=False
                )(
                    vhost=self.vhost,
                    team=team,
                    system_object_type="team",
                    system_object_uuid=team.uuid,
                    driver_object_type=f"{obj._meta.app_label}.{obj._meta.model_name}.{obj._meta.object_name}",
                    driver_object_uuid=obj.uuid,
                    defaults={"driver_object_uuid": obj.uuid},
                )
                if c:
                    if self.verbose:
                        self.logger.info(f"[TeamLinker] Link created and saved. {obj.uuid}")
                await sync_to_async(lambda:obj.save(),thread_sensitive=False)()
            except:
                obj = await sync_to_async(lambda:self.models.TeamSyncStatus.objects.using("default").filter(vhost=self.vhost,
                    team=team,system_object_type="team",
                    driver_object_type=f"{obj._meta.app_label}.{obj._meta.model_name}.{obj._meta.object_name}",
                    driver_object_uuid=obj.uuid).first(),
                    thread_sensitive=False
                )()
            self.logger.info(f"Created Link Object for Team {team.name} (uuid={team.uuid}) / {obj._meta.app_label}.{obj._meta.model_name}.{obj._meta.object_name}")
            return obj

        # Multiple APISPORT entries
        apisport_matches = False
        tennis_match = False
        goalserve_match = False

        if not await self.find_sync_objects("team","apisports.team.Team",True,team):
            apisport_matches = await self._match_driver_team(self.models.APISportTeam, sys_name)
            if self.verbose:
                self.logger.info(
                    f"    APISPORT:   {[o.name for o in apisport_matches] if apisport_matches else 'None'}")

        if not await self.find_sync_objects("team", "apitennis.players.Players", True, team):
            tennis_match = await self._match_driver_team(self.models.APITennisPlayer, sys_name)
            if self.verbose:
                self.logger.info(
                    f"    APITENNIS:  System Name: {sys_name}: {getattr(tennis_match, 'player_name', None) if tennis_match else 'None'}")


        if not await self.find_sync_objects("team", "goalserve.team.Team", True, team):
            goalserve_match = await self._match_driver_team(self.models.GoalserveTeam, sys_name)
            if self.verbose:
                self.logger.info(f"    GOALSERVE:  {goalserve_match.name if goalserve_match else 'None'}")

        if apisport_matches:
            for obj in apisport_matches:
                if self.verbose:
                    self.logger.info(f"[TeamLinker] Creating SyncStatus (APISPORT) → uuid={obj.uuid}")
                await create_sync(obj)

        # Single entries
        if tennis_match:
            if self.verbose:
                self.logger.info(f"[TeamLinker] Creating SyncStatus (APITENNIS) → uuid={tennis_match.uuid}")
            await create_sync(tennis_match)

        if goalserve_match:
            if self.verbose:
                self.logger.info(f"[TeamLinker] Creating SyncStatus (GOALSERVE) → uuid={goalserve_match.uuid}")
            await create_sync(goalserve_match)

        return {
            "team": team.name,
            "apisport": [o.name for o in apisport_matches] if apisport_matches else None,
            "tennis": getattr(tennis_match, "player_name", None) if tennis_match else None,
            "goalserve": goalserve_match.name if goalserve_match else None,
        }

    # ------------------------------------------------------------
    # MAIN LOOP
    # ------------------------------------------------------------
    async def _work_cycle(self):
        teamSyncQuery = self.models.TeamSyncStatus.objects.using("default").filter(team__uuid=OuterRef("pk"))

        teams = (
            self.models.Team.objects.using("default").filter(vhost=self.vhost,name__isnull=False)
        )

        team_list = await sync_to_async(list, thread_sensitive=False)(teams)
        # print(team_list)
        if now() - self.last_timestamp >= timedelta(seconds=1800):
            await self.run_in_batches(
                team_list,
                self._process_team_data,
                batch_size=50,
                label="team_link_source"
            )
            self.last_timestamp = now()

        self.logger.info(f"{self.name} tick...")
