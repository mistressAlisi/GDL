from decimal import Decimal

import numpy as np
import torch
from django.db.models import Q

from grader.toolkit.parlays import  parlay_decimal_odds
from odds.models import MatchOddsSummary


class GDLCore(object):
    min_lines = 3


    # Version 1 of the Algorithm is completely randomised, maximises returns over everything else:
    def _run_gdl_algo1(self,lines,min_payout=0,depth=7,stake=1,serialise=True):
        # print(f"Selecting Possible Lines for GDL With min payout odds of {min_payout} or more.")
        col_data = {
            "odds": [],
            "odds_prices": [],
            "odds_types": [],
            "odds_sports": [],
            "odds_muuids": [],
            "odds_lines": [],
            "total_odds": 0,
            "total_returns":0
        }
        i = 0
        price = 0

        odds = []
        odds_prices = []
        odds_types = []
        odds_sports = []
        odds_muuids = []
        odds_lines = []
        total_odds = -1
        if (len(lines)) == 0:
            #logger.warning("No lines found! Cannot run it, capt'n!")
            # print("No lines found! Cannot run it, capt'n!")
            return False,False
        _lines = lines
        while (stake*total_odds) < min_payout or self.min_lines >= len(odds):
            odds = []
            odds_prices = []
            odds_types = []
            odds_sports = []
            odds_muuids = []
            odds_lines = []
            total_odds = 0
            _lines = lines

            for i in range(0, depth, 1):
                if (stake*total_odds) < min_payout or self.min_lines >= len(odds):
                    line_col = int(np.random.randint(len(_lines)))
                    line = _lines[line_col]
                    _lines = _lines.exclude(Q(uuid=line.uuid))
                    if not serialise:
                        odds.append(line)
                    else:
                        odds.append([str(line.uuid),line.match.get_match_name()])
                    price = 0
                    odds_muuids.append(str(line.match.uuid))
                    type = ""
                    for value in ["home_price", "away_price", "draw_price"]:
                        if price < getattr(line, value):
                            price = float(getattr(line, value))
                            type = value
                    odds_prices.append(float(price))
                    odds_types.append(type)
                    odds_lines.append(str(line.uuid))
                    odds_sports.append([str(line.match.sport.uuid),line.match.sport.title,line.match.sport.group.name,line.match.sport.group.icon])
                    total_odds = round(parlay_decimal_odds(odds_prices),0)
        # print(odds)
        col_data["odds"] = odds
        col_data["odds_prices"] = odds_prices
        col_data["odds_types"] = odds_types
        col_data["total_odds"] = float(total_odds)
        col_data["odds_sports"] = odds_sports
        col_data["odds_muuids"] = odds_muuids
        col_data["odds_lines"] = odds_lines
        col_data["total_returns"] = round(float(total_odds*stake),0)
        lines = _lines
        return col_data,lines

    def _american_to_decimal(self, american_odds, neg_limit=-200, juice=0):
        """
        Convert a single American odd to decimal, respecting negative odds limit.
        Odds below neg_limit (e.g. -200) will be zeroed (excluded).
        """
        if american_odds == 0 or american_odds < neg_limit:
            return None

            # Step 1: Convert to implied probability
        if american_odds > 0:
            implied_prob = 100 / (american_odds + 100)
        else:
            implied_prob = abs(american_odds) / (abs(american_odds) + 100)

        # Step 2: Apply juice (increase implied probability)
        if juice > 0:
            juiced_prob = implied_prob * (1 + juice / 100)
        else:
            juiced_prob = implied_prob

        # Prevent overflow (>100% probability)
        if juiced_prob >= 1:
            return None

        # Step 3: Convert back to decimal odds
        decimal_odds = 1 / juiced_prob
        return decimal_odds
