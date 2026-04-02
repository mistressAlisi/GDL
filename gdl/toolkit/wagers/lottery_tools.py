"""
Lottery Wager Tools

Helper functions for creating and managing lottery wagers.
Updated to use LottoMatch and LottoWagerPicks models.
"""

import logging
from decimal import Decimal
from django.utils.timezone import now
from django.db import transaction

from wager.models import Wager, LottoWagerPicks
from account.models import Account
from parameters.models import VHost

logger = logging.getLogger(__name__)


def validate_lottery_numbers_for_game(game, main_numbers, bonus_numbers=None):
    """
    Validate lottery numbers based on game configuration.

    Args:
        game: LotteryGame object with number range configuration
        main_numbers: List of main numbers
        bonus_numbers: Optional list of bonus numbers

    Returns:
        tuple: (is_valid, error_message)
    """
    # Validate main numbers count
    if len(main_numbers) != game.main_count:
        return False, f"Expected {game.main_count} main numbers, got {len(main_numbers)}"

    # Validate main numbers range
    for num in main_numbers:
        if not (game.main_range_min <= num <= game.main_range_max):
            return False, f"Main numbers must be between {game.main_range_min} and {game.main_range_max}"

    # Check for duplicates
    if len(set(main_numbers)) != len(main_numbers):
        return False, "Main numbers must be unique"

    # Validate bonus numbers if required
    if game.bonus_count > 0:
        if not bonus_numbers:
            return False, f"Expected {game.bonus_count} bonus numbers"

        if len(bonus_numbers) != game.bonus_count:
            return False, f"Expected {game.bonus_count} bonus numbers, got {len(bonus_numbers)}"

        for num in bonus_numbers:
            if not (game.bonus_range_min <= num <= game.bonus_range_max):
                return False, f"Bonus numbers must be between {game.bonus_range_min} and {game.bonus_range_max}"

    return True, None


def validate_lottery_numbers(lottery_type, main_numbers, bonus_number):
    """
    Validate lottery numbers based on lottery type rules.
    Legacy function for backwards compatibility.

    Args:
        lottery_type: String ('powerball' or 'megamillions')
        main_numbers: List of main numbers
        bonus_number: Bonus ball number

    Returns:
        tuple: (is_valid, error_message)
    """
    if lottery_type.lower() == 'powerball':
        # Powerball: 5 numbers from 1-69, bonus from 1-26
        if len(main_numbers) != 5:
            return False, "Powerball requires exactly 5 main numbers"

        if not all(1 <= n <= 69 for n in main_numbers):
            return False, "Powerball main numbers must be between 1 and 69"

        if len(set(main_numbers)) != len(main_numbers):
            return False, "Main numbers must be unique"

        if not 1 <= bonus_number <= 26:
            return False, "Powerball bonus must be between 1 and 26"

    elif lottery_type.lower() == 'megamillions':
        # Mega Millions: 5 numbers from 1-70, bonus from 1-25
        if len(main_numbers) != 5:
            return False, "Mega Millions requires exactly 5 main numbers"

        if not all(1 <= n <= 70 for n in main_numbers):
            return False, "Mega Millions main numbers must be between 1 and 70"

        if len(set(main_numbers)) != len(main_numbers):
            return False, "Main numbers must be unique"

        if not 1 <= bonus_number <= 25:
            return False, "Mega Ball must be between 1 and 25"
    else:
        return False, f"Unknown lottery type: {lottery_type}"

    return True, None


def create_lottery_wager_v2(
    vhost,
    account,
    lotto_match_uuid,
    main_numbers,
    bonus_numbers=None,
    risk=None,
    is_quick_pick=False,
    ip_address=None
):
    """
    Create a lottery exact match wager using new LottoMatch system.

    Args:
        vhost: VHost object
        account: Account object
        lotto_match_uuid: UUID of the LottoMatch
        main_numbers: List of main numbers
        bonus_numbers: Optional list of bonus numbers
        risk: Amount wagered (Decimal)
        is_quick_pick: Whether numbers were auto-generated
        ip_address: Optional IP address

    Returns:
        Wager object or raises ValueError
    """
    from lotto.models import LottoMatch, LottoAccountCache

    # Get the LottoMatch from lotto database
    try:
        lotto_match = LottoMatch.objects.using('lotto').get(
            uuid=lotto_match_uuid,
            vhost=vhost,
        )
    except LottoMatch.DoesNotExist:
        raise ValueError("Lotto match not found")

    # Check if match is open for betting
    if lotto_match.status not in ['UPCOMING', 'OPEN']:
        raise ValueError("Betting is closed for this draw")

    if lotto_match.betting_closes and now() > lotto_match.betting_closes:
        raise ValueError("Betting window has closed")

    # Get game configuration
    game = lotto_match.lottery_draw.game

    # Validate numbers
    is_valid, error_msg = validate_lottery_numbers_for_game(game, main_numbers, bonus_numbers)
    if not is_valid:
        raise ValueError(error_msg)

    risk_decimal = Decimal(str(risk))

    # Validate account via LottoAccountCache
    try:
        account_cache = LottoAccountCache.objects.using('lotto').get(
            account_uuid=account.uuid,
            vhost_uuid=vhost.uuid,
        )
        can_wager, error_msg = account_cache.can_place_lotto_wager(risk_decimal)
        if not can_wager:
            raise ValueError(error_msg)
    except LottoAccountCache.DoesNotExist:
        # Fall back to main DB validation
        logger.warning(f"No account cache for {account.uuid}, using main DB balance check")
        if hasattr(account, 'balance') and account.balance < risk_decimal:
            raise ValueError(f"Insufficient balance. Available: ${account.balance}")

    # Calculate potential win
    potential_win = min(
        risk_decimal * lotto_match.payout_multiplier,
        lotto_match.max_payout
    )

    with transaction.atomic(using='default'):
        # Create wager
        wager = Wager.objects.create(
            account=account,
            vhost=vhost,
            type='LE',
            status='P',
            risk=risk_decimal,
            win=potential_win,
            bet_data={
                'lotto_match_uuid': str(lotto_match_uuid),
                'game_name': game.name,
                'draw_date': str(lotto_match.lottery_draw.draw_date),
            },
            current_ip=ip_address
        )

        # Create picks
        picks = LottoWagerPicks(
            wager=wager,
            lotto_match_uuid=lotto_match_uuid,
            is_quick_pick=is_quick_pick,
        )
        picks.set_picks(main_numbers, bonus_numbers or [])

        # Check for duplicate
        is_duplicate, existing_uuid = picks.check_duplicate()
        if is_duplicate:
            raise ValueError("You already have a wager with these numbers on this draw")

        picks.save()

        # Debit account
        from cashier.toolkit import account_debit_wager_risk
        account_debit_wager_risk(account, wager, risk_decimal)

    logger.info(
        f"Created lottery wager {wager.uuid} for {account.acctnum}: "
        f"${risk} on {game.name} - Numbers: {main_numbers}+{bonus_numbers or []}"
    )

    return wager


def create_lottery_wager(
    vhost,
    account,
    lottery_type,
    main_numbers,
    bonus_number,
    risk,
    domain=None,
    ip_address=None
):
    """
    Create a lottery exact match wager.
    Legacy function - uses LottoMatch if available, falls back to old system.

    Args:
        vhost: VHost object
        account: Account object
        lottery_type: String ('powerball' or 'megamillions')
        main_numbers: List of main numbers
        bonus_number: Bonus ball number
        risk: Amount wagered
        domain: Optional domain
        ip_address: Optional IP address

    Returns:
        Wager object or raises ValueError
    """
    from lotto.models import LottoMatch

    # Validate numbers using legacy validator
    is_valid, error_msg = validate_lottery_numbers(lottery_type, main_numbers, bonus_number)
    if not is_valid:
        raise ValueError(error_msg)

    # Try to find a LottoMatch for this lottery type
    lotto_match = LottoMatch.objects.using('lotto').filter(
        vhost=vhost,
        status__in=['UPCOMING', 'OPEN'],
        lottery_draw__game__slug__icontains=lottery_type.lower(),
        betting_closes__gte=now(),
    ).order_by('lottery_draw__draw_date').first()

    if lotto_match:
        # Use new system
        return create_lottery_wager_v2(
            vhost=vhost,
            account=account,
            lotto_match_uuid=lotto_match.uuid,
            main_numbers=main_numbers,
            bonus_numbers=[bonus_number] if bonus_number else [],
            risk=risk,
            is_quick_pick=False,
            ip_address=ip_address
        )

    # Fallback to old system if no LottoMatch found
    logger.warning(f"No LottoMatch found for {lottery_type}, using legacy system")

    from matches.models import Match
    from dataengine.drivers.collectapi.models import LotteryType, LotteryPayoutConfig

    # Get upcoming lottery match from old system
    match = Match.objects.filter(
        sport__name__icontains=lottery_type,
        finished=False,
        open=True,
        commence_time__gte=now()
    ).order_by('commence_time').first()

    if not match:
        raise ValueError(f"No upcoming {lottery_type} draw available for betting")

    # Check if draw is not too close
    from datetime import timedelta
    cutoff_time = match.commence_time - timedelta(hours=1)
    if now() > cutoff_time:
        raise ValueError(f"Betting closed for {lottery_type} draw on {match.commence_time.date()}")

    # Get payout configuration
    try:
        lottery_type_obj = LotteryType.objects.get(
            vhost=vhost,
            slug=f"usa-{lottery_type.lower()}"
        )
        payout_config = LotteryPayoutConfig.objects.get(
            vhost=vhost,
            lottery_type=lottery_type_obj,
            active=True
        )
        multiplier = payout_config.multiplier
        max_payout = payout_config.max_payout

        if risk < payout_config.min_wager:
            raise ValueError(f"Minimum wager is ${payout_config.min_wager}")
        if risk > payout_config.max_wager:
            raise ValueError(f"Maximum wager is ${payout_config.max_wager}")
    except (LotteryType.DoesNotExist, LotteryPayoutConfig.DoesNotExist):
        logger.warning(f"No payout config for {lottery_type}, using defaults")
        multiplier = 10000
        max_payout = Decimal('100000')
        if risk < 1:
            raise ValueError("Minimum wager is $1")
        if risk > 100:
            raise ValueError("Maximum wager is $100")

    risk_decimal = Decimal(str(risk))
    potential_win = min(risk_decimal * multiplier, max_payout)

    with transaction.atomic():
        if hasattr(account, 'balance') and account.balance < risk_decimal:
            raise ValueError(f"Insufficient balance. Available: ${account.balance}")

        wager = Wager.objects.create(
            account=account,
            vhost=vhost,
            type='LE',
            status='P',
            match=match,
            risk=risk_decimal,
            win=potential_win,
            base_spread=multiplier,
            bet_data={
                "lottery_type": lottery_type.lower(),
                "user_numbers": sorted(main_numbers),
                "bonus_number": bonus_number,
                "payout_multiplier": multiplier,
                "max_payout": float(max_payout),
                "draw_date": str(match.commence_time.date())
            },
            current_ip=ip_address
        )

        # Also create LottoWagerPicks for consistency
        picks = LottoWagerPicks(
            wager=wager,
            lotto_match_uuid=None,  # No LottoMatch available
            is_quick_pick=False,
        )
        picks.set_picks(main_numbers, [bonus_number] if bonus_number else [])
        picks.save()

        from cashier.toolkit import account_debit_wager_risk
        account_debit_wager_risk(account, wager, risk_decimal)

        logger.info(
            f"Created lottery wager {wager.uuid} for {account.acctnum}: "
            f"${risk} on {lottery_type} - Numbers: {main_numbers}+{bonus_number}"
        )

        return wager


def get_lottery_wager_status(wager):
    """
    Get detailed status of a lottery wager.

    Args:
        wager: Wager object

    Returns:
        dict: Status information
    """
    if wager.type != 'LE':
        return {"error": "Not a lottery wager"}

    status = {
        "wager_id": str(wager.uuid),
        "account": wager.account.acctnum,
        "risk": float(wager.risk),
        "potential_win": float(wager.win),
        "status": wager.get_status_display(),
        "graded": wager.graded,
        "executed": wager.executed
    }

    # Get picks from LottoWagerPicks if available
    try:
        picks = wager.lotto_picks
        status["user_numbers"] = picks.get_picks_list()
        status["user_bonus"] = picks.get_bonus_list()
        status["matched_main"] = picks.matched_main
        status["matched_bonus"] = picks.matched_bonus
        status["is_exact_match"] = picks.is_exact_match
    except LottoWagerPicks.DoesNotExist:
        # Fall back to bet_data
        status["user_numbers"] = wager.bet_data.get("user_numbers")
        status["user_bonus"] = wager.bet_data.get("bonus_number")

    status["lottery_type"] = wager.bet_data.get("lottery_type")
    status["draw_date"] = wager.bet_data.get("draw_date")

    # Add grader history if available
    if wager.grader_history:
        status["result"] = {
            "exact_match": wager.grader_history.get("exact_match") or wager.grader_history.get("is_exact_match"),
            "winning_numbers": wager.grader_history.get("winning_numbers") or wager.grader_history.get("winning_main"),
            "winning_bonus": wager.grader_history.get("winning_bonus"),
            "payout": wager.grader_history.get("payout")
        }

    return status


def get_upcoming_lottery_matches(vhost=None):
    """
    Get all upcoming lottery matches available for betting.
    Uses LottoMatch from lotto database.

    Args:
        vhost: Optional VHost filter

    Returns:
        list: List of upcoming lottery matches
    """
    from lotto.models import LottoMatch

    query = LottoMatch.objects.using('lotto').filter(
        status__in=['UPCOMING', 'OPEN'],
    ).select_related('lottery_draw', 'lottery_draw__game').order_by('lottery_draw__draw_date')

    if vhost:
        query = query.filter(vhost=vhost)

    matches = []
    for match in query:
        draw = match.lottery_draw
        game = draw.game

        betting_open = True
        if match.betting_closes and now() > match.betting_closes:
            betting_open = False

        matches.append({
            "lotto_match_uuid": str(match.uuid),
            "game_name": game.name,
            "game_slug": game.slug,
            "draw_date": draw.draw_date,
            "draw_datetime": draw.draw_datetime,
            "betting_open": betting_open,
            "betting_opens": match.betting_opens,
            "betting_closes": match.betting_closes,
            "payout_multiplier": float(match.payout_multiplier),
            "max_payout": float(match.max_payout),
            "main_count": game.main_count,
            "main_range": (game.main_range_min, game.main_range_max),
            "bonus_count": game.bonus_count,
            "bonus_range": (game.bonus_range_min, game.bonus_range_max) if game.bonus_count > 0 else None,
        })

    return matches
