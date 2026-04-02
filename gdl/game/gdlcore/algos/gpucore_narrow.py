import os
import torch
from uuid import UUID
from typing import List, Tuple, Dict
from django.db.models import QuerySet
from .utils.analytics import track_event
from grader.toolkit.parlays import  american_juicer,parlay_decimal_odds,american_to_decimal


# -------------------------------
# Core Parlay Generator Class: Optimising for the chosen winnings (Narrow/windowed version)
# -------------------------------


class GDLGPUCore:
    """
    Core logic to generate parlay bet combinations using PyTorch (CUDA/ROCm),
    based on American odds, juicing rules, and stake/winnings constraints.
    """

    """ Parameters for narrow window control: """
    min_window_pct = 3
    max_window_pct = 3
    """ Set min/max values: """
    min_window = 0
    max_window = 0

    def get_valid_odd_index(self, odds_row: torch.Tensor, generator: torch.Generator) -> int | None:
        """
        Choose a valid index (home, away, or draw) from a row of decimal odds, skipping any 0.0s.
        Uses CPU-safe generator for compatibility with indexing.
        """
        valid_indices = [i for i, val in enumerate(odds_row.tolist()) if val > 0.0]
        if not valid_indices:
            return None
        cpu_gen = torch.Generator(device="cpu").manual_seed(generator.initial_seed())
        rand_idx = torch.randint(len(valid_indices), (1,), generator=cpu_gen).item()
        return valid_indices[rand_idx]

    def _run_gdl_algo1(
        self,
        line_ids: List[str],
        lines_qs: QuerySet,
        min_payout: float = 0,
        depth: int = 7,
        stake: float = 1,
        count: int = 1,
        serialise: bool = True,
        neg_limit: int = -200,
        juice: int = 0,
        debug: bool = False
    ) -> Tuple[List[Dict], QuerySet]:

        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        base_payout = min_payout
        self.min_window = min_payout - (min_payout * (self.min_window_pct / 100))
        self.max_window = min_payout + (min_payout * (self.max_window_pct / 100))

        backoff_pct = 0
        last_backoff_trial = 0
        max_backoff_pct = 50
        backoff_step_pct = 5
        backoff_trigger_trials = 15000

        updated_lines_qs = lines_qs  # Safe fallback

        # Step 1: Filter by UUIDs
        try:
            lines = lines_qs.filter(uuid__in=line_ids)
        except Exception as e:
            if debug:
                print(f"[ERROR] Failed to filter lines: {e}")
            return [], lines_qs

        if len(lines) < depth:
            if debug:
                print(f"[DEBUG] Not enough lines: found {len(lines)}, required {depth}")
            return [], lines_qs

        track_event("parlay_generation_start", {
            "depth": depth,
            "stake": stake,
            "min_payout": min_payout,
            "target_count": count,
            "line_pool_size": len(lines),
        })

        # Step 2: Build odds matrix
        odds_matrix = []
        meta = []
        for line in lines:
            try:
                hp, ap, dp = float(line.home_price), float(line.away_price), float(line.draw_price)
                hp, ap, dp = american_juicer(hp, ap, dp, juice_pct=juice)
                home = american_to_decimal(hp, neg_limit) or 0.0
                away = american_to_decimal(ap, neg_limit) or 0.0
                draw = american_to_decimal(dp, neg_limit) or 0.0

                odds_matrix.append([home, away, draw])
                meta.append({
                    "uuid": str(line.uuid),
                    "home_price": float(line.home_price),
                    "away_price": float(line.away_price),
                    "draw_price": float(line.draw_price),
                    "match_name": line.match.get_match_name(),
                    "match_id": str(line.match.uuid),
                    "sport_id": str(line.match.sport.uuid) if line.match and line.match.sport else None,
                    "sport_title": line.match.sport.title if line.match and line.match.sport else None,
                    "sport_group_name": line.match.sport.group.name if line.match and line.match.sport and line.match.sport.group else None,
                    "sport_group_icon": line.match.sport.group.icon if line.match and line.match.sport and line.match.sport.group else None,
                })
            except Exception as e:
                if debug:
                    print(f"[ERROR] Skipping line: {e}")
                continue

        if len(meta) < depth:
            if debug:
                print(f"[DEBUG] Not enough valid lines.")
            return [], lines_qs

        odds_tensor = torch.tensor(odds_matrix, dtype=torch.float32, device=device)
        num_lines = odds_tensor.shape[0]
        seed = int.from_bytes(os.urandom(8), byteorder="big")
        g = torch.Generator(device=device).manual_seed(seed)

        valid_results = []
        used_uuids = set()
        trials = 0
        max_trials = count * 2500

        while len(valid_results) < count and trials < max_trials:
            trials += 1

            # Sample matches dynamically
            line_sample = torch.randperm(num_lines, generator=g, device=device)[:depth]
            sampled_meta = [meta[idx] for idx in line_sample.tolist()]
            match_ids = [m["match_id"] for m in sampled_meta]
            if len(set(match_ids)) < depth:
                track_event("parlay_ticket_skipped", {"trial": trials, "reason": "duplicate_matches"})
                continue

            choice_sample = torch.randint(0, 3, (depth,), generator=g, device=device)
            selected_odds = odds_tensor[line_sample]
            chosen_odds = torch.zeros(depth, dtype=torch.float32, device=device)

            valid_ticket = True
            for i in range(depth):
                row = selected_odds[i]
                choice = choice_sample[i].item()
                if row[choice] == 0.0:
                    new_choice = self.get_valid_odd_index(row, g)
                    if new_choice is None:
                        valid_ticket = False
                        break
                    choice_sample[i] = new_choice
                    choice = new_choice
                chosen_odds[i] = row[choice]

            if not valid_ticket:
                track_event("parlay_ticket_skipped", {"trial": trials, "reason": "invalid_odds"})
                continue

            total_odds = torch.prod(chosen_odds)
            total_return = total_odds * stake

            if total_return < self.min_window:
                track_event("parlay_ticket_skipped", {"trial": trials, "reason": "below_min_return", "return": round(total_return.item(), 2)})
                continue
            elif total_return > self.max_window:
                track_event("parlay_ticket_skipped", {"trial": trials, "reason": "above_max_return", "return": round(total_return.item(), 2)})
                continue

            # Ticket is valid — assemble
            odds, odds_prices, odds_types = [], [], []
            odds_muuids, odds_lines, odds_sports = [], [], []

            for i, (line_idx, choice_idx) in enumerate(zip(line_sample.tolist(), choice_sample.tolist())):
                m = meta[line_idx]
                chosen_type = ["home_price", "away_price", "draw_price"][choice_idx]
                chosen_price = m[chosen_type]

                odds.append([m["uuid"], m["match_name"]] if serialise else lines[line_idx])
                odds_prices.append(chosen_price)
                odds_types.append(chosen_type)
                odds_muuids.append(m["match_id"])
                odds_lines.append(m["uuid"])
                odds_sports.append([
                    m["sport_id"],
                    m["sport_title"],
                    m["sport_group_name"],
                    m["sport_group_icon"],
                ])
                used_uuids.add(m["uuid"])

            col_data = {
                "odds": odds,
                "odds_prices": odds_prices,
                "odds_types": odds_types,
                "odds_sports": odds_sports,
                "odds_muuids": odds_muuids,
                "odds_lines": odds_lines,
                "total_odds": round(total_odds.item(), 0),
                "total_returns": round(total_return.item(), 0),
            }

            valid_results.append(col_data)

            try:
                updated_lines_qs = lines_qs.exclude(uuid__in=list(used_uuids))
            except Exception as e:
                if debug:
                    print(f"[ERROR] Failed to update queryset: {e}")

            track_event("parlay_ticket_accepted", {
                "trial": trials,
                "return": round(total_return.item(), 2),
                "odds": round(total_odds.item(), 2),
                "line_uuids": odds_lines
            })

            # Backoff trigger
            if trials - last_backoff_trial >= backoff_trigger_trials and backoff_pct < max_backoff_pct:
                backoff_pct += backoff_step_pct
                adjusted_payout = base_payout * (1 - backoff_pct / 100)
                self.min_window = adjusted_payout - (adjusted_payout * (self.min_window_pct / 100))
                self.max_window = adjusted_payout + (adjusted_payout * (self.max_window_pct / 100))
                last_backoff_trial = trials

                track_event("parlay_backoff_triggered", {
                    "trial": trials,
                    "backoff_pct": backoff_pct,
                    "adjusted_payout": adjusted_payout,
                    "new_window": [self.min_window, self.max_window]
                })

                if debug:
                    print(f"[BACKOFF] Trial {trials}: Adjusted payout target to {adjusted_payout:.2f} ({backoff_pct}% off)")

        track_event("parlay_generation_complete", {
            "tickets_generated": len(valid_results),
            "total_trials": trials,
            "final_backoff_pct": backoff_pct,
            "final_window": [self.min_window, self.max_window],
            "used_lines": len(used_uuids)
        })

        if debug:
            print(f"[DEBUG] ✅ Generated {len(valid_results)} tickets in {trials} trials.")

        return valid_results, updated_lines_qs
