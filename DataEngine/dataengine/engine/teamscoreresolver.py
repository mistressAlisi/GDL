# utils/team_score_resolver.py

import re
from rapidfuzz import fuzz
from asgiref.sync import sync_to_async


class TeamScoreResolver:
    """
    Async-safe team score resolver.

    CPU-bound logic stays synchronous.
    Public async entrypoints offload to threadpool.
    """

    GENDER_PATTERNS = {
        "women": re.compile(r"\b(w|women|womens)\b", re.I),
        "men": re.compile(r"\b(m|men|mens)\b", re.I),
    }

    NORMALIZE_RX = re.compile(
        r"\b(w|women|womens|m|men|mens|varsity|jv)\b",
        re.I
    )

    def __init__(self, *, fuzzy_threshold=50, uuid_threshold=85, logger=None):
        self.fuzzy_threshold = fuzzy_threshold
        self.uuid_threshold = uuid_threshold
        self.logger = logger

    # ============================================================
    # 🔒 INTERNAL (SYNC, CPU-BOUND)
    # ============================================================

    def _detect_gender(self, name: str):
        for gender, rx in self.GENDER_PATTERNS.items():
            if rx.search(name or ""):
                return gender
        return "unknown"

    def _normalize(self, name: str):
        if not name:
            return ""
        name = name.lower()
        name = self.NORMALIZE_RX.sub("", name)
        name = re.sub(r"[^a-z0-9 ]+", " ", name)
        return re.sub(r"\s+", " ", name).strip()

    def _uuid_is_compatible(self, sys_name: str, api_name: str) -> bool:
        sys_gender = self._detect_gender(sys_name)
        api_gender = self._detect_gender(api_name)

        # HARD GATE
        if sys_gender != "unknown" and api_gender != "unknown":
            if sys_gender != api_gender:
                return False

        score = fuzz.token_sort_ratio(
            self._normalize(sys_name),
            self._normalize(api_name),
        )

        return score >= self.uuid_threshold

    def _fuzzy_resolve(self, scores, sys_team_name):
        sys_gender = self._detect_gender(sys_team_name)
        sys_norm = self._normalize(sys_team_name)

        best = None
        best_score = 0

        for s in scores:
            if not s.team or not s.team.name:
                continue

            api_gender = self._detect_gender(s.team.name)

            # HARD GATE
            if sys_gender != "unknown" and api_gender != "unknown":
                if sys_gender != api_gender:
                    continue

            api_norm = self._normalize(s.team.name)
            score = fuzz.token_sort_ratio(sys_norm, api_norm)

            if score >= self.fuzzy_threshold and score > best_score:
                best = s
                best_score = score

        return best

    # ============================================================
    # ⚡ PUBLIC ASYNC API (NON-BLOCKING)
    # ============================================================

    async def uuid_is_compatible(self, sys_name: str, api_name: str) -> bool:
        return await sync_to_async(
            self._uuid_is_compatible,
            thread_sensitive=False
        )(sys_name, api_name)

    async def fuzzy_resolve(self, scores, sys_team_name):
        return await sync_to_async(
            self._fuzzy_resolve,
            thread_sensitive=False
        )(scores, sys_team_name)
