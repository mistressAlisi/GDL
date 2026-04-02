from decimal import Decimal
from email.mime import base


def calculate_spread_total_wins(wagered=100, base=110, reward=100):
    return int(((reward / abs(base)) + 1) * wagered)

def calculate_parlay_total_wins(wagered,total_odds):
    if wagered == 0 or total_odds == 0:
        return 0
    if (type(wagered) != Decimal):
        wagered = Decimal(wagered)
    if (type(total_odds) != Decimal):
        total_odds = Decimal(total_odds)
    return wagered*total_odds

def calculate_straight_bet_wins(risk=100,base=110):
    if base == 0 or risk == 0:
        return 0
    if (type(risk) != Decimal):
        risk = Decimal(risk)
    if (type(base) != Decimal):
        base = Decimal(base)
    if (base > 0):
        to_win = round(risk * Decimal(base / 100)) + risk
    else:
        to_win = round(risk  +Decimal(100/abs(base)) * risk)
    return to_win

def decimal_to_moneyline(decimal_odds,append_plus=False):
    if decimal_odds == 0 or decimal_odds == 1:
        return 0
    if (type(decimal_odds) != Decimal):
        decimal_odds = Decimal(decimal_odds)
    if decimal_odds < 2.0:
        return int(-100 / Decimal(decimal_odds - 1))
    else:
        if not append_plus:
            return int(100 * (decimal_odds - 1))
        else:
            return f"+{int(100 * (decimal_odds - 1))}"


def calculate_moneyline_payout(risk, ml):
    if (type(risk) != int):
        risk = int(risk)
    if (type(ml) != int):
        ml = int(ml)
    if ml > 0:
        return int((risk*(ml/100)+risk))
    elif ml <0:
        return int((risk*(100/abs(ml))))+risk
    else:
        return 0


def calculate_outright_payout(risk=1000,base=100):
    if base == 0 or risk == 0:
        return 0
    return risk + (risk * (base/100))

def calculate_decimal_payout(risk=1000,decimal_base=1.0):
    if base == 0 or risk == 0:
        return 0
    return risk * decimal_base


def decimal_to_american(decimal_odds,precision=2):
    if decimal_odds >= 2.0:
        # For decimal odds >= 2.0, calculate positive American odds
        american_odds = (decimal_odds - 1) * 100
    else:
        # For decimal odds < 2.0, calculate negative American odds
        american_odds = -100 / (decimal_odds - 1)

    return round(american_odds,precision)

def odd_rounder(value):
    if value is "": return 0
    value = Decimal(value)
    sign= 1
    integer_part = int(value)
    if value == 0:
        return 0
    elif value < 0:
        value = value*-1
        sign = -1
        integer_part = int(value)
    elif value >= 1.0:
        integer_part = int(value)
    decimal_part = Decimal(value) - integer_part
    if decimal_part <= 0.33:
        return integer_part*sign
    elif decimal_part <= 0.7:
        return float(f"{integer_part}.5")*sign
    else:
        return float((integer_part+1)*sign)
