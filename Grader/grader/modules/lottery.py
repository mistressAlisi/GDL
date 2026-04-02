"""
Lottery Grader Module

Grader for lottery exact match wagers.
Updated to use LottoWagerPicks for number storage.
"""

import logging
from decimal import Decimal
from django.db import transaction
from django.utils.timezone import now

from grader.engine.core import GraderEngine
from wager.models import Wager, LottoWagerPicks
from wager.signals.core import signal_wager_qualified


class LotteryGrader(GraderEngine):
    """Grader for lottery exact match wagers"""

    MAX_PAYOUT = 100000  # $100k max payout cap

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(__name__)

    def qualify_exact_lottery_wager(self, wagerObj):
        """
        Qualify lottery wager - only wins if ALL numbers match exactly.

        Supports both new LottoMatch system and legacy collectapi system.

        Args:
            wagerObj: Wager object to qualify

        Returns:
            bool: True if exact match (winner), False otherwise, None if cannot grade
        """
        if wagerObj.type != 'LE':
            self.logger.warning(f"Wager {wagerObj.uuid} is not a lottery wager")
            return None

        if wagerObj.graded or wagerObj.executed:
            self.logger.warning(f"Wager {wagerObj.uuid} already qualified/executed")
            return None

        # Try to get picks from LottoWagerPicks first
        try:
            picks = wagerObj.lotto_picks
            return self._grade_with_picks(wagerObj, picks)
        except LottoWagerPicks.DoesNotExist:
            # Fall back to legacy bet_data grading
            return self._grade_with_bet_data(wagerObj)

    def _grade_with_picks(self, wagerObj, picks):
        """
        Grade wager using LottoWagerPicks and LottoMatch.

        Args:
            wagerObj: Wager object
            picks: LottoWagerPicks object

        Returns:
            bool: True if winner, False if loser, None if cannot grade
        """
        from lotto.models import LottoMatch

        lotto_match_uuid = picks.lotto_match_uuid
        if not lotto_match_uuid:
            self.logger.warning(
                f"Wager {wagerObj.uuid} has picks but no lotto_match_uuid"
            )
            return self._grade_with_bet_data(wagerObj)

        # Get LottoMatch from lotto database
        try:
            lotto_match = LottoMatch.objects.using('lotto').get(uuid=lotto_match_uuid)
        except LottoMatch.DoesNotExist:
            self.logger.error(f"No LottoMatch found: {lotto_match_uuid}")
            return None

        # Check if draw has results
        if not lotto_match.has_results:
            self.logger.info(f"LottoMatch {lotto_match_uuid} has no results yet")
            return None

        winning = lotto_match.get_winning_numbers()
        winning_main = sorted(winning['main'])
        winning_bonus = winning['bonus'] or []

        user_main = picks.get_picks_list()
        user_bonus = picks.get_bonus_list()

        # Check for exact match
        exact_match = (
            user_main == winning_main and
            user_bonus == winning_bonus
        )

        with transaction.atomic():
            # Update picks
            picks.matched_main = len(set(user_main) & set(winning_main))
            picks.matched_bonus = len(set(user_bonus) & set(winning_bonus))
            picks.is_exact_match = exact_match
            picks.save()

            if exact_match:
                # Winner!
                wagerObj.status = "W"

                # Calculate payout using LottoMatch configuration
                calculated_payout = Decimal(str(wagerObj.risk)) * lotto_match.payout_multiplier
                wagerObj.win = min(calculated_payout, lotto_match.max_payout)

                wagerObj.grader_history = {
                    "exact_match": True,
                    "winning_main": winning_main,
                    "winning_bonus": winning_bonus,
                    "user_main": user_main,
                    "user_bonus": user_bonus,
                    "matched_main": picks.matched_main,
                    "matched_bonus": picks.matched_bonus,
                    "payout": float(wagerObj.win),
                    "lotto_match_uuid": str(lotto_match_uuid),
                    "grader": "LotteryGrader._grade_with_picks"
                }

                self.logger.info(
                    f"Wager {wagerObj.uuid} WON! Exact match. "
                    f"Payout: ${wagerObj.win} (Risk: ${wagerObj.risk})"
                )
            else:
                # Loser
                wagerObj.status = "L"
                wagerObj.grader_history = {
                    "exact_match": False,
                    "winning_main": winning_main,
                    "winning_bonus": winning_bonus,
                    "user_main": user_main,
                    "user_bonus": user_bonus,
                    "matched_main": picks.matched_main,
                    "matched_bonus": picks.matched_bonus,
                    "lotto_match_uuid": str(lotto_match_uuid),
                    "grader": "LotteryGrader._grade_with_picks"
                }

                self.logger.info(
                    f"Wager {wagerObj.uuid} lost. No exact match. "
                    f"User: {user_main}+{user_bonus}, "
                    f"Winning: {winning_main}+{winning_bonus}"
                )

            wagerObj.graded = True
            wagerObj.graded_at = now()
            wagerObj.closed = False  # Will be closed by execute_close
            wagerObj.save()

            # Send qualification signal
            signal_wager_qualified.send(
                sender=self.__class__,
                wagerObj=wagerObj,
                account=wagerObj.account,
                vhost=wagerObj.vhost
            )

            return exact_match

    def _grade_with_bet_data(self, wagerObj):
        """
        Grade wager using legacy bet_data and collectapi LotteryDraw.

        Args:
            wagerObj: Wager object

        Returns:
            bool: True if winner, False if loser, None if cannot grade
        """
        from dataengine.drivers.collectapi.models import LotteryDraw, LotteryPayoutConfig

        with transaction.atomic():
            try:
                # Get the lottery draw based on match date
                lottery_type_slug = wagerObj.bet_data.get("lottery_type")
                draw_date = wagerObj.match.commence_time.date()

                lottery_draw = LotteryDraw.objects.get(
                    lottery_type__slug=f"usa-{lottery_type_slug}",
                    draw_date=draw_date
                )

                # Check if draw has results
                if not lottery_draw.main_numbers:
                    self.logger.info(f"Draw for {draw_date} has no results yet")
                    return None

                # Compare user numbers with winning numbers
                user_numbers = sorted(wagerObj.bet_data.get("user_numbers", []))
                winning_numbers = sorted(lottery_draw.main_numbers)
                user_bonus = wagerObj.bet_data.get("bonus_number")
                winning_bonus = lottery_draw.bonus_numbers[0] if lottery_draw.bonus_numbers else None

                # Check for exact match
                exact_match = (
                    user_numbers == winning_numbers and
                    user_bonus == winning_bonus
                )

                if exact_match:
                    # Winner! Calculate payout
                    wagerObj.status = "W"

                    # Get payout configuration
                    try:
                        payout_config = LotteryPayoutConfig.objects.get(
                            vhost=wagerObj.vhost,
                            lottery_type=lottery_draw.lottery_type,
                            active=True
                        )
                        multiplier = payout_config.multiplier
                        max_payout = payout_config.max_payout
                    except LotteryPayoutConfig.DoesNotExist:
                        # Use defaults if no config
                        multiplier = wagerObj.bet_data.get("payout_multiplier", 10000)
                        max_payout = Decimal(self.MAX_PAYOUT)

                    # Calculate winnings with cap
                    calculated_payout = Decimal(str(wagerObj.risk)) * multiplier
                    wagerObj.win = min(calculated_payout, max_payout)

                    wagerObj.grader_history = {
                        "exact_match": True,
                        "winning_numbers": winning_numbers,
                        "winning_bonus": winning_bonus,
                        "user_numbers": user_numbers,
                        "user_bonus": user_bonus,
                        "payout": float(wagerObj.win),
                        "multiplier": multiplier,
                        "capped": wagerObj.win == max_payout,
                        "lottery_draw_uuid": str(lottery_draw.uuid),
                        "grader": "LotteryGrader._grade_with_bet_data"
                    }

                    self.logger.info(
                        f"Wager {wagerObj.uuid} WON! Exact match. "
                        f"Payout: ${wagerObj.win} (Risk: ${wagerObj.risk})"
                    )
                else:
                    # Not a winner
                    wagerObj.status = "L"
                    wagerObj.grader_history = {
                        "exact_match": False,
                        "user_numbers": user_numbers,
                        "user_bonus": user_bonus,
                        "winning_numbers": winning_numbers,
                        "winning_bonus": winning_bonus,
                        "lottery_draw_uuid": str(lottery_draw.uuid),
                        "grader": "LotteryGrader._grade_with_bet_data"
                    }

                    self.logger.info(
                        f"Wager {wagerObj.uuid} lost. No exact match. "
                        f"User: {user_numbers}+{user_bonus}, "
                        f"Winning: {winning_numbers}+{winning_bonus}"
                    )

                # Update LottoWagerPicks if exists
                try:
                    picks = wagerObj.lotto_picks
                    picks.matched_main = len(set(user_numbers) & set(winning_numbers))
                    picks.matched_bonus = 1 if user_bonus == winning_bonus else 0
                    picks.is_exact_match = exact_match
                    picks.save()
                except LottoWagerPicks.DoesNotExist:
                    pass

                # Mark as qualified and save
                wagerObj.graded = True
                wagerObj.graded_at = now()
                wagerObj.closed = False  # Will be closed by execute_close
                wagerObj.save()

                # Send qualification signal
                signal_wager_qualified.send(
                    sender=self.__class__,
                    wagerObj=wagerObj,
                    account=wagerObj.account,
                    vhost=wagerObj.vhost
                )

                return exact_match

            except LotteryDraw.DoesNotExist:
                self.logger.error(
                    f"No lottery draw found for {lottery_type_slug} on {draw_date}"
                )
                return None
            except Exception as e:
                self.logger.error(f"Error qualifying wager {wagerObj.uuid}: {e}")
                return None

    def qualify_lottery_wagers_for_match(self, match):
        """
        Qualify all lottery wagers for a specific match/draw.

        Args:
            match: Match object representing the lottery draw

        Returns:
            dict: Summary of qualification results
        """
        # Get all pending lottery wagers for this match
        wagers = Wager.objects.filter(
            match=match,
            status='P',
            type='LE',
            graded=False
        )

        results = {
            "total": wagers.count(),
            "winners": 0,
            "losers": 0,
            "errors": 0
        }

        self.logger.info(f"Qualifying {results['total']} lottery wagers for match {match.id}")

        for wager in wagers:
            try:
                is_winner = self.qualify_exact_lottery_wager(wager)

                if is_winner is True:
                    results["winners"] += 1
                    # Execute payout
                    if wager.execute_close():
                        self.logger.info(f"Executed payout for winning wager {wager.uuid}")
                elif is_winner is False:
                    results["losers"] += 1
                    # Execute loss (debit)
                    if wager.execute_close():
                        self.logger.info(f"Executed loss for wager {wager.uuid}")
                else:
                    results["errors"] += 1

            except Exception as e:
                self.logger.error(f"Failed to qualify wager {wager.uuid}: {e}")
                results["errors"] += 1

        self.logger.info(
            f"Qualification complete for match {match.id}: "
            f"{results['winners']} winners, {results['losers']} losers, "
            f"{results['errors']} errors"
        )

        return results

    def qualify_lottery_wagers_for_lotto_match(self, lotto_match_uuid):
        """
        Qualify all lottery wagers for a specific LottoMatch.

        Args:
            lotto_match_uuid: UUID of the LottoMatch

        Returns:
            dict: Summary of qualification results
        """
        # Get all pending lottery wagers for this lotto match
        wagers_with_picks = LottoWagerPicks.objects.filter(
            lotto_match_uuid=lotto_match_uuid,
            wager__status='P',
            wager__type='LE',
            wager__graded=False
        ).select_related('wager', 'wager__account', 'wager__vhost')

        results = {
            "total": wagers_with_picks.count(),
            "winners": 0,
            "losers": 0,
            "errors": 0
        }

        self.logger.info(
            f"Qualifying {results['total']} lottery wagers for lotto match {lotto_match_uuid}"
        )

        for picks in wagers_with_picks:
            wager = picks.wager
            try:
                is_winner = self._grade_with_picks(wager, picks)

                if is_winner is True:
                    results["winners"] += 1
                    if wager.execute_close():
                        self.logger.info(f"Executed payout for winning wager {wager.uuid}")
                elif is_winner is False:
                    results["losers"] += 1
                    if wager.execute_close():
                        self.logger.info(f"Executed loss for wager {wager.uuid}")
                else:
                    results["errors"] += 1

            except Exception as e:
                self.logger.error(f"Failed to qualify wager {wager.uuid}: {e}")
                results["errors"] += 1

        self.logger.info(
            f"Qualification complete for lotto match {lotto_match_uuid}: "
            f"{results['winners']} winners, {results['losers']} losers, "
            f"{results['errors']} errors"
        )

        return results
