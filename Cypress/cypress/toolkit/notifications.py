from django.shortcuts import render

from toolkit.wagers.scoring_tools import calculate_straight_bet_wins, calculate_moneyline_payout
from wager.models import Wager


def parse_and_render_notification(notification,request):
    if notification.type == "wa":
        wager = Wager.objects.get(uuid=notification.wager)
        if not notification.wager_won:
            if wager.type == "ST":
                return render(request,"sportsbook/index/notifications/lost_straight_wager.html",{"wager":wager})
            elif wager.type == "PA":
                return render(request, "sportsbook/index/notifications/lost_parlay_wager.html", {"wager": wager})
            elif wager.type == "TO":
                return render(request, "sportsbook/index/notifications/lost_totals_wager.html", {"wager": wager})
            elif wager.type == "ML":
                return render(request, "sportsbook/index/notifications/lost_ml_wager.html", {"wager": wager})
            elif wager.type == "LI":
                return render(request, "sportsbook/index/notifications/lost_live_wager.html", {"wager": wager})
            elif wager.type == "SP":
                return render(request, "sportsbook/index/notifications/lost_spread_wager.html", {"wager": wager})
            else:
                return render(request, "sportsbook/index/notifications/lost_generic_wager.html", {"wager": wager})

        elif notification.wager_won:
            if wager.type.startswith("S"):
                wager_won = calculate_straight_bet_wins(wager.risk,wager.match.base_line)
                winnings = wager_won + wager.risk
                if wager.type == "ST":
                    return render(request, "sportsbook/index/notifications/won_straight_wager.html", {"wager": wager,"won":wager_won,"winnings":winnings})
                elif wager.type == "SP":
                    return render(request, "sportsbook/index/notifications/won_spread_wager.html",{"wager": wager, "won": wager_won, "winnings": winnings})
            elif wager.type == "TO":
                wager_won = calculate_straight_bet_wins(wager.risk,wager.match.base_line)
                winnings = wager_won + wager.risk
                return render(request,"sportsbook/index/notifications/won_totals_wager.html",{"wager": wager,"won":wager_won,"winnings":winnings})
            elif wager.type == "ML":
                wager_won = calculate_moneyline_payout(wager.risk,wager.match.base_line)
                winnings = wager_won + wager.risk
                return render(request,"sportsbook/index/notifications/won_ml_wager.html",{"wager": wager,"won":wager_won,"winnings":winnings})
            elif wager.type == "PA":
                winnings = wager.win + wager.risk
                return render(request,"sportsbook/index/notifications/won_parlay_wager.html",{"wager": wager,"won":wager.win,"winnings":winnings})
            elif wager.type == "LI":
                winnings = wager.win + wager.risk
                return render(request,"sportsbook/index/notifications/won_live_wager.html",{"wager": wager,"won":wager.win,"winnings":winnings})
            else:
                wager_won = wager.win
                winnings = wager_won
                return render(request, "sportsbook/index/notifications/win_generic_base.html",
                              {"wager": wager, "won": wager_won, "winnings": winnings})



    return render(request, "sportsbook/index/notifications/generic.html", {"notification": notification})