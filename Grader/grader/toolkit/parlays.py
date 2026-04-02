import math
from decimal import Decimal
from fractions import Fraction




def parlay_decimal_odds(american_odds_list):
    """
    Convert a list of American odds into final decimal odds for a parlay bet.

    Parameters:
        american_odds_list (list of float or int): List of American odds for each leg.

    Returns:
        float: Final decimal odds for the parlay.
    """
    decimal_odds = []

    for odd in american_odds_list:
        if odd > 0:
            decimal = (odd / 100) + 1
        else:
            decimal = (100 / abs(odd)) + 1
        decimal_odds.append(decimal)

    # Multiply all decimal odds together
    # print(decimal_odds)
    parlay_odds = 1
    for dec in decimal_odds:
        parlay_odds *= dec

    return parlay_odds


def american_to_dec(american_odds):
    if american_odds == 0: return 0
    if american_odds > 0:
        return (american_odds / 100)
    else:
        return (100 / abs(american_odds)) + 1

def american_juicer(home_price,away_price,draw_price=0,juice_pct=0,use_decimal=False):
   """
   Apply juice (vig) by lowering all prices by a scaled delta based on home/away price.
   """
   delta = abs(min(home_price,away_price))+max(home_price,away_price)
   if juice_pct > 0:
        j_delta = Decimal((delta / 2)) * Decimal(juice_pct)
        if draw_price > 0:
            draw_price = Decimal(draw_price) - j_delta
        home_price = Decimal(home_price) -j_delta
        away_price = Decimal(away_price) -j_delta
   # print(home_price, away_price, draw_price)
   if not use_decimal:
        return home_price,away_price,draw_price
   else:
        return american_to_dec(home_price), american_to_dec(away_price), american_to_dec(draw_price)


def american_to_decimal(american_odds,neg_limit=-110):
        """
        Convert American odds (juiced externally) to decimal odds.

        Args:
            american_odds (float): Juiced American odds (positive or negative).
            neg_limit (int): Minimum allowed value for negative odds.

        Returns:
            float or None: Decimal odds or None if odds are invalid.
        """
        if american_odds == 0 or american_odds < neg_limit:
            return None

        if american_odds > 0:
            return (american_odds / 100) + 1
        else:
            return (100 / abs(american_odds)) + 1

def moneyline_to_prob(ml):
    """Convert American moneyline to implied probability (no juice)."""

    if ml < 0:
        return -ml / (-ml + 100)
    else:
        return 100 / (ml + 100)

def prob_to_moneyline(
    p,
    min_prob=0.005,
    max_prob=0.995,
    max_fav=-5000,
    max_dog=5000,
):
    # Clamp probability
    p = max(min(p, max_prob), min_prob)

    if p >= 0.5:
        ml = -int(round((p / (1 - p)) * 100))
        return max(ml, max_fav)
    else:
        ml = int(round(((1 - p) / p) * 100))
        return min(ml, max_dog)

# def american_juicer_v2(home_price, away_price, juice_pct=0.0):
#     """
#     Apply symmetric juice to a true zero-juice 2-way American line.
#
#     Assumptions
#     -----------
#     - Exactly one side is negative, one positive
#     - Input line is zero-juice (|fav| == |dog|)
#     - juice_pct is expressed as 0.04 for 4%
#
#     Returns
#     -------
#     home, away : int
#         Symmetrically juiced American odds
#     """
#
#     if home_price == 0 or away_price == 0:
#         raise ValueError("Invalid moneyline")
#
#     if home_price * away_price >= 0:
#         raise ValueError(f"Expected opposite-signed moneylines. Recieved: Hp: {home_price}, Ap: {away_price}")
#
#     scale = 1.0 + float(juice_pct)
#
#     # Identify favorite/dog by magnitude
#     if abs(home_price) >= abs(away_price):
#         fav_home = True
#         fav = home_price
#         dog = away_price
#     else:
#         fav_home = False
#         fav = away_price
#         dog = home_price
#
#     fav_new = -int(round(abs(fav) * scale))
#     dog_new =  int(round(abs(dog) * scale))
#
#     if fav_home:
#         return fav_new, dog_new
#     else:
#         return dog_new, fav_new


def american_to_prob(american):
    if american > 0:
        return 100 / (american + 100)
    else:
        return -american / (-american + 100)


def prob_to_decimal(p):
    return 1 / p


def decimal_to_american(decimal):
    # print(f"DTA {decimal}")
    if decimal >= 2.0:
        return int(round((decimal - 1) * 100))
    else:
        return int(round(-100 / (decimal - 1)))


def logit(p):
    return math.log(p / (1 - p))


def inv_logit(x):
    return 1 / (1 + math.exp(-x))


def american_juicer_v2_old(home_price, away_price, juice_pct=0.0):
    """
    Logit-based American juicer with extreme-price hold caps.
    Correctly juices pick'em and extreme favorites.
    """

    # --- 1. Determine effective hold (risk caps) ---
    effective_hold = juice_pct
    min_odds = min(home_price)
    if min_odds <= -9500:
        raise ValueError("Odds are beyond the minimum, -9500.")
    elif min_odds >=  -9499:
        effective_hold = min(0.01,effective_hold)
    elif min_odds >= -6500 and min_odds <= -4599:
        effective_hold = min(0.015, effective_hold)
    elif min_odds >= -4600 and min_odds <= 3001:
        effective_hold = min(0.02, effective_hold)
    elif min_odds >= -3000 and min_odds <= -2000:
        effective_hold = min(0.03, effective_hold)
    elif min_odds >= -1999 and min_odds <= -1000:
        effective_hold = min(0.045, effective_hold)
    print(f"For Odds of {min_odds} - Effective hold is {effective_hold}")
    # --- 2. Fair probabilities ---
    p_home = american_to_prob(home_price)
    p_away = american_to_prob(away_price)

    if abs((p_home + p_away) - 1.0) > 1e-6:
        raise ValueError("Input prices are not 0-juice")

    # --- 3. Logit transformation ---
    l_home = logit(p_home)
    l_away = logit(p_away)

    # Shape + overround
    shape_scale = 1 + effective_hold
    overround_shift = math.log(1 + effective_hold)

    l_home_j = l_home * shape_scale + overround_shift
    l_away_j = l_away * shape_scale + overround_shift

    p_home_j = inv_logit(l_home_j)
    p_away_j = inv_logit(l_away_j)

    # --- 4. Convert back to odds ---
    return (
        decimal_to_american(prob_to_decimal(p_home_j)),
        decimal_to_american(prob_to_decimal(p_away_j)),
    )

def american_to_fraction_str(odds):
    odds = int(odds)
    frac = Fraction(abs(odds), 100)
    return f"{frac.numerator}/{frac.denominator}"


# def american_to_prob(american):
#     """
#     Convert American odds to implied probability (no juice).
#     """
#     if american > 0:
#         return 100 / (american + 100)
#     else:
#         return -american / (-american + 100)
#
#
# def prob_to_decimal(p):
#     return 1 / p
#
#
# def decimal_to_american(decimal):
#     if decimal >= 2.0:
#         return round((decimal - 1) * 100)
#     else:
#         return round(-100 / (decimal - 1))


def american_juicer_v2(home_price, away_price, hold_pct, eps=1e-9):
    """
    Exact linear juicing with hard safety guards.
    """
    min_odds = min(home_price,away_price)
    if min_odds <= -9500:
        raise ValueError("Odds are <= the minimum, -9500.")
    elif min_odds >=  -9499 and min_odds <= -6501:
        hold_pct = min(0.005,hold_pct)
    elif min_odds >= -6500 and min_odds <= -4601:
        hold_pct = min(0.015, hold_pct)
    elif min_odds >= -4600 and min_odds <= -3001:
        hold_pct = min(0.02, hold_pct)
    elif min_odds >= -3000 and min_odds <= -2000:
        hold_pct = min(0.03, hold_pct)
    elif min_odds >= -1999 and min_odds <= -1000:
        hold_pct = min(0.045, hold_pct)
    # print(f"For Odds of {min_odds} - Effective hold is {hold_pct}")
    # Step 1: fair probabilities
    p_home = Decimal(american_to_prob(home_price))
    p_away = Decimal(american_to_prob(away_price))

    # Step 2: apply linear hold
    scale = Decimal(1 + hold_pct)
    p_home_j = p_home * scale
    p_away_j = p_away * scale

    # --- HARD GUARD ---
    # Linear model is invalid if p >= 1
    if p_home_j >= 1:
        p_home_j = 1 - eps
    if p_away_j >= 1:
        p_away_j = 1 - eps

    # Step 3: convert back
    home_dec = prob_to_decimal(p_home_j)
    away_dec = prob_to_decimal(p_away_j)

    home_american = decimal_to_american(home_dec)
    away_american = decimal_to_american(away_dec)

    return home_american, away_american


def validate_three_way(home_price, away_price, draw_price):
    p_home = Decimal(american_to_prob(home_price))
    p_away = Decimal(american_to_prob(away_price))
    p_draw = Decimal(american_to_prob(draw_price))
    p_total = p_home + p_away + p_draw
    # Reject invalid lines:
    if p_total > 1.01 or p_total < 0.99:
        return False
    return True

def three_way_juicer(home_price, away_price, draw_price, juice_pct, eps=1e-9):
    min_odds = min(home_price,away_price,draw_price)
    if min_odds <= -9500:
        raise ValueError("Odds are <= the minimum, -9500.")
    elif min_odds >=  -9499 and min_odds <= -6501:
        juice_pct = min(0.005, juice_pct)
    elif min_odds >= -6500 and min_odds <= -4601:
        juice_pct = min(0.015, juice_pct)
    elif min_odds >= -4600 and min_odds <= -3001:
        juice_pct = min(0.02, juice_pct)
    elif min_odds >= -3000 and min_odds <= -2000:
        juice_pct = min(0.03, juice_pct)
    elif min_odds >= -1999 and min_odds <= -1000:
        juice_pct = min(0.045, juice_pct)

    # Now convert to Decimal:
    p_home = Decimal(american_to_prob(home_price))
    p_away = Decimal(american_to_prob(away_price))
    p_draw = Decimal(american_to_prob(draw_price))
    juice_pct = Decimal(juice_pct)
    # Juice and compute out:
    jp_home = p_home+(p_home * juice_pct)
    jp_away = p_away+(p_away * juice_pct)
    jp_draw = p_draw+(p_draw * juice_pct)
    if jp_home < 0.5:
        fj_home = 100 / (1/(1-jp_home)-1)
    elif jp_home >= 0.5:
        fj_home = -100 *(jp_home/(1-jp_home))
    if jp_away < 0.5:
        fj_away = 100 / (1/(1-jp_away)-1)
    elif jp_away >= 0.5:
        fj_away = -100 *(jp_away/(1-jp_away))
    if jp_draw < 0.5:
        fj_draw = 100 / (1/(1-jp_draw)-1)
    elif jp_draw >= 0.5:
        fj_draw = -100 *(jp_draw/(1-jp_draw))
    return fj_home,fj_away,fj_draw