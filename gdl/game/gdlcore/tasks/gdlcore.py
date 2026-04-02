import torch
from datetime import timedelta

from django.conf import settings
from django.db.models import Q
from django.utils import timezone
from django.utils.timezone import now

from game.gdlcore.models import GDLTicketCache
from game.gdlfront.models import GDLFilterSettingsSportEntry
from odds.models import MatchOddsSummary
from grader.toolkit.parlays import american_juicer

if settings.GDL_USE_GPU:
    if settings.GDL_USE_MAX:
        from game.gdlcore.algos.gpucore_max import GDLGPUCore
    else:
        from game.gdlcore.algos.gpucore_narrow import GDLGPUCore
    GDL = GDLGPUCore()
else:
    from game.gdlgdlcore.algos.core import GDLCore
    GDL = GDLCore()



def task_header(arg=False):
    logger.info("Task Header: Starting Task!")
    return []


def collect_results(worker_results):
    logger.info("Collecting results from all workers")
    return worker_results


def gdl_algo_worker(_lines,min_payout,depth,stake,save_to_cache=False):
    # logger.info(f"Starting GDL Algo: {min_payout}/{depth}/{stake}!")
    # print(f"Starting GDL Algo: {min_payout}/{depth}/{stake}!")
    lines = MatchOddsSummary.objects.filter(uuid__in=_lines)
    col_data, lines = GDL._run_gdl_algo1(_lines,lines, min_payout, depth,stake)
    if save_to_cache:
        gdlcol = GDLTicketCache(expires=timezone.now()+timedelta(minutes=30),min_payout=min_payout,depth=depth,stake=stake,ticket_data=col_data)
        gdlcol.save()
        # print("saved")
        return True
    return col_data


def gdl_algo_worker_gpu(_lines,min_payout,depth,stake,count,negative_lim=-200,serialise=True):
    logger.info(f"Starting GDL GPU Algo: {min_payout}/{depth}/{stake}!")
    print(f"Starting GDL GPU Algo: {min_payout}/{depth}/{stake}!")
    lines = MatchOddsSummary.objects.filter(uuid__in=_lines)
    col_data, lines = GDL._run_gdl_algo1(lines, min_payout, depth, stake, count, negative_lim, serialise)
    return col_data


def gdl_algo_parallel_by_count(min_payout=6000, count=32, depth=7, stake=6, negative_limit=-150,juice=0.05,events_within=None,sports_filter=[],window_pct=5,debug=False):
    # Fetch all active, matching lines
    if sports_filter != []:
        final_groups = []
        final_sports = []
        for sport in sports_filter:
            sportFilterObj = GDLFilterSettingsSportEntry.objects.get(uuid=sport)
            if sportFilterObj.sport:
                final_sports.append(sportFilterObj.sport)
            else:
                final_groups.append(sportFilterObj.group)
        _lines = MatchOddsSummary.objects.filter(Q(match__sport__in=final_sports)|Q(match__sport__group__in=final_groups)).filter(
            Q(match__active=True) & Q(match__open=True) & Q(match__finished=False) & Q(
                match__commence_time__gte=now()) &
            (Q(home_price__gt=0) | Q(away_price__gt=0) | Q(draw_price__gt=0))
        )
    else:
        _lines = MatchOddsSummary.objects.filter(
            Q(match__active=True) & Q(match__open=True) & Q(match__finished=False) & Q(match__commence_time__gte=now()) &
            (Q(home_price__gt=0) | Q(away_price__gt=0) | Q(draw_price__gt=0))
        )
    # Filter by cutoff if present:
    if events_within:
        cutoff_time = now() + timedelta(seconds=events_within)
        _lines = _lines.filter(match__commence_time__lte=cutoff_time)
    line_ids = [str(line.uuid) for line in _lines]
    # There's no need for GPU entry if we're doing a single-leg parlay:
    total_risk = min_payout / stake
    total_lines = len(_lines)
    # print("total_lines", total_lines,"total_risk", total_risk)
    min_win = min_payout-(min_payout * (window_pct/100))
    max_win = min_payout+(min_payout* (window_pct/100))
    # print(min_win,max_win)
    chosen_lines = []
    total_trials = 0
    if depth == 1:
        results = []
        total_gen = 0
        total_lines = len(_lines)
        max_trials = count * 1000  # Prevent infinite loop
        total_trials = 0
        chosen_indices = set()

        logger.info(f"Entering GDL Algo in CPU Single-Parlay Leg mode for {count} tickets and {total_lines} lines...")

        generator = torch.Generator(device="cpu")
        cpu_gen = torch.Generator(device="cpu").manual_seed(generator.initial_seed())

        # Initial window (±50% of min_win)
        window_pct = 0.5
        adaptive_min_win = min_win * (1 - window_pct)
        adaptive_max_win = min_win * (1 + window_pct)

        while total_gen < count and total_trials < max_trials:
            total_trials += 1
            rand_idx = torch.randint(0, total_lines, (1,), generator=cpu_gen).item()

            if rand_idx in chosen_indices:
                continue

            line = _lines[rand_idx]
            chosen_indices.add(rand_idx)

            hp, ap, dp = american_juicer(
                line.home_price, line.away_price, line.draw_price,
                juice_pct=juice, use_decimal=True
            )

            label, value = max(
                [("home_price", hp), ("away_price", ap), ("draw_price", dp)],
                key=lambda x: x[1]
            )

            mvalue = value * stake

            if adaptive_min_win <= mvalue <= adaptive_max_win:
                col_data = {
                    "odds": [[str(line.uuid), line.match.name]],
                    "odds_prices": [value],
                    "odds_types": [label],
                    "odds_sports": [[
                        str(line.match.sport.uuid) if line.match.sport else None,
                        line.match.sport.title if line.match.sport else None,
                        line.match.sport.group.name if line.match.sport and line.match.sport.group else None,
                        line.match.sport.group.icon if line.match.sport and line.match.sport.group else None,
                    ]],
                    "odds_muuids": [str(line.match.uuid)],
                    "odds_lines": [str(line.uuid)],
                    "total_odds": value,
                    "total_returns": round(value * stake, 0),
                }
                results.append(col_data)
                total_gen += 1

            # Not in window → back off
            if total_trials % (count * 10) == 0:
                adaptive_min_win *= 0.95  # Decrease lower bound by 5%
                adaptive_max_win *= 1.05  # Increase upper bound by 5%

        if total_gen < count:
            logger.warning(
                f"GDL CPU Algo: Only generated {total_gen} tickets out of {count} after {total_trials} trials.")

        return results

    # Now we're past that, let's talk about parallel:
    # Use GPU if enabled
    if (getattr,"GDL_USE_GPU",True) and not torch.cuda.is_available():
        print("****WARNING!*** Unable to Initialise PyTorch/CUDA/ROCM. GPU Accelerator unavailable... This will probably NOT WORK!*****")
        logger.warning(
            "****WARNING!*** Unable to Initialise PyTorch/CUDA/ROCM. GPU Accelerator unavailable... This will probably NOT WORK!*****")
    if getattr(settings, "GDL_USE_GPU", True) and torch.cuda.is_available():
        gpu_core = GDLGPUCore()
        col_data_list, _ = gpu_core._run_gdl_algo1(
            line_ids=line_ids,
            lines_qs=_lines,
            min_payout=min_payout,
            depth=depth,
            stake=stake,
            count=count,
            serialise=True,
            neg_limit=negative_limit,
            debug=debug,
            juice=juice
        )
        # print(col_data_list)
        return col_data_list

    # CPU fallback – run workers in parallel
    workers = [gdl_algo_worker.s(line_ids, min_payout, depth, stake) for _ in range(count)]
    job = chord(group(workers))(collect_results.s())
    return job

def gdl_algo_parallel_cache_count(min_payout=6000, count=128, depth=7,stake=6):
    logger.info(f"Starting GDL Algo for Cache: {min_payout}/{depth}/{stake}!")
    GDLTicketCache.objects.filter(expires__lt=timezone.now()).delete()
    # print(f"Starting GDL Algo for Cache: {min_payout}/{depth}/{stake}!")
    _lines = MatchOddsSummary.objects.filter(
        Q(match__active=True) & Q(match__open=True) &
        (Q(home_price__gt=0) | Q(away_price__gt=0) | Q(draw_price__gt=0))
    )
    line_ids = [str(line.uuid) for line in _lines]

    # Create group of gdl_algo_worker tasks (in parallel)
    workers = [gdl_algo_worker.s(line_ids, min_payout, depth,stake,True) for _ in range(count)]
    # Run them in parallel, then call collect_results with all outputs
    job = chord(group(workers))(collect_results.s())

    return job
