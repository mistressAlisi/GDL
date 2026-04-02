# applications/gdl/gdlcore/algos/gpucore_async.py
# Version: v1.8 (Vectorised GPU batch sampling + device-side fingerprint uniqueness)
# Notes:
# - Adds GPU-side ticket fingerprinting to avoid duplicates (unordered).
# - Minimal host/device chatter: only small fingerprint arrays are moved to host for uniqueness filtering.

import os
import asyncio
import random
import traceback
from datetime import timedelta
from decimal import Decimal
from typing import List, Dict, AsyncGenerator

import torch
from django.conf import settings
from django.db.models import Q
from django.utils.timezone import now
from django.utils import timezone
from asgiref.sync import sync_to_async

from account.models import Account
from odds.models import MatchOddsSummary
from parameters.models import VHost
from grader.toolkit.parlays import american_juicer, american_to_decimal, american_juicer_v2


class GDLGPUCoreAsync:
    """
    Asynchronous GPU/CPU parlay generator with streaming support.
    v1.8: Vectorised GPU batch sampling with on-device fingerprinting to ensure unique unordered tickets.
    """

    vhost = False
    account = False
    OUTCOME_MAP = {0: "home", 1: "away", 2: "draw"}
    min_window_pct = 3
    max_window_pct = 3
    min_window = 0
    max_window = 0

    def reset(self):
        self.vhost = False
        self.min_window = 0
        self.max_window = 0

    def _to_float(self, val):
        if val is None:
            return 0.0
        if isinstance(val, Decimal):
            return float(val)
        return float(val)

    def _build_outcome_meta(self, ls, cs, odds_matrix, meta):
        """
        Build {match_uuid: {outcome, odds}} mapping for a ticket
        """
        outcome_meta = {}
        for j, line_idx in enumerate(ls):
            m = meta[line_idx]
            choice = int(cs[j])
            outcome = self.OUTCOME_MAP[choice]
            odds_val = float(odds_matrix[line_idx][choice])

            outcome_meta[m["match_id"]] = {
                "outcome": outcome,
                "odds": odds_val,
            }
        return outcome_meta

    def get_lines(self,
                  lines_list: List = None,
                  sports_filter: List = None,
                  events_within: int = None,
                  juice_pct: float= 0.0):
        if lines_list is not None:
            return lines_list, len(lines_list)
        VHostObj = VHost.objects.get(pk=self.vhost)
        qs = MatchOddsSummary.objects.filter(
            Q(match__vhost=VHostObj)
            & Q(match__active=True)
            & Q(match__open=True)
            & Q(match__finished=False)
            & Q(match__commence_time__gte=now())
            & Q(juice_pct=juice_pct)
            & (Q(home_price__range=(-9499,2000)) | Q(away_price_range=(-9499,2000)) | Q(draw_price_range=(-9499,2000)))
        )
        if sports_filter:
            qs = qs.filter(
                Q(match__sport__uuid__in=sports_filter)
                | Q(match__sport__group__uuid__in=sports_filter)
            )
        if events_within:
            cutoff_time = now() + timedelta(seconds=events_within)
            qs = qs.filter(match__commence_time__lte=cutoff_time)

        qso = qs.select_related(
            "match__home_team",
            "match__away_team",
            "match__sport",
        ).only(
            "uuid",
            "home_price",
            "away_price",
            "draw_price",
            "match__uuid",
            "match__name",
            "match__commence_time",
            "match__home_team__uuid",
            "match__home_team__name",
            "match__home_team__card_logo",
            "match__away_team__uuid",
            "match__away_team__name",
            "match__away_team__card_logo",
            "match__sport__uuid",
            "match__sport__title",
        )

        return qso, qso.count()

    def build_tensor(self, lines, debug):
        odds_matrix, meta = [], []
        accountObj = Account.objects.get(pk=self.account, vhost=self.vhost)
        if accountObj.timezone:
            timezone.activate(accountObj.timezone.timezone)
        for line in lines:
            try:

                # --- NEW MECHANISM: Pre-juiced data: ---
                home = float(american_to_decimal(line.home_price, -5000) or 0.0)
                away = float(american_to_decimal(line.away_price, -5000) or 0.0)
                draw = float(american_to_decimal(line.draw_price, -5000) or 0.0)
                # print(f"Juicer: Home: {line.home_price}->{hp}->{home}, Away: {line.away_price}->{ap}->{away}")
                odds_matrix.append([home, away, draw])
                meta.append({
                    "uuid": str(line.uuid),
                    "match_id": str(line.match.uuid),
                    "match_name": line.match.name,
                    "match_time": str(timezone.localtime(line.match.commence_time).strftime("%m/%d/%Y %I:%M %p")),
                    "sport_id": str(line.match.sport.uuid) if line.match and line.match.sport else None,
                    "sport_name": str(line.match.sport.title) if line.match and line.match.sport else None,
                    "home_price": int(round(float(home), 0)),
                    "away_price": int(round(float(away), 0)),
                    "draw_price": int(round(float(draw), 0)),
                    "home_team": {
                        "uuid": str(line.match.home_team.uuid),
                        "name": line.match.home_team.name,
                        "card_logo": (
                            line.match.home_team.card_logo.url
                            if getattr(line.match.home_team, "card_logo", None)
                            else False
                        ),
                    } if getattr(line.match, "home_team", None) else None,
                    "away_team": {
                        "uuid": str(line.match.away_team.uuid),
                        "name": line.match.away_team.name,
                        "card_logo": (
                            line.match.away_team.card_logo.url
                            if getattr(line.match.away_team, "card_logo", None)
                            else False
                        ),
                    } if getattr(line.match, "away_team", None) else None,
                })
            except Exception as e:
                if debug:
                    print("[build_tensor] Skipping line due to error:", e)
                    traceback.print_exc()
                continue
        return odds_matrix, meta

    def get_valid_odd_index(self, row: torch.Tensor, g: torch.Generator):
        try:
            row_cpu = row.cpu()
            nonzero_indices = (row_cpu != 0.0).nonzero(as_tuple=True)[0]
            if len(nonzero_indices) == 0:
                return None
            rand_idx = torch.randint(0, len(nonzero_indices), (1,), generator=g).item()
            return int(nonzero_indices[rand_idx].item())
        except Exception:
            return None

    # -----------------------
    # CPU single-leg worker (never fails if valid odds exist)
    # -----------------------
    def _generate_single_leg_cpu_blocking(
        self,
        min_payout: float,
        count: int,
        stake: float,
        lines: List,
        juice: float,
        neg_limit: float,
        debug: bool = True,
    ) -> List[Dict]:
        """
        Blocking CPU worker for single-leg parlays. Runs in threads (asyncio.to_thread).
        This version ensures that if there is at least one valid odd in the dataset,
        the worker will produce tickets (it selects the best/closest odd to min_payout
        when none fall inside the adaptive window).
        """
        odds_matrix, meta = self.build_tensor(lines, debug)

        results = []
        trials = 0
        total_gen = 0
        failed_tickets = 0
        if count > 1:
            MAX_TRIALS = max(1000, int(count) * 10000)
        else:
            MAX_TRIALS = 30000

        adaptive_min = self.min_window
        adaptive_max = self.max_window
        expansion_pct = 0.01
        max_expansion = 0.20

        # Pre-calc available indices to allow quick sampling
        num_rows = len(odds_matrix)

        while total_gen < int(count) and trials < MAX_TRIALS:
            trials += 1

            if num_rows == 0:
                # no lines — cannot produce tickets
                failed_tickets += 1
                continue

            # pick a random row
            idx = random.randrange(num_rows)
            row = odds_matrix[idx]
            m = meta[idx]

            # collect valid choices in this row
            valid_choices = [i for i, odd in enumerate(row) if odd > 0.0]
            if not valid_choices:
                # this row has no valid odds — try another
                failed_tickets += 1
                continue

            # For each valid choice compute total_return and pick:
            # 1) any choice that falls in adaptive window (prefer randomly among them)
            # 2) if none in window, pick the choice whose return is closest to min_payout
            candidate_returns = []
            for c in valid_choices:
                total_odds = float(row[c])
                total_return = total_odds * float(stake)
                candidate_returns.append((c, total_odds, total_return))

            # find choices within adaptive window
            within_window_choices = [t for t in candidate_returns if adaptive_min <= t[2] <= adaptive_max]

            if within_window_choices:
                # pick random one among valid within-window choices to add variety
                c_choice, c_odds, c_return = random.choice(within_window_choices)
            else:
                # none in window — choose the one closest to min_payout
                # this guarantees we accept a ticket for this row
                best = min(candidate_returns, key=lambda x: abs(x[2] - min_payout))
                c_choice, c_odds, c_return = best

                # If the chosen return is far from window and we're seeing lots of failures,
                # expand adaptive window progressively (but we still accept this choice).
                if failed_tickets % 1000 == 0 and failed_tickets > 0:
                    expansion = min(expansion_pct, max_expansion)
                    adaptive_min = min_payout - (min_payout * (self.min_window_pct / 100 + expansion))
                    adaptive_max = min_payout + (min_payout * (self.max_window_pct / 100 + expansion))
                    expansion_pct = min(expansion_pct + 0.01, max_expansion)
                    if debug:
                        print(f"[single-leg] Expanded adaptive window: {adaptive_min} - {adaptive_max}")

            outcome = self.OUTCOME_MAP[c_choice]
            total_odds = float(c_odds)
            total_return = float(c_return)
            if debug:
                print(f"[single-leg] Total Odds: {total_odds} - Total Return: {total_return}")
            # Build ticket (we always accept this single-leg)
            ticket = {
                "type": "ticket",
                "lines": [m["uuid"]],
                "muuids": [m["match_id"]],
                "outcomes": [outcome],
                "total_odds": int(round(total_odds)),
                "total_returns": int(round(total_return)),
                "total_stake": int(round(stake)),
                "status": "C",
                "depth": 1,
                "legs": [
                    {
                        "match_name": m["match_name"],
                        "match_time": m.get("match_time"),
                        "home_team": m["home_team"],
                        "away_team": m["away_team"],
                        "match_uuid": m["match_id"],
                        "outcome": outcome,
                    }
                ],
                "outcome_meta": {
                    m["match_id"]: {
                        "outcome": outcome,
                        "odds": total_odds,
                    }
                },
            }
            results.append(ticket)
            total_gen += 1

        results.append(
            {
                "type": "complete",
                "message": f"Single-leg generation finished: {total_gen}/{count}",
                "trials": trials,
                "failed": failed_tickets,
            }
        )
        return results

    # -----------------------
    # MAIN STREAM GENERATE
    # -----------------------
    async def stream_generate(
        self,
        vhost: str,
        account: str,
        vdomain: str,
        min_payout: float,
        count: int,
        depth: int,
        stake: float,
        lines_list: List = None,
        sports_filter: List = None,
        events_within: int = None,
        use_gpu: bool = True,
        debug: bool = True,
        neg_limit: float = -200,
        serialise: bool = False,
        juice: float = 0.05,
    ) -> AsyncGenerator[Dict, None]:
        # sanitize inputs
        try:
            count = max(1, int(count))
        except Exception:
            count = 1
        try:
            depth = max(1, int(depth))
        except Exception:
            depth = 1
        try:
            stake = float(stake)
        except Exception:
            stake = 1.0
        try:
            min_payout = float(min_payout)
        except Exception:
            min_payout = 0.0
        if settings.GDL_USE_GPU:
            device = torch.device("cuda" if use_gpu and torch.cuda.is_available() else "cpu")
        else:
            device = torch.device("cpu")
        if debug:
            print(f"[DEBUG] stream_generate start: device={device}, count={count}, depth={depth}, stake={stake}, min_payout={min_payout}")
        # print(f"[DEBUG] We're using device {device} for operations.")
        self.min_window = min_payout - (min_payout * (self.min_window_pct / 100))
        self.max_window = min_payout + (min_payout * (self.max_window_pct / 100))
        self.vhost = vhost
        self.account = account

        # load lines (sync -> thread)
        try:
            lines, line_count = await sync_to_async(self.get_lines, thread_sensitive=True)(lines_list, sports_filter, events_within, juice)
        except Exception as e:
            if debug:
                print("[ERROR] get_lines failed:", e)
                traceback.print_exc()
            yield {"type": "error", "error": f"get_lines failed: {e}"}
            self.reset()
            return

        if debug:
            print(f"[DEBUG] get_lines returned count={line_count}")

        if line_count < depth:
            if debug:
                print(f"[DEBUG] Not enough lines for depth={depth}. Got {line_count}")
            yield {"type": "complete", "message": f"Generation finished: 0/{count} (insufficient source lines)", "trials": 0, "failed": 0,"incomplete":True}
            self.reset()
            return

        # single-leg CPU handling for single dimension tickets:
        if depth == 1:
            workers = max(1, min(4, os.cpu_count() or 1))
            per_worker = max(1, count // workers)
            remainder = count - (per_worker * workers)
            tasks = []
            for i in range(workers):
                this_count = per_worker + (1 if i < remainder else 0)
                tasks.append(asyncio.to_thread(
                    self._generate_single_leg_cpu_blocking,
                    min_payout,
                    this_count,
                    stake,
                    lines,
                    juice,
                    neg_limit,
                    debug,
                ))
            for coro in asyncio.as_completed(tasks):
                try:
                    results = await coro
                except Exception as e:
                    if debug:
                        print("[ERROR] single-leg worker failed:", e)
                        traceback.print_exc()
                    continue
                for r in results:
                    yield r
            self.reset()
            return

        # build tensor & meta (on CPU)
        try:
            odds_matrix, meta = await sync_to_async(self.build_tensor, thread_sensitive=True)(lines, debug)
        except Exception as e:
            if debug:
                print("[ERROR] build_tensor failed:", e)
                traceback.print_exc()
            yield {"type": "error", "error": f"build_tensor failed: {e}"}
            self.reset()
            return

        num_lines = len(meta)
        if debug:
            print(f"[DEBUG] Post build_tensor: meta_len={num_lines}, odds_rows={len(odds_matrix)}, Juice {juice} ")

        if num_lines == 0:
            yield {"type": "complete", "message": "Generation finished: 0/0 (no valid lines)", "trials": 0, "failed": 0}
            self.reset()
            return

        if num_lines < depth:
            if debug:
                print(f"[DEBUG] After build_tensor not enough valid lines for depth={depth}: {num_lines}")
            yield {"type": "complete", "message": f"Generation finished: 0/{count} (insufficient valid lines after filtering)", "trials": 0, "failed": 0}
            self.reset()
            return

        # move odds tensor to device (GPU or CPU)
        try:
            odds_tensor = torch.tensor([[float(v) for v in row] for row in odds_matrix], dtype=torch.float32, device=device)
        except Exception as e:
            if debug:
                print("[ERROR] Failed to build odds_tensor:", e)
                traceback.print_exc()
            yield {"type": "error", "error": f"Failed to build odds tensor: {e}"}
            self.reset()
            return

        # Build integer mapping of match ids to small ints so we can detect duplicate matches on-device
        match_id_list = [m["match_id"] for m in meta]
        # map each unique match_id to an int id
        match_to_idx = {}
        match_idx_arr = []
        next_mid = 0
        for mid in match_id_list:
            if mid not in match_to_idx:
                match_to_idx[mid] = next_mid
                next_mid += 1
            match_idx_arr.append(match_to_idx[mid])
        match_idx_tensor = torch.tensor(match_idx_arr, dtype=torch.int64, device=device)  # shape: (num_lines,)

        # RNG generator for device; if cuda, use cuda generator; else cpu generator.
        seed = int.from_bytes(os.urandom(8), byteorder="big")
        gen_device = device.type
        try:
            gen = torch.Generator(device=device).manual_seed(seed)
        except Exception:
            # fallback to CPU generator if device-specific generator not available
            gen = torch.Generator(device="cpu").manual_seed(seed)
            gen_device = "cpu"
        if debug:
            print(f"[DEBUG] RNG seed={seed}; generator device={gen_device}; sampling on device={device}")

        # batching parameters (tune these to your hardware)
        # larger batch_size = more GPU utilisation but more memory
        batch_size = 8192  # start high; adjust if you run OOM
        # The number of valid tickets to collect per batch to move results back, clamp to count
        needed = count

        # adaptive window
        adaptive_min = self.min_window
        adaptive_max = self.max_window
        expansion_pct = 0.01
        max_expansion = 0.50

        trials = 0
        total_gen = 0
        failed_tickets = 0
        if count == 1:
            MAX_TRIALS = 10000000
        else:
            MAX_TRIALS = max(10000, count * 500000)

        # Keep a host-side set of already seen fingerprints for this run
        seen_fps = set()

        # We'll collect valid candidate rows' (line_samples, choice_samples) on device,
        # then move the chosen subset indexes & fingerprints to CPU and build final ticket dicts from meta.
        while total_gen < count and trials < MAX_TRIALS:
            trials += 1

            # sample a batch on-device using device generator where possible
            try:
                # line samples: shape (batch_size, depth)
                line_samples = torch.randint(0, num_lines, (batch_size, depth), dtype=torch.long, device=device, generator=gen)
                # choice samples: shape (batch_size, depth) with values in {0,1,2}
                choice_samples = torch.randint(0, 3, (batch_size, depth), dtype=torch.long, device=device, generator=gen)
            except Exception as e:
                # fallback: sample on CPU and transfer (slower, but robust)
                failed_tickets += batch_size
                if debug:
                    print("[WARN] device sampling failed, falling back to CPU sampling:", e)
                    traceback.print_exc()
                line_samples = torch.randint(0, num_lines, (batch_size, depth), dtype=torch.long, device="cpu")
                choice_samples = torch.randint(0, 3, (batch_size, depth), dtype=torch.long, device="cpu")
                line_samples = line_samples.to(device)
                choice_samples = choice_samples.to(device)

            # gather selected odds: selected_odds shape (batch_size, depth, 3) -> then pick chosen odds
            # get per-sample-per-leg row of 3 odds
            selected_odds = odds_tensor[line_samples]  # -> (batch_size, depth, 3)

            # gather chosen odds using choice_samples
            # expand choice_samples to match last dim for gather: (batch_size, depth, 1)
            choice_idx = choice_samples.unsqueeze(-1)
            chosen_odds = torch.gather(selected_odds, dim=2, index=choice_idx).squeeze(-1)  # (batch_size, depth)

            # Replace zeros: for entries where chosen_odds == 0, find best non-zero option (argmax over masked values)
            zero_mask = (chosen_odds == 0.0)  # (batch_size, depth)
            if zero_mask.any():
                # create masked selected_odds where zeros become 0 in sel_mask (we'll argmax)
                sel_mask = (selected_odds > 0.0).to(selected_odds.dtype) * selected_odds
                alt_choice = torch.argmax(sel_mask, dim=2)  # (batch_size, depth)
                alt_choice_values = torch.gather(selected_odds, 2, alt_choice.unsqueeze(-1)).squeeze(-1)  # (batch_size, depth)
                alt_nonzero = (alt_choice_values > 0.0) & zero_mask
                if alt_nonzero.any():
                    choice_samples = torch.where(alt_nonzero, alt_choice, choice_samples)
                    chosen_odds = torch.where(alt_nonzero, alt_choice_values, chosen_odds)

            # Now filter out any rows with any remaining zero chosen odds
            valid_nonzero_mask = (chosen_odds > 0.0).all(dim=1)  # (batch_size,)

            # Duplicate match detection: map line_samples -> match_idx and check per-row duplicates
            match_idxs = match_idx_tensor[line_samples]  # (batch_size, depth)
            # To detect duplicates per row, sort and compare adjacent
            sorted_match_idxs, _ = torch.sort(match_idxs, dim=1)
            dup_mask = (sorted_match_idxs[:, 1:] == sorted_match_idxs[:, :-1]).any(dim=1)  # (batch_size,)
            unique_match_mask = ~dup_mask

            # Combined validity mask so far
            candidate_mask = valid_nonzero_mask & unique_match_mask

            if candidate_mask.sum().item() == 0:
                # nothing valid in this batch: expand window periodically to avoid starving
                failed_tickets += batch_size

                if failed_tickets % 100 == 0:
                    expansion = min(expansion_pct + (failed_tickets // 100) * 0.01, max_expansion)
                    adaptive_min = min_payout - (min_payout * (self.min_window_pct / 100 + expansion))
                    adaptive_max = min_payout + (min_payout * (self.max_window_pct / 100 + expansion))
                    if debug:
                        print(f"[DEBUG] expanded window to {adaptive_min} - {adaptive_max} after {failed_tickets} fails, {max_expansion}, MT: {MAX_TRIALS}")
                # continue sampling

                continue
            # print(f"loopin like a maniac! {failed_tickets}")
            if failed_tickets > MAX_TRIALS:
                if debug:
                    print(f"[DEBUG] failed tickets: {failed_tickets} - Breaking")
                yield {
                    "type": "empty",
                    "message": "Single-leg generation finished: 0/{} (no valid tickets after max window expansion)".format(
                        count),
                    "trials": trials,
                    "failed": failed_tickets,
                    "incomplete":True
                }
                break

            # compute total odds and returns vectorised
            # chosen_odds is (batch_size, depth)
            total_odds_vec = torch.prod(chosen_odds, dim=1)  # (batch_size,)
            total_returns_vec = total_odds_vec * float(stake)

            # window mask
            within_window = (total_returns_vec >= adaptive_min) & (total_returns_vec <= adaptive_max)

            # final valid mask
            final_mask = candidate_mask & within_window

            # If nothing passing window, expand window handling later
            if final_mask.sum().item() == 0:
                failed_tickets += int(candidate_mask.sum().item())
                if failed_tickets % 100 == 0:
                    expansion = min(expansion_pct + (failed_tickets // 100) * 0.01, max_expansion)
                    adaptive_min = min_payout - (min_payout * (self.min_window_pct / 100 + expansion))
                    adaptive_max = min_payout + (min_payout * (self.max_window_pct / 100 + expansion))
                    if debug:
                        print(f"[DEBUG] expanded window to {adaptive_min} - {adaptive_max} after {failed_tickets} fails, {max_expansion}, MT: {MAX_TRIALS}")
                continue
            # print("loopin like a maniac")
            # Compute leg-level compact IDs on device: leg_id = match_idx * 3 + choice
            # dtype int64 to be safe
            leg_ids = match_idxs * 3 + choice_samples  # (batch_size, depth), int64

            # Build fingerprints for rows that are final candidates (do on-device)
            cand_indices = torch.nonzero(final_mask, as_tuple=False).squeeze(-1)  # indices on device
            if cand_indices.numel() == 0:
                # nothing to process this batch
                continue

            cand_leg_ids = leg_ids[cand_indices]  # (n_cand, depth)
            # sort leg ids per row to make unordered sets equal
            sorted_leg_ids_for_cand, _ = torch.sort(cand_leg_ids, dim=1)  # (n_cand, depth)

            # Rolling FNV-like mix on-device using int64
            # FNV parameters (64-bit-ish constants)
            # We'll keep values within int64 range; collisions extremely unlikely for small depth
            FNV_OFFSET = torch.tensor([1469598103934665603], dtype=torch.int64, device=device)
            FNV_PRIME = torch.tensor([1099511628211], dtype=torch.int64, device=device)

            # compute fingerprint vectorized:
            # start with offset, then for each leg: h = (h ^ leg) * FNV_PRIME
            h = FNV_OFFSET.repeat(sorted_leg_ids_for_cand.size(0))  # (n_cand,)
            # iterate over depth dimension (small) — efficient because depth is small (2-8)
            for d in range(sorted_leg_ids_for_cand.size(1)):
                leg_column = sorted_leg_ids_for_cand[:, d].to(torch.int64)
                h = (h ^ leg_column) * FNV_PRIME
                # keep in signed int64 range (Torch will wrap naturally)

            # `h` is device int64 tensor of fingerprints for candidate rows
            # Move small fingerprint array and the candidate indices to host for uniqueness filtering
            try:
                dev_fps = h.cpu().numpy().tolist()  # list of ints (python)
                dev_cand_idx_list = cand_indices.cpu().numpy().tolist()
            except Exception as e:
                # if transfer fails, skip this batch
                failed_tickets += cand_indices.numel()
                if debug:
                    print("[ERROR] Failed to move fingerprints to host:", e)
                    traceback.print_exc()
                continue

            # Filter out fingerprints already seen (host-side set)
            new_accept_positions = []
            new_accept_fp = []
            batch_seen = set()

            for pos_in_cand, fp in enumerate(dev_fps):
                if fp in seen_fps or fp in batch_seen:
                    continue
                batch_seen.add(fp)
                new_accept_positions.append(dev_cand_idx_list[pos_in_cand])
                new_accept_fp.append(fp)

            if len(new_accept_positions) == 0:
                # all candidates were duplicates — count as failures and continue
                failed_tickets += len(dev_fps)
                # allow window expansion as before
                if failed_tickets % 1000 == 0:
                    expansion = min(expansion_pct + (failed_tickets // 1000) * 0.01, max_expansion)
                    adaptive_min = min_payout - (min_payout * (self.min_window_pct / 100 + expansion))
                    adaptive_max = min_payout + (min_payout * (self.max_window_pct / 100 + expansion))
                    if debug:
                        print(f"[DEBUG] expanded window to {adaptive_min} - {adaptive_max} after {failed_tickets} fails")
                continue

            # We have one or more unique candidate positions in this batch. Take up to `count - total_gen`.
            # Map new_accept_positions (which are indices into the batch) to local order and slice.
            # Determine how many to take
            take = min(len(new_accept_positions), count - total_gen)
            # take the first `take` unique new positions
            sel_batch_positions = new_accept_positions[:take]
            sel_fps = new_accept_fp[:take]

            # Now assemble selected sample arrays from device tensors for each chosen position
            sel_idx = torch.tensor(sel_batch_positions, dtype=torch.long, device=device)

            sel_line_samples = line_samples[sel_idx].cpu().numpy().tolist()
            sel_choice_samples = choice_samples[sel_idx].cpu().numpy().tolist()
            sel_total_odds = total_odds_vec[sel_idx].cpu().numpy().tolist()
            sel_total_returns = total_returns_vec[sel_idx].cpu().numpy().tolist()

            # Build and yield tickets (single CPU pass per selection)
            for fp in sel_fps[:take]:
                seen_fps.add(int(fp))

            for i in range(take):
                ls = sel_line_samples[i]
                cs = sel_choice_samples[i]
                todds = sel_total_odds[i]
                treturns = sel_total_returns[i]

                # assemble outcomes and legs using meta (already in memory, safe)
                outcomes = [self.OUTCOME_MAP[int(c)] for c in cs]
                legs = []
                for j, line_idx in enumerate(ls):
                    m = meta[line_idx]
                    legs.append({
                        "match_id": m["match_id"],
                        "match_name": m["match_name"],
                        "match_time": m["match_time"],
                        "sport_id": m["sport_id"],
                        "sport_name": m["sport_name"],
                        "home_team": m["home_team"],
                        "away_team": m["away_team"],
                        "outcome": outcomes[j],
                    })

                outcome_meta = self._build_outcome_meta(
                    ls,
                    cs,
                    odds_matrix,
                    meta,
                )

                ticket = {
                    "type": "ticket",
                    "lines": [meta[idx]["uuid"] for idx in ls],
                    "muuids": [meta[idx]["match_id"] for idx in ls],
                    "outcomes": outcomes,
                    "total_odds": int(round(float(todds))),
                    "total_returns": int(round(float(treturns))),
                    "total_stake": int(round(stake)),
                    "status": "C",
                    "depth": depth,
                    "legs": legs,
                    "outcome_meta": outcome_meta,
                }

                yield ticket
                total_gen += 1
            # done with this batch; continue if more needed
            # adaptive expansion may be adjusted inside loop if many failures
            if debug:
                print(f"[DEBUG] batch produced {len(sel_fps[:take])} tickets; total_gen={total_gen}; trials={trials}; failed={failed_tickets}")

        # final completion frame
        yield {
            "type": "complete",
            "message": f"Generation finished: {total_gen}/{count} tickets produced.",
            "trials": trials,
            "failed": failed_tickets,
        }

        self.reset()
