import asyncio
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from playwright.async_api import async_playwright, Page, Browser

logger = logging.getLogger(__name__)


@dataclass
class ScrapeResult:
    """Result of a scrape operation."""
    success: bool
    main_numbers: List[int]
    bonus_numbers: List[int]
    draw_date: Optional[datetime] = None
    draw_number: Optional[str] = None
    draw_label: Optional[str] = None
    raw_html: str = ''
    error_message: str = ''
    duration_ms: int = 0


@dataclass
class DrawInfo:
    """Parsed draw information."""
    draw_date: Optional[datetime] = None
    draw_number: Optional[str] = None
    draw_label: Optional[str] = None


class BaseScraper(ABC):
    """
    Base class for state lottery scrapers.
    Each state should implement its own scraper class inheriting from this.
    """
    state: str = ''  # Override in subclass (e.g., 'NY', 'CA')
    timeout_ms: int = 30000

    def __init__(self):
        self.browser: Optional[Browser] = None
        self.playwright = None

    async def __aenter__(self):
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.stop()

    async def start(self):
        """Start the Playwright browser with stealth settings."""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-blink-features=AutomationControlled',
            ]
        )
        logger.info(f"Started browser for {self.state} scraper")

    async def stop(self):
        """Stop the Playwright browser."""
        if self.browser:
            await self.browser.close()
            self.browser = None
        if self.playwright:
            await self.playwright.stop()
            self.playwright = None
        logger.info(f"Stopped browser for {self.state} scraper")

    async def scrape(self, game) -> ScrapeResult:
        """
        Scrape lottery results for a game.

        Args:
            game: LotteryGame instance

        Returns:
            ScrapeResult with the scraped data
        """
        start_time = datetime.now()

        if not self.browser:
            await self.start()

        page = None
        try:
            # Create context with realistic user agent to bypass bot detection
            context = await self.browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                viewport={'width': 1920, 'height': 1080}
            )
            page = await context.new_page()

            # Disable webdriver detection
            await page.add_init_script(
                "Object.defineProperty(navigator, 'webdriver', {get: () => undefined});"
            )

            logger.info(f"Navigating to {game.url}")
            await page.goto(game.url, timeout=self.timeout_ms, wait_until='domcontentloaded')

            # Wait for dynamic content to load
            await self._wait_for_content(page, game)

            # Parse numbers using selectors from game config
            # Check if we have a combined all_numbers selector
            if game.selectors.get('all_numbers') and hasattr(self, 'parse_all_numbers'):
                main_numbers, bonus_numbers = await self.parse_all_numbers(page, game)
            else:
                main_numbers = await self._parse_numbers(page, game.selectors, 'winning_numbers')
                bonus_numbers = await self._parse_numbers(page, game.selectors, 'bonus_number')

            # Parse draw info
            draw_info = await self._parse_draw_info(page, game.selectors)

            # Get raw HTML for debugging
            raw_html = await page.content()

            duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)

            # Validate results
            if not main_numbers:
                return ScrapeResult(
                    success=False,
                    main_numbers=[],
                    bonus_numbers=[],
                    raw_html=raw_html,
                    error_message="No main numbers found",
                    duration_ms=duration_ms
                )

            return ScrapeResult(
                success=True,
                main_numbers=main_numbers,
                bonus_numbers=bonus_numbers,
                draw_date=draw_info.draw_date,
                draw_number=draw_info.draw_number,
                draw_label=draw_info.draw_label,
                raw_html=raw_html,
                duration_ms=duration_ms
            )

        except Exception as e:
            duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            error_msg = f"Scrape error: {str(e)}"
            logger.error(f"{error_msg} for game {game.slug}")

            # Capture screenshot on failure
            screenshot_path = ''
            if page:
                try:
                    screenshot_path = f"/tmp/scrape_error_{game.slug}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                    await page.screenshot(path=screenshot_path)
                    logger.info(f"Saved error screenshot to {screenshot_path}")
                except Exception as screenshot_error:
                    logger.warning(f"Failed to capture screenshot: {screenshot_error}")

            return ScrapeResult(
                success=False,
                main_numbers=[],
                bonus_numbers=[],
                raw_html='',
                error_message=error_msg,
                duration_ms=duration_ms
            )
        finally:
            if page:
                context = page.context
                await page.close()
                await context.close()

    async def _wait_for_content(self, page: Page, game) -> None:
        """
        Wait for dynamic content to load.
        Override in subclass for state-specific waiting logic.
        """
        # Default: wait for winning numbers selector if specified
        selectors = game.selectors
        if selectors.get('winning_numbers'):
            try:
                await page.wait_for_selector(
                    selectors['winning_numbers'],
                    timeout=10000
                )
            except Exception:
                logger.warning(f"Timeout waiting for winning_numbers selector")

    async def _parse_numbers(
        self,
        page: Page,
        selectors: dict,
        selector_key: str
    ) -> List[int]:
        """
        Parse numbers from the page using the configured selector.

        Args:
            page: Playwright page
            selectors: Dict of CSS selectors from game config
            selector_key: Key to look up in selectors dict

        Returns:
            List of parsed integers
        """
        selector = selectors.get(selector_key)
        if not selector:
            return []

        try:
            elements = await page.query_selector_all(selector)
            numbers = []

            for element in elements:
                text = await element.text_content()
                if text:
                    text = text.strip()
                    try:
                        numbers.append(int(text))
                    except ValueError:
                        logger.warning(f"Could not parse number from: {text}")

            return numbers
        except Exception as e:
            logger.error(f"Error parsing numbers with selector {selector}: {e}")
            return []

    async def _parse_draw_info(self, page: Page, selectors: dict) -> DrawInfo:
        """
        Parse draw date, number, and label from the page.
        Override in subclass for state-specific parsing.
        """
        draw_info = DrawInfo()

        # Parse draw date
        date_selector = selectors.get('draw_date')
        if date_selector:
            try:
                element = await page.query_selector(date_selector)
                if element:
                    text = await element.text_content()
                    draw_info.draw_date = self._parse_date(text)
            except Exception as e:
                logger.warning(f"Error parsing draw date: {e}")

        # Parse draw number
        number_selector = selectors.get('draw_number')
        if number_selector:
            try:
                element = await page.query_selector(number_selector)
                if element:
                    text = await element.text_content()
                    if text:
                        draw_info.draw_number = text.strip()
            except Exception as e:
                logger.warning(f"Error parsing draw number: {e}")

        return draw_info

    def _parse_date(self, date_string: Optional[str]) -> Optional[datetime]:
        """
        Parse a date string into a datetime object.
        Override in subclass for state-specific date formats.
        """
        if not date_string:
            return None

        date_string = date_string.strip()

        # Common date formats to try
        formats = [
            '%A, %B %d, %Y',      # "Saturday, December 7, 2025"
            '%B %d, %Y',          # "December 7, 2025"
            '%m/%d/%Y',           # "12/07/2025"
            '%Y-%m-%d',           # "2025-12-07"
            '%a %b %d, %Y',       # "Sat Dec 7, 2025"
            '%A %B %d, %Y',       # "Saturday December 7, 2025"
        ]

        for fmt in formats:
            try:
                return datetime.strptime(date_string, fmt)
            except ValueError:
                continue

        logger.warning(f"Could not parse date: {date_string}")
        return None

    @abstractmethod
    async def get_draw_label(self, page: Page, game) -> Optional[str]:
        """
        Determine the draw label (midday/evening) for multi-draw games.
        Must be implemented by state-specific scrapers.
        """
        pass
