import os
import seaborn as sns
import numpy as np
from django.core.wsgi import get_wsgi_application
from matplotlib.lines import Line2D


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "athena.settings")
application = get_wsgi_application()

from game.gdlgdlcore.models import GDLSimulationMatchOddsSummary
import pandas as pd
import torch
import matplotlib.pyplot as plt
from datetime import datetime
from matplotlib.lines import Line2D
from django.core.wsgi import get_wsgi_application
from django.db.models import Q
from game.gdlgdlcore.algos.gpucore import GDLGPUCore
from odds.models import MatchOddsSummary



def simulate_parlay_tickets(
    gdl: GDLGPUCore,
    line_ids: list,
    lines_qs,
    depth=10,
    stake=10.0,
    count=500,
    min_payout=100,
    neg_limit=-100,
    juice=5,
    rounds=100,
    short_lines=False,
) -> list:
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
        short_lines=short_lines,
    )

    for parlay in all_results:
        total_odds = parlay["total_odds"]
        if total_odds <= 0:
            continue

        prob_win = 1.0 / total_odds

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


def batch_simulate_parlay_trials(
    num_runs=1000,
    depth_range=range(5, 21),
    stake=10.0,
    count=100,
    rounds=100,
    neg_limit=-200,
    juice=10
):
    gdl = GDLGPUCore()
    line_queryset = MatchOddsSummary.objects.filter(
        (Q(home_price__gt=0) | Q(away_price__gt=0) | Q(draw_price__gt=0))
    )
    # line_queryset = MatchOddsSummary.objects.filter(
    #     (Q(home_price__gt=100) | Q(away_price__gt=100)) & (Q(home_price__lt=-110)|Q(away_price__lt=-110))
    # )
    # line_queryset = GDLSimulationMatchOddsSummary.objects.all()
    uuids = []
    for lq in line_queryset:
        uuids.append(lq.uuid)
    print(f"Total Records in set: {len(line_queryset)}")
    summary_records = []
    hold_records = []
    for run in range(num_runs):
        print(f"[{run + 1}/{num_runs}] Running simulation batch...")

        all_results = []
        for depth in depth_range:
            results = simulate_parlay_tickets(
                gdl=gdl,
                line_ids=uuids,
                lines_qs=line_queryset,
                depth=depth,
                stake=stake,
                count=count,
                neg_limit=neg_limit,
                rounds=rounds,
                juice=juice,
                short_lines=False
            )
            # print(results)
            all_results.extend(results)
        # print(all_results)
        df = pd.DataFrame(all_results)
        total_wagered = df["total_wagered"].sum()
        total_paid_out = df["total_paid_out"].sum()
        total_bettors = df["num_bettors"].sum()
        total_wins = df["wins"].sum()
        total_losses = df["losses"].sum()
        total_hold = total_wagered - total_paid_out
        hold_pct = (total_hold / total_wagered) * 100 if total_wagered else 0

        # Store summary
        summary_records.append({
            "run_id": run + 1,
            "total_wagered": total_wagered,
            "total_paid_out": total_paid_out,
            "total_hold": total_hold,
            "hold_pct": hold_pct,
            "total_bettors": total_bettors,
            "total_wins": total_wins,
            "total_losses": total_losses
        })

        # Print per-run summary
        print(f"  Total Wagered: ${total_wagered:,.2f}")
        print(f"  Total Paid Out: ${total_paid_out:,.2f}")
        print(f"  House Hold: ${total_hold:,.2f} ({hold_pct:.2f}%)")
        hold_records.append({total_hold,hold_pct})
        print(f"  Player Wins: {int(total_wins)}")
        print(f"  Player Losses: {int(total_losses)}\n")

    # Final summary output
    df_summary = pd.DataFrame(summary_records)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_file = f"parlay_sim_batch_summary_{timestamp}.csv"
    df_summary.to_csv(csv_file, index=False)
    print(f"Saved batch summary to {csv_file}")

    # Plot batch hold percentage
    plt.figure(figsize=(12, 6))
    sns.lineplot(data=df_summary, x="run_id", y="hold_pct", marker="o", linewidth=1.5)

    plt.axhline(0, color="gray", linestyle="--", linewidth=1, label="Break-even (0%)")
    plt.axhline(df_summary["hold_pct"].mean(), color="red", linestyle="--", linewidth=1.2,
                label=f"Avg Hold: {df_summary['hold_pct'].mean():.2f}%")

    plt.title("House Hold % Across Batch Simulations")
    plt.xlabel("Simulation Run")
    plt.ylabel("House Hold (%)")
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.legend()
    plt.tight_layout()

    plot_file = f"parlay_batch_hold_plot.png"
    plt.savefig(plot_file)
    print(f"Plot saved to {plot_file}")
    print(f"Final Hold rate and amounts:")
    total_pct = 0
    for hold_tot,hold_pct in hold_records:
        total_pct += hold_tot
        print(f"  House Hold: ${total_hold:,.2f} ({hold_pct}%)")
    total_pct /= len(hold_records)
    print(f"Total House Hold: {total_pct:.2f}%")

if __name__ == "__main__":
    batch_simulate_parlay_trials(num_runs=5)
