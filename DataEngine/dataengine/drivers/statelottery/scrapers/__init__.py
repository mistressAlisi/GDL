from .base import BaseScraper, ScrapeResult, DrawInfo

# Registry of state scrapers
_SCRAPERS = {}


def register_scraper(state: str):
    """Decorator to register a scraper class for a state."""
    def decorator(cls):
        _SCRAPERS[state.upper()] = cls
        return cls
    return decorator


# Import scrapers to trigger registration
from . import ny  # noqa: F401, E402
from . import ca  # noqa: F401, E402
from . import multi  # noqa: F401, E402
from . import ct  # noqa: F401, E402
from . import md  # noqa: F401, E402
from . import generic  # noqa: F401, E402  # AZ, AR, CO, FL, etc.
from . import custom  # noqa: F401, E402  # Custom scrapers override generic


def get_scraper_for_state(state: str) -> type:
    """
    Get the scraper class for a given state.

    Args:
        state: Two-letter state code (e.g., 'NY', 'CA')

    Returns:
        Scraper class for the state

    Raises:
        ValueError: If no scraper exists for the state
    """
    state = state.upper()
    if state not in _SCRAPERS:
        raise ValueError(f"No scraper registered for state: {state}")
    return _SCRAPERS[state]


def get_registered_states() -> list:
    """Get list of states with registered scrapers."""
    return list(_SCRAPERS.keys())


__all__ = [
    'BaseScraper',
    'ScrapeResult',
    'DrawInfo',
    'register_scraper',
    'get_scraper_for_state',
    'get_registered_states',
]
