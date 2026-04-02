import logging
import re
from datetime import datetime
from typing import List, Optional, Tuple

from playwright.async_api import Page

from . import BaseScraper, register_scraper, ScrapeResult, DrawInfo

logger = logging.getLogger(__name__)


@register_scraper('CA')
class CAScraper(BaseScraper):
    """
    Scraper for California Lottery games.
    The CA Lottery site uses server-rendered HTML, making it easier to scrape.
    """
    state = 'CA'

    async def parse_all_numbers(
        self,
        page: Page,
        game,
        target_draw_label: Optional[str] = None
    ) -> Tuple[List[int], List[int]]:
        """
        Parse numbers from CA Lottery page, limiting to main_count.
        CA pages show past results, so we only want the first N numbers.
        For multi-draw games, extracts the appropriate draw based on target_draw_label.

        Returns:
            Tuple of (main_numbers, bonus_numbers)
        """
        selectors = game.selectors
        parser_config = getattr(game, 'parser_config', {}) or {}
        selector = selectors.get('all_numbers')

        if not selector:
            selector = '.winning-numbers li'

        try:
            elements = await page.query_selector_all(selector)
            all_numbers = []

            for element in elements:
                text = await element.text_content()
                if text:
                    text = text.strip().lstrip('*').strip()
                    if text.isdigit():
                        all_numbers.append(int(text))

            if not all_numbers:
                logger.warning("No numbers found with CA selector")
                return [], []

            # Check if this is a multi-draw page (e.g., Daily 3 midday/evening)
            if parser_config.get('multi_draw'):
                all_numbers = self._extract_target_draw(
                    all_numbers,
                    parser_config,
                    target_draw_label
                )

            # Limit to main_count (CA pages show many past results)
            main_count = game.main_count
            bonus_count = getattr(game, 'bonus_count', 0) or 0

            main_numbers = all_numbers[:main_count]
            bonus_numbers = all_numbers[main_count:main_count + bonus_count] if bonus_count else []

            logger.info(f"Parsed CA numbers - main: {main_numbers}, bonus: {bonus_numbers}")
            return main_numbers, bonus_numbers

        except Exception as e:
            logger.error(f"Error parsing CA all numbers: {e}")
            return [], []

    def _extract_target_draw(
        self,
        all_numbers: List[int],
        parser_config: dict,
        target_draw_label: Optional[str]
    ) -> List[int]:
        """
        Extract numbers for a specific draw from a multi-draw page.
        """
        balls_per_draw = parser_config.get('balls_per_draw', 3)
        draw_order = parser_config.get('draw_order', ['evening', 'midday'])

        if not target_draw_label:
            target_draw_label = self._get_current_draw_label()

        try:
            draw_index = draw_order.index(target_draw_label)
        except ValueError:
            logger.warning(f"Unknown draw label: {target_draw_label}, using first draw")
            draw_index = 0

        start_idx = draw_index * balls_per_draw
        end_idx = start_idx + balls_per_draw

        extracted = all_numbers[start_idx:end_idx]
        logger.info(f"Extracted {target_draw_label} draw (index {draw_index}): {extracted}")

        return extracted

    def _get_current_draw_label(self) -> str:
        """Determine which draw label to use based on current PT time."""
        from datetime import datetime
        try:
            import pytz
            pacific = pytz.timezone('America/Los_Angeles')
            now = datetime.now(pacific)
            hour = now.hour
            # Midday draw ~1pm, Evening draw ~6:30pm
            if hour >= 19 or hour < 13:
                return 'midday'
            else:
                return 'evening'
        except Exception:
            return 'evening'

    async def _wait_for_content(self, page: Page, game) -> None:
        """
        Wait for CA Lottery content to load.
        CA Lottery uses server-rendered HTML, so less waiting needed.
        """
        try:
            # Wait for the page to be fully loaded
            await page.wait_for_load_state('domcontentloaded')
            # Small delay for any JavaScript enhancements
            await page.wait_for_timeout(1000)
        except Exception as e:
            logger.warning(f"Timeout waiting for CA Lottery content: {e}")

    async def _parse_numbers(
        self,
        page: Page,
        selectors: dict,
        selector_key: str
    ) -> List[int]:
        """
        Parse numbers from CA Lottery page.
        CA Lottery typically displays numbers in list items.
        """
        selector = selectors.get(selector_key)
        if not selector:
            # Default selectors for CA Lottery
            if selector_key == 'winning_numbers':
                selector = self._get_default_winning_selector()
            elif selector_key == 'bonus_number':
                selector = self._get_default_bonus_selector()

        if not selector:
            return []

        try:
            elements = await page.query_selector_all(selector)

            if not elements:
                # Fallback for common CA Lottery patterns
                elements = await self._find_number_elements(page)

            numbers = []
            for element in elements:
                text = await element.text_content()
                if text:
                    text = text.strip()
                    # CA Lottery sometimes uses "* N" format
                    text = text.lstrip('*').strip()
                    try:
                        numbers.append(int(text))
                    except ValueError:
                        # Try extracting number from text
                        match = re.search(r'\d+', text)
                        if match:
                            numbers.append(int(match.group()))

            return numbers

        except Exception as e:
            logger.error(f"Error parsing CA numbers with selector {selector}: {e}")
            return []

    async def _find_number_elements(self, page: Page):
        """
        Fallback method to find number elements on CA Lottery.
        """
        # CA Lottery commonly uses list items for numbers
        patterns = [
            '.past-results li',
            '.winning-numbers li',
            '[class*="number"] li',
            '.draw-results li',
        ]

        for pattern in patterns:
            elements = await page.query_selector_all(pattern)
            if elements:
                valid_elements = []
                for el in elements:
                    text = await el.text_content()
                    if text:
                        text = text.strip().lstrip('*').strip()
                        if text.isdigit():
                            valid_elements.append(el)
                if valid_elements:
                    return valid_elements

        return []

    def _get_default_winning_selector(self) -> str:
        """Return default selector for winning numbers on CA Lottery."""
        return '.winning-numbers li, .past-results li'

    def _get_default_bonus_selector(self) -> str:
        """Return default selector for bonus numbers on CA Lottery."""
        return '.mega-ball, .bonus-number'

    async def _parse_draw_info(self, page: Page, selectors: dict) -> DrawInfo:
        """
        Parse draw information from CA Lottery page.
        """
        draw_info = DrawInfo()

        # Try to find draw date
        date_selector = selectors.get('draw_date')
        if date_selector:
            try:
                element = await page.query_selector(date_selector)
                if element:
                    text = await element.text_content()
                    draw_info.draw_date = self._parse_date(text)
            except Exception as e:
                logger.warning(f"Error parsing CA draw date: {e}")

        if not draw_info.draw_date:
            draw_info.draw_date = await self._find_draw_date(page)

        # Try to find draw number
        number_selector = selectors.get('draw_number')
        if number_selector:
            try:
                element = await page.query_selector(number_selector)
                if element:
                    text = await element.text_content()
                    # Extract draw number (e.g., "Draw #6412")
                    match = re.search(r'#?(\d+)', text)
                    if match:
                        draw_info.draw_number = match.group(1)
            except Exception as e:
                logger.warning(f"Error parsing CA draw number: {e}")

        return draw_info

    async def _find_draw_date(self, page: Page) -> Optional[datetime]:
        """
        Try to find the draw date on CA Lottery pages.
        """
        try:
            # CA Lottery uses formats like "SUN/DEC 7, 2025"
            containers = await page.query_selector_all(
                '[class*="date"], [class*="draw"], .past-results-header'
            )

            for container in containers:
                text = await container.text_content()
                if text:
                    parsed = self._parse_date(text)
                    if parsed:
                        return parsed

        except Exception as e:
            logger.warning(f"Error finding CA draw date: {e}")

        return None

    async def get_draw_label(self, page: Page, game) -> Optional[str]:
        """
        Determine draw label for CA games.
        Most CA games have single daily draws, but some have multiple.
        """
        try:
            text_content = await page.content()
            text_lower = text_content.lower()

            if 'midday' in text_lower:
                return 'midday'
            elif 'evening' in text_lower:
                return 'evening'

        except Exception as e:
            logger.warning(f"Error determining CA draw label: {e}")

        return None

    def _parse_date(self, date_string: Optional[str]) -> Optional[datetime]:
        """
        Parse date strings in formats used by CA Lottery.
        """
        if not date_string:
            return None

        date_string = date_string.strip().upper()

        # CA Lottery specific formats
        formats = [
            '%a/%b %d, %Y',       # "SUN/DEC 7, 2025"
            '%A/%B %d, %Y',       # "SUNDAY/DECEMBER 7, 2025"
            '%a %b %d, %Y',       # "SUN DEC 7, 2025"
            '%B %d, %Y',          # "DECEMBER 7, 2025"
            '%b %d, %Y',          # "DEC 7, 2025"
            '%m/%d/%Y',           # "12/07/2025"
        ]

        # Clean up the string
        date_string = re.sub(r'\s+', ' ', date_string)

        for fmt in formats:
            try:
                return datetime.strptime(date_string, fmt)
            except ValueError:
                continue

        # Try with lowercase
        date_string_lower = date_string.title()
        for fmt in formats:
            try:
                return datetime.strptime(date_string_lower, fmt)
            except ValueError:
                continue

        # Try to extract and parse date components
        match = re.search(
            r'(\w{3})[/\s]+(\w{3})\s+(\d{1,2}),?\s+(\d{4})',
            date_string
        )
        if match:
            try:
                clean_date = f"{match.group(2)} {match.group(3)}, {match.group(4)}"
                return datetime.strptime(clean_date.title(), '%b %d, %Y')
            except ValueError:
                pass

        logger.warning(f"Could not parse CA date: {date_string}")
        return None
