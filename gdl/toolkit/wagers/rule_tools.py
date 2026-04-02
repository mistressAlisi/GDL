from cashier.models import ParlayPayoutRulesetEntry


def parlay_leg_ruleset_builder(account):
    if account.account_level.parlay_ruleset:
        parlayRuleset = ParlayPayoutRulesetEntry.objects.filter(ruleset=account.account_level.parlay_ruleset).order_by("parlay_legs")
    elif account.parlay_rules:
        parlayRuleset = ParlayPayoutRulesetEntry.objects.filter(ruleset=account.parlay_rules).order_by("parlay_legs")
    else:
        raise Exception(f"No parlay rules available for Account {account.acctnum}!")
        return False

    levels = {

    }
    min_legs = 100
    max_legs = 0
    if account.account_level.fiat_enabled:
        min_bet = account.account_level.min_play_amount_fiat
        max_bet = account.account_level.max_play_amount_fiat
    else:
        min_bet = account.account_level.min_play_amount_cryp
        max_bet = account.account_level.max_play_amount_cryp
    for parlayRule in parlayRuleset:
        key = parlayRule.parlay_legs
        if key not in levels:
            levels[key] = {
                "losses":[],
                "payouts":[],
                "min_bet":float(min(min_bet,parlayRule.min_bet)),
                "max_bet":float(min(max_bet,parlayRule.max_bet)),
                "juice":parlayRule.juice_percentage
            }
        levels[key]["losses"].append(parlayRule.max_losses)
        levels[key]["payouts"].append(parlayRule.players_percentage)
        if parlayRule.parlay_legs < min_legs:
            min_legs = parlayRule.parlay_legs
        if parlayRule.parlay_legs > max_legs:
            max_legs = parlayRule.parlay_legs

    return levels,min_legs,max_legs