import os
import seaborn as sns
import numpy as np
from django.core.wsgi import get_wsgi_application
from matplotlib.lines import Line2D

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "athena.settings")
application = get_wsgi_application()

import torch
import pandas as pd
import matplotlib.pyplot as plt
from decimal import Decimal
from django.db.models import Q
from game.gdlgdlcore.algos.gpucore import GDLGPUCore
from odds.models import MatchOddsSummary


def simulate_parlay_tickets(
    gdl: GDLGPUCore,
    line_ids: list,
    lines_qs,
    depth=10,
    stake=10.0,
    count=100,
    min_payout=100,
    neg_limit=-100,
    juice=5,
    rounds=1000,
) -> list:
    """
    Simulates house hold over many rounds using real-world generated parlays.
    Returns list of dictionaries with results per depth.
    """
    results = []
    all_results, _ = gdl._run_gdl_algo1(
        line_ids=line_ids,
        lines_qs=lines_qs,
        min_payout=min_payout,
        depth=depth,
        stake=stake,
        count=count,
        serialise=True,
        neg_limit=neg_limit,
        juice=juice,
    )

    for parlay in all_results:
        total_odds = parlay["total_odds"]
        if total_odds <= 0:
            continue

        prob_win = 1.0 / total_odds
        # prob_win = min(prob_win,), 0.999999)

        num_bettors = rounds
        wins = torch.rand(num_bettors) < prob_win

        payouts = torch.tensor(wins, dtype=torch.float32) * stake * total_odds
        wagered = stake * num_bettors
        paid_out = payouts.sum().item()

        hold = wagered - paid_out
        hold_pct = (hold / wagered) * 100

        results.append({
            "legs": len(parlay["odds"]),
            "total_odds": total_odds,
            "win_probability": prob_win,
            "total_wagered": wagered,
            "total_paid_out": paid_out,
            "hold_pct": hold_pct,
            "wins": wins.sum().item(),
            "losses": num_bettors - wins.sum().item(),
            "num_bettors": num_bettors,
        })

    return results


def main():
    gdl = GDLGPUCore()

    _lines = MatchOddsSummary.objects.filter(

        (Q(home_price__gt=0) | Q(away_price__gt=0) | Q(draw_price__gt=0))
    )

    all_results = []

    # Run simulation for legs from 2 to 20
    for depth in range(7, 21):
        print(f"Simulating parlays with {depth} legs...")
        results = simulate_parlay_tickets(
            gdl=gdl,
            line_ids=_lines,
            lines_qs=MatchOddsSummary.objects.all(),
            depth=depth,
            stake=5.0,
            count=250,
            neg_limit=-110,
            rounds=5000,
            juice=10
        )
        all_results.extend(results)

    # Create DataFrame
    df = pd.DataFrame(all_results)
    df.to_csv("real_parlay_sim_results_multi_depth.csv", index=False)

    # Aggregate summary stats across all legs
    total_bettors = df["num_bettors"].sum()
    total_wagered = df["total_wagered"].sum()
    total_paid_out = df["total_paid_out"].sum()
    total_wins = df["wins"].sum()
    total_losses = df["losses"].sum()
    total_hold = total_wagered - total_paid_out
    total_hold_pct = (total_hold / total_wagered) * 100 if total_wagered else 0

    print("\n===== SIMULATION SUMMARY =====")
    print(f"Total Bettors Simulated: {total_bettors}")
    print(f"Total Bets Wagered ($): {total_wagered:,.2f}")
    print(f"Total Paid Out ($): {total_paid_out:,.2f}")
    print(f"Total House Hold ($): {total_hold:,.2f}")
    print(f"Total House Hold (%): {total_hold_pct:.4f}%")
    print(f"Total Player Wins: {total_wins}")
    print(f"Total Player Losses: {total_losses}")

    df['return_pct'] = (df['total_paid_out'] / df['total_wagered']) * 100  # This is % payout to players

    plt.figure(figsize=(12, 7))

    unique_legs = sorted(df['legs'].unique())
    palette = sns.color_palette("viridis", len(unique_legs))
    leg_color_map = {leg: palette[i] for i, leg in enumerate(unique_legs)}
    colors = df['legs'].map(leg_color_map)

    # Scatter plot: total odds vs. player return %, color-coded by legs
    plt.scatter(df["total_odds"], df["return_pct"], c=colors, alpha=0.6, edgecolor='k', linewidth=0.2)

    plt.xscale("log")
    plt.xlabel("Total Parlay Odds (Log Scale)")
    plt.ylabel("Player Return (%)")
    plt.title("Player Return % vs Real Parlay Odds (Color by Legs)")
    plt.ylim(0, 150)  # 0-100% returns
    plt.grid(True, which="both", linestyle="--", linewidth=0.5)
    plt.axhline(100, color="gray", linestyle="--", linewidth=0.8, label="Break-even (100%)")

    # Binning odds in log space
    df["log_odds"] = np.log10(df["total_odds"])
    bins = np.linspace(df["log_odds"].min(), df["log_odds"].max(), 15)
    df["odds_bin"] = pd.cut(df["log_odds"], bins)

    # Compute binned average returns
    binned = df.groupby("odds_bin")["return_pct"].mean().reset_index()
    bin_centers = [10 ** (interval.mid) for interval in binned["odds_bin"]]
    # plt.plot(bin_centers, binned["return_pct"], color="black", linewidth=2.5, label="Binned Avg Return")

    # Legend for legs
    legend_elements = [Line2D([0], [0], marker='o', color='w', label=f"{leg} Legs",
                              markerfacecolor=leg_color_map[leg], markersize=8)
                       for leg in unique_legs]
    legend_elements.append(Line2D([0], [0], color='black', lw=2, label='Binned Avg Return'))
    plt.legend(handles=legend_elements, title="Parlay Legs")

    plt.tight_layout()
    plt.savefig("parlay_player_return_binned_colored.png")
    plt.show()


if __name__ == "__main__":
    main()
