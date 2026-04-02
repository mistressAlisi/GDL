import os
import torch
from uuid import UUID
from typing import List, Tuple, Dict
from django.db.models import QuerySet

from qualifier.toolkit.parlays import  american_juicer,parlay_decimal_odds,american_to_decimal


# -------------------------------
# Core Parlay Generator Class
# -------------------------------


class GDLGPUCore:
    """
    Core logic to generate parlay bet combinations using PyTorch (CUDA/ROCm),
    based on American odds, juicing rules, and stake/winnings constraints.
    """

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
        """
        Main parlay ticket generator using PyTorch tensor ops.

        Args:
            line_ids (List[str]): UUIDs of odds lines to consider.
            lines_qs (QuerySet): QuerySet of MatchOddsSummary lines.
            min_payout (float): Minimum acceptable payout per parlay.
            depth (int): Number of legs in each parlay.
            stake (float): Stake amount per parlay.
            count (int): Number of valid parlays to return.
            serialise (bool): Whether to return UUIDs/names or model objects.
            neg_limit (int): Lowest acceptable American odds.
            juice (int): Percentage juice to apply before conversion.
            debug (bool): Print debug info if True.

        Returns:
            Tuple[List[Dict], QuerySet]: List of generated parlay data and updated line pool.
        """

        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        if debug:
            print(f"[DEBUG] Using device: {device}")
            print(f"[DEBUG]: Juice is set to {juice}")

        # Step 1: Filter lines by input UUIDs
        lines = lines_qs.filter(uuid__in=line_ids)
        if len(lines) < depth:
            if debug:
                print(f"[DEBUG] Not enough lines: found {len(lines)}, required {depth}")
            return [], lines_qs

        odds_matrix = []
        meta = []

        # Step 2: Apply juice, convert to decimal odds, and collect metadata
        for line in lines:
            hp, ap, dp = float(line.home_price), float(line.away_price), float(line.draw_price)

            if debug:
                print(f"[DEBUG] PRE-JUICE Line {line.uuid}: home={hp}, away={ap}, draw={dp}")

            hp, ap, dp = american_juicer(hp, ap, dp, juice_pct=juice)

            home = american_to_decimal(hp, neg_limit)
            away = american_to_decimal(ap, neg_limit)
            draw = american_to_decimal(dp, neg_limit)

            # Replace any failed conversions (None) with 0.0
            home = home if home is not None else 0.0
            away = away if away is not None else 0.0
            draw = draw if draw is not None else 0.0

            if debug and (home == 0.0 or away == 0.0 or (dp != 0 and draw == 0.0)):
                print(
                    f"[DEBUG] Line {line.uuid} has some zeroed decimal odds after juicing/conversion: "
                    f"home={home}, away={away}, draw={draw} | raw juiced: {hp}, {ap}, {dp}"
                )

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

        if len(meta) < depth:
            if debug:
                print(f"[DEBUG] Not enough valid lines: got {len(meta)}, required {depth}")
            return [], lines_qs

        # Step 3: Move data to PyTorch
        odds_tensor = torch.tensor(odds_matrix, dtype=torch.float32, device=device)
        num_lines = odds_tensor.shape[0]

        # Step 4: Set seed and random generator
        seed = int.from_bytes(os.urandom(8), byteorder="big")
        g = torch.Generator(device=device).manual_seed(seed)

        valid_results = []
        used_uuids = set()
        trials = 0
        max_trials = count * 50

        if debug:
            print(f"[DEBUG] Starting parlay generation loop...")
            print(f"[DEBUG] Number of lines: {num_lines}")
            print(f"[DEBUG] Number of seeds: {seed}")
        # Step 5: Generate valid parlays
        while len(valid_results) < count and trials < max_trials:
            trials += 1

            line_sample = torch.randperm(num_lines, generator=g, device=device)[:depth]
            match_ids = [meta[idx]["match_id"] for idx in line_sample.tolist()]
            if len(set(match_ids)) < depth:
                if debug:
                    print(f"[DEBUG] Trial {trials}: Duplicate matches found, skipping.")
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
                        if debug:
                            print(f"[DEBUG] Trial {trials}: All odds zero in match {line_sample[i].item()}, skipping.")
                        break
                    else:
                        choice_sample[i] = new_choice
                        choice = new_choice
                        if debug:
                            print(f"[DEBUG] Trial {trials}: Replaced 0.0 odd at leg {i} with alternative {choice}")

                chosen_odds[i] = row[choice]

            if not valid_ticket:
                continue

            total_odds = torch.prod(chosen_odds)
            total_return = total_odds * stake

            if total_return < min_payout:
                if debug:
                    print(f"[DEBUG] Trial {trials}: Below minimum payout {min_payout:.2f}, skipping.")
                continue

            # Step 6: Assemble result
            odds = []
            odds_prices = []
            odds_types = []
            odds_sports = []
            odds_muuids = []
            odds_lines = []

            for i, (line_idx, choice_idx) in enumerate(zip(line_sample.tolist(), choice_sample.tolist())):
                m = meta[line_idx]
                chosen_type = ["home_price", "away_price", "draw_price"][choice_idx]
                chosen_price = m[chosen_type]

                if serialise:
                    odds.append([m["uuid"], m["match_name"]])
                else:
                    odds.append(lines[line_idx])

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
            if debug:
                print(f"[DEBUG] Trial {trials}: ✅ Ticket accepted. Total Return: {col_data['total_returns']}")
                print(f"[DEBUG] Trial Odds Lines {odds_lines}")
                print(f"[DEBUG] Trial Odds Prices {odds_prices}")
                print(f"***************")
            valid_results.append(col_data)

            # Step 7: Exclude used lines from pool
            updated_lines_qs = lines_qs.exclude(uuid__in=list(used_uuids))

        if debug:
            print(f"[DEBUG] Completed. Generated {len(valid_results)} valid tickets.")

        return valid_results, updated_lines_qs

