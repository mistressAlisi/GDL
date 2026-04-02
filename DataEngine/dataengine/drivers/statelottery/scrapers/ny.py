import logging
import re
from datetime import datetime
from typing import List, Optional, Tuple

from playwright.async_api import Page

from . import BaseScraper, register_scraper, ScrapeResult, DrawInfo

logger = logging.getLogger(__name__)


@register_scraper('NY')
class NYScraper(BaseScraper):
    """
    Scraper for New York Lottery games.
    Handles the SPA-based nylottery.ny.gov site which uses styled-components.
    """
    state = 'NY'

    async def _wait_for_content(self, page: Page, game) -> None:
        """
        Wait for NY Lottery's dynamic content to load.
        The site uses React and loads results via JavaScript.
        """
        # Wait for the main content area to be present
        selectors = game.selectors

        # Try the configured selector first
        if selectors.get('all_numbers'):
            wait_selector = selectors['all_numbers']
        else:
            wait_selector = '[class*="BallContainer"], [class*="Ball"], [class*="winning"]'

        try:
            await page.wait_for_selector(wait_selector, timeout=15000)
            # Additional wait for React hydration
            await page.wait_for_timeout(2000)
        except Exception as e:
            logger.warning(f"Timeout waiting for NY Lottery content: {e}")

    async def parse_all_numbers(
        self,
        page: Page,
        game,
        target_draw_label: Optional[str] = None
    ) -> Tuple[List[int], List[int]]:
        """
        Parse all numbers from NY Lottery page using the all_numbers selector.
        Splits results into main and bonus based on game.main_count.

        For multi-draw pages (like Win4), extracts the appropriate draw based on
        target_draw_label or current time.

        Returns:
            Tuple of (main_numbers, bonus_numbers)
        """
        selectors = game.selectors
        parser_config = getattr(game, 'parser_config', {}) or {}
        selector = selectors.get('all_numbers')

        if not selector:
            # Fall back to separate selectors
            main = await self._parse_numbers(page, selectors, 'winning_numbers')
            bonus = await self._parse_numbers(page, selectors, 'bonus_number')
            return main, bonus

        try:
            elements = await page.query_selector_all(selector)
            all_numbers = []

            for element in elements:
                text = await element.text_content()
                if text:
                    text = text.strip()
                    match = re.search(r'\d+', text)
                    if match:
                        all_numbers.append(int(match.group()))

            if not all_numbers:
                logger.warning("No numbers found with all_numbers selector")
                return [], []

            # Check if this is a multi-draw page (e.g., Win4 shows both midday and evening)
            if parser_config.get('multi_draw'):
                all_numbers = self._extract_target_draw(
                    all_numbers,
                    parser_config,
                    target_draw_label
                )

            # Split based on main_count from game config
            main_count = game.main_count
            bonus_count = getattr(game, 'bonus_count', 0) or 0

            main_numbers = all_numbers[:main_count]
            bonus_numbers = all_numbers[main_count:main_count + bonus_count] if bonus_count else []

            logger.info(f"Parsed NY numbers - main: {main_numbers}, bonus: {bonus_numbers}")
            return main_numbers, bonus_numbers

        except Exception as e:
            logger.error(f"Error parsing NY all numbers: {e}")
            return [], []

    def _extract_target_draw(
        self,
        all_numbers: List[int],
        parser_config: dict,
        target_draw_label: Optional[str]
    ) -> List[int]:
        """
        Extract numbers for a specific draw from a multi-draw page.

        Args:
            all_numbers: All numbers found on page
            parser_config: Parser configuration from game
            target_draw_label: Which draw to extract ('midday', 'evening', etc.)

        Returns:
            Numbers for the target draw only
        """
        balls_per_draw = parser_config.get('balls_per_draw', 4)
        draw_order = parser_config.get('draw_order', ['evening', 'midday'])

        # Determine which draw to extract
        if not target_draw_label:
            # Default to most recent draw based on current time
            target_draw_label = self._get_current_draw_label()

        # Find the index of target draw in the order
        try:
            draw_index = draw_order.index(target_draw_label)
        except ValueError:
            logger.warning(f"Unknown draw label: {target_draw_label}, using first draw")
            draw_index = 0

        # Extract the slice for this draw
        start_idx = draw_index * balls_per_draw
        end_idx = start_idx + balls_per_draw

        extracted = all_numbers[start_idx:end_idx]
        logger.info(f"Extracted {target_draw_label} draw (index {draw_index}): {extracted}")

        return extracted

    def _get_current_draw_label(self) -> str:
        """
        Determine which draw label to use based on current time.
        Returns 'evening' if after ~3pm, otherwise 'midday'.
        """
        from datetime import datetime
        import pytz

        try:
            eastern = pytz.timezone('America/New_York')
            now = datetime.now(eastern)

            # If after 3pm (15:00), the midday draw has happened, target evening
            # If after 11pm (23:00), evening draw happened, target next midday
            hour = now.hour

            if hour >= 23 or hour < 15:
                return 'midday'
            else:
                return 'evening'
        except Exception:
            # Default to evening if timezone lookup fails
            return 'evening'

    async def _parse_numbers(
        self,
        page: Page,
        selectors: dict,
        selector_key: str
    ) -> List[int]:
        """
        Parse numbers from NY Lottery page.
        Handles the specific HTML structure of nylottery.ny.gov.
        """
        selector = selectors.get(selector_key)
        if not selector:
            # Try default selectors for NY Lottery
            if selector_key == 'winning_numbers':
                selector = self._get_default_winning_selector()
            elif selector_key == 'bonus_number':
                selector = self._get_default_bonus_selector()

        if not selector:
            return []

        try:
            # Try the configured selector first
            elements = await page.query_selector_all(selector)

            if not elements:
                # Fallback: try to find numbers in common patterns
                elements = await self._find_number_elements(page, selector_key)

            numbers = []
            for element in elements:
                text = await element.text_content()
                if text:
                    text = text.strip()
                    # Handle cases where text might have extra content
                    match = re.search(r'\d+', text)
                    if match:
                        numbers.append(int(match.group()))

            return numbers

        except Exception as e:
            logger.error(f"Error parsing NY numbers with selector {selector}: {e}")
            return []

    async def _find_number_elements(self, page: Page, selector_key: str):
        """
        Fallback method to find number elements using common patterns.
        """
        # Common patterns on NY Lottery site
        patterns = [
            '[class*="ball"]',
            '[class*="number"]',
            '[class*="winning"] span',
            '[class*="result"] span',
        ]

        for pattern in patterns:
            elements = await page.query_selector_all(pattern)
            if elements:
                # Filter to elements that contain only numbers
                valid_elements = []
                for el in elements:
                    text = await el.text_content()
                    if text and text.strip().isdigit():
                        valid_elements.append(el)
                if valid_elements:
                    return valid_elements

        return []

    def _get_default_winning_selector(self) -> str:
        """Return default selector for winning numbers on NY Lottery."""
        return '[class*="winning"] [class*="ball"], [class*="number-ball"]'

    def _get_default_bonus_selector(self) -> str:
        """Return default selector for bonus numbers on NY Lottery."""
        return '[class*="bonus"] [class*="ball"], [class*="bonus-ball"]'

    async def _parse_draw_info(self, page: Page, selectors: dict) -> DrawInfo:
        """
        Parse draw information from NY Lottery page.
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
                logger.warning(f"Error parsing NY draw date: {e}")

        # If no date found via selector, try common patterns
        if not draw_info.draw_date:
            draw_info.draw_date = await self._find_draw_date(page)

        # Determine draw label (midday/evening) for multi-draw games
        draw_info.draw_label = await self.get_draw_label(page, None)

        return draw_info

    async def _find_draw_date(self, page: Page) -> Optional[datetime]:
        """
        Try to find the draw date using common patterns on NY Lottery.
        """
        # Common date patterns
        date_patterns = [
            r'(\w+day),?\s+(\w+)\s+(\d{1,2}),?\s+(\d{4})',  # "Saturday, December 7, 2025"
            r'(\d{1,2})/(\d{1,2})/(\d{4})',  # "12/7/2025"
            r'(\w+)\s+(\d{1,2}),?\s+(\d{4})',  # "December 7, 2025"
        ]

        try:
            # Look for date in common containers
            containers = await page.query_selector_all(
                '[class*="date"], [class*="draw"], time'
            )

            for container in containers:
                text = await container.text_content()
                if text:
                    for pattern in date_patterns:
                        match = re.search(pattern, text)
                        if match:
                            return self._parse_date(text)

        except Exception as e:
            logger.warning(f"Error finding NY draw date: {e}")

        return None

    async def get_draw_label(self, page: Page, game) -> Optional[str]:
        """
        Determine if this is a midday or evening draw for games like Take 5.
        """
        try:
            # Look for explicit midday/evening labels
            text_content = await page.content()
            text_lower = text_content.lower()

            if 'midday' in text_lower:
                return 'midday'
            elif 'evening' in text_lower:
                return 'evening'

            # Check for time indicators
            time_patterns = [
                (r'2:30\s*pm|14:30', 'midday'),
                (r'10:30\s*pm|22:30', 'evening'),
            ]

            for pattern, label in time_patterns:
                if re.search(pattern, text_content, re.IGNORECASE):
                    return label

        except Exception as e:
            logger.warning(f"Error determining draw label: {e}")

        return None

    def _parse_date(self, date_string: Optional[str]) -> Optional[datetime]:
        """
        Parse date strings in formats commonly used by NY Lottery.
        """
        if not date_string:
            return None

        date_string = date_string.strip()

        # NY Lottery specific formats
        formats = [
            '%A, %B %d, %Y',      # "Saturday, December 7, 2025"
            '%a, %b %d, %Y',      # "Sat, Dec 7, 2025"
            '%B %d, %Y',          # "December 7, 2025"
            '%b %d, %Y',          # "Dec 7, 2025"
            '%m/%d/%Y',           # "12/07/2025"
            '%m/%d/%y',           # "12/07/25"
        ]

        # Clean up the string
        date_string = re.sub(r'\s+', ' ', date_string)

        # Strip common prefixes like "Midday Fri ", "Evening Sat ", etc.
        date_string = re.sub(r'^(Midday|Evening|Morning|Night)\s+\w+\s+', '', date_string)

        for fmt in formats:
            try:
                return datetime.strptime(date_string, fmt)
            except ValueError:
                continue

        # Try to extract date components with regex
        match = re.search(
            r'(\w+)\s+(\d{1,2}),?\s+(\d{4})',
            date_string
        )
        if match:
            try:
                clean_date = f"{match.group(1)} {match.group(2)}, {match.group(3)}"
                return datetime.strptime(clean_date, '%B %d, %Y')
            except ValueError:
                pass

        logger.warning(f"Could not parse NY date: {date_string}")
        return None
