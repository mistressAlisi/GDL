import logging
from dataclasses import dataclass
from typing import List, Optional, Tuple

from ..models import LotteryGame
from ..scrapers import ScrapeResult

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Result of validating scraped lottery numbers."""
    valid: bool
    errors: List[str]
    warnings: List[str]


def validate_scrape_result(game: LotteryGame, result: ScrapeResult) -> ValidationResult:
    """
    Validate a scrape result against the game's configuration.

    Args:
        game: LotteryGame instance with format rules
        result: ScrapeResult from the scraper

    Returns:
        ValidationResult with valid flag and any errors/warnings
    """
    errors = []
    warnings = []

    # Check if scrape was successful
    if not result.success:
        errors.append(f"Scrape failed: {result.error_message}")
        return ValidationResult(valid=False, errors=errors, warnings=warnings)

    # Validate main numbers
    main_errors = _validate_numbers(
        numbers=result.main_numbers,
        expected_count=game.main_count,
        range_min=game.main_range_min,
        range_max=game.main_range_max,
        require_unique=not game.is_positional,
        label="main"
    )
    errors.extend(main_errors)

    # Validate bonus numbers if expected
    if game.bonus_count > 0:
        if not result.bonus_numbers:
            errors.append(f"Expected {game.bonus_count} bonus number(s) but got none")
        else:
            bonus_range = game.bonus_range
            if bonus_range:
                bonus_errors = _validate_numbers(
                    numbers=result.bonus_numbers,
                    expected_count=game.bonus_count,
                    range_min=bonus_range[0],
                    range_max=bonus_range[1],
                    require_unique=True,
                    label="bonus"
                )
                errors.extend(bonus_errors)
    elif result.bonus_numbers:
        warnings.append(f"Unexpected bonus numbers found: {result.bonus_numbers}")

    return ValidationResult(
        valid=len(errors) == 0,
        errors=errors,
        warnings=warnings
    )


def _validate_numbers(
    numbers: List[int],
    expected_count: int,
    range_min: int,
    range_max: int,
    require_unique: bool,
    label: str
) -> List[str]:
    """
    Validate a list of numbers against expected constraints.

    Args:
        numbers: List of numbers to validate
        expected_count: Expected number of values
        range_min: Minimum allowed value
        range_max: Maximum allowed value
        require_unique: Whether numbers must be unique
        label: Label for error messages (e.g., "main", "bonus")

    Returns:
        List of error messages (empty if valid)
    """
    errors = []

    # Check count
    if len(numbers) != expected_count:
        errors.append(
            f"Expected {expected_count} {label} number(s) but got {len(numbers)}: {numbers}"
        )

    # Check range
    out_of_range = [n for n in numbers if n < range_min or n > range_max]
    if out_of_range:
        errors.append(
            f"{label.capitalize()} numbers out of range [{range_min}-{range_max}]: {out_of_range}"
        )

    # Check uniqueness (for pool games, not positional)
    if require_unique and len(numbers) != len(set(numbers)):
        errors.append(f"Duplicate {label} numbers found: {numbers}")

    return errors


def validate_game_config(game: LotteryGame) -> ValidationResult:
    """
    Validate a game's configuration for consistency.

    Args:
        game: LotteryGame instance

    Returns:
        ValidationResult with any configuration issues
    """
    errors = []
    warnings = []

    # Check number ranges make sense
    if game.main_range_min >= game.main_range_max:
        errors.append(
            f"Invalid main range: min ({game.main_range_min}) >= max ({game.main_range_max})"
        )

    # Check we can pick enough numbers from the range
    range_size = game.main_range_max - game.main_range_min + 1
    if not game.is_positional and range_size < game.main_count:
        errors.append(
            f"Cannot pick {game.main_count} unique numbers from range "
            f"[{game.main_range_min}-{game.main_range_max}]"
        )

    # Check bonus configuration
    if game.bonus_count > 0:
        if not game.bonus_range_min or not game.bonus_range_max:
            errors.append("Bonus count > 0 but bonus range not specified")
        elif game.bonus_range_min >= game.bonus_range_max:
            errors.append(
                f"Invalid bonus range: min ({game.bonus_range_min}) >= max ({game.bonus_range_max})"
            )

    # Check selectors
    if not game.selectors:
        errors.append("No selectors configured")
    elif 'winning_numbers' not in game.selectors:
        warnings.append("No 'winning_numbers' selector configured")

    # Check schedule
    if not game.schedule:
        warnings.append("No schedule configured")
    elif 'times' not in game.schedule:
        warnings.append("No draw times configured in schedule")

    return ValidationResult(
        valid=len(errors) == 0,
        errors=errors,
        warnings=warnings
    )
