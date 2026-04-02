import logging
import re
from datetime import datetime
from typing import List, Optional, Tuple

from playwright.async_api import Page

from . import BaseScraper, register_scraper, DrawInfo

logger = logging.getLogger(__name__)


class GenericStateScraper(BaseScraper):
    """
    Generic scraper for state lottery websites.
    Handles common patterns found across many state lottery sites.
    Subclasses can override specific methods for state-specific handling.
    """

    async def _wait_for_content(self, page: Page, game) -> None:
        """
        Wait for lottery content to load.
        Most state sites use some form of dynamic content.
        """
        selectors = game.selectors

        try:
            # Try the configured selector first
            if selectors.get('all_numbers'):
                await page.wait_for_selector(
                    selectors['all_numbers'],
                    timeout=10000
                )
            else:
                # Fallback to common patterns
                await page.wait_for_selector(
                    '.winning-numbers, .ball, [class*="number"], table',
                    timeout=10000
                )
            # Allow time for any JavaScript to complete
            await page.wait_for_timeout(1500)
        except Exception as e:
            logger.warning(f"Timeout waiting for {self.state} content: {e}")

    async def parse_all_numbers(
        self,
        page: Page,
        game,
        target_draw_label: Optional[str] = None
    ) -> Tuple[List[int], List[int]]:
        """
        Parse all numbers from a state lottery page.
        Uses configured selectors with fallback patterns.

        Returns:
            Tuple of (main_numbers, bonus_numbers)
        """
        selectors = game.selectors
        selector = selectors.get('all_numbers')

        # Calculate expected total numbers
        main_count = game.main_count
        bonus_count = getattr(game, 'bonus_count', 0) or 0
        expected_count = main_count + bonus_count

        all_numbers = []

        # Try configured selector first
        if selector:
            all_numbers = await self._extract_with_selector(page, selector, expected_count)

        # Fallback to common patterns if no numbers found
        if not all_numbers:
            all_numbers = await self._try_common_patterns(page)

        if not all_numbers:
            logger.warning(f"No numbers found on {self.state} lottery page")
            return [], []

        # Split into main and bonus
        main_count = game.main_count
        bonus_count = getattr(game, 'bonus_count', 0) or 0

        main_numbers = all_numbers[:main_count]
        bonus_numbers = all_numbers[main_count:main_count + bonus_count] if bonus_count else []

        logger.info(f"Parsed {self.state} numbers - main: {main_numbers}, bonus: {bonus_numbers}")
        return main_numbers, bonus_numbers

    async def _extract_with_selector(
        self,
        page: Page,
        selector: str,
        expected_count: int = 6
    ) -> List[int]:
        """
        Extract numbers using a CSS selector.
        Handles both individual number elements and space-separated numbers in one element.
        """
        try:
            elements = await page.query_selector_all(selector)
            numbers = []

            for element in elements:
                text = await element.text_content()
                if text:
                    text = text.strip().lstrip('*').strip()
                    # Find all numbers in the text (handles "2 12 21 27 34 42" format)
                    found_nums = re.findall(r'\d+', text)
                    for num_str in found_nums:
                        num = int(num_str)
                        # Filter out unreasonable numbers (likely not lottery numbers)
                        if 0 <= num <= 99:
                            numbers.append(num)

                    # If we found enough numbers from first element, stop
                    # (avoids combining numbers from multiple draws)
                    if len(numbers) >= expected_count:
                        break

            return numbers

        except Exception as e:
            logger.error(f"Error extracting with selector {selector}: {e}")
            return []

    async def _try_common_patterns(self, page: Page) -> List[int]:
        """
        Try common CSS patterns found on lottery sites.
        """
        patterns = [
            '.winning-numbers li',
            '.winning-numbers span',
            '.ball',
            '.number-ball',
            '.lotto-ball',
            'table.winning-numbers td',
            '.draw-results span',
            '.numbers span',
            '[class*="ball"]',
            '[class*="number"]',
        ]

        for pattern in patterns:
            try:
                elements = await page.query_selector_all(pattern)
                if elements:
                    numbers = []
                    for el in elements:
                        text = await el.text_content()
                        if text:
                            text = text.strip().lstrip('*').strip()
                            if text.isdigit():
                                num = int(text)
                                if 0 <= num <= 99:
                                    numbers.append(num)
                    if numbers:
                        return numbers
            except Exception:
                continue

        return []

    async def _parse_draw_info(self, page: Page, selectors: dict) -> DrawInfo:
        """
        Parse draw information from state lottery page.
        """
        draw_info = DrawInfo()

        # Try configured selector first
        date_selector = selectors.get('draw_date')
        if date_selector:
            try:
                element = await page.query_selector(date_selector)
                if element:
                    text = await element.text_content()
                    draw_info.draw_date = self._parse_date(text)
            except Exception as e:
                logger.warning(f"Error parsing draw date: {e}")

        # If no date found, try common patterns
        if not draw_info.draw_date:
            draw_info.draw_date = await self._find_draw_date(page)

        return draw_info

    async def _find_draw_date(self, page: Page) -> Optional[datetime]:
        """
        Try to find draw date using common patterns.
        """
        date_selectors = [
            '.draw-date',
            '.date',
            '.drawing-date',
            '[class*="date"]',
            'h2',
            'h3',
            'th',
        ]

        for selector in date_selectors:
            try:
                elements = await page.query_selector_all(selector)
                for element in elements:
                    text = await element.text_content()
                    if text:
                        parsed = self._parse_date(text)
                        if parsed:
                            return parsed
            except Exception:
                continue

        return None

    async def get_draw_label(self, page: Page, game) -> Optional[str]:
        """
        Determine if this is a midday or evening draw.
        Most main lotto games have single draws.
        """
        try:
            text_content = await page.content()
            text_lower = text_content.lower()

            if 'midday' in text_lower:
                return 'midday'
            elif 'evening' in text_lower:
                return 'evening'
        except Exception:
            pass

        return None

    def _parse_date(self, date_string: Optional[str]) -> Optional[datetime]:
        """
        Parse date strings in common formats.
        """
        if not date_string:
            return None

        date_string = date_string.strip()

        formats = [
            '%A, %B %d, %Y',      # "Wednesday, January 7, 2026"
            '%a, %b %d, %Y',      # "Wed, Jan 7, 2026"
            '%B %d, %Y',          # "January 7, 2026"
            '%b %d, %Y',          # "Jan 7, 2026"
            '%m/%d/%Y',           # "01/07/2026"
            '%m-%d-%Y',           # "01-07-2026"
            '%Y-%m-%d',           # "2026-01-07"
            '%a/%b %d, %Y',       # "Wed/Jan 7, 2026" (CA format)
        ]

        # Clean up the string
        date_string = re.sub(r'\s+', ' ', date_string)

        for fmt in formats:
            try:
                return datetime.strptime(date_string, fmt)
            except ValueError:
                continue

        # Try regex extraction
        match = re.search(
            r'(\w+)\s+(\d{1,2}),?\s+(\d{4})',
            date_string
        )
        if match:
            try:
                clean_date = f"{match.group(1)} {match.group(2)}, {match.group(3)}"
                return datetime.strptime(clean_date, '%B %d, %Y')
            except ValueError:
                try:
                    return datetime.strptime(clean_date, '%b %d, %Y')
                except ValueError:
                    pass

        logger.warning(f"Could not parse date: {date_string}")
        return None


# Register scrapers for states using the generic scraper
@register_scraper('AZ')
class AZScraper(GenericStateScraper):
    """Arizona Lottery scraper."""
    state = 'AZ'


@register_scraper('AR')
class ARScraper(GenericStateScraper):
    """Arkansas Lottery scraper."""
    state = 'AR'


@register_scraper('CO')
class COScraper(GenericStateScraper):
    """Colorado Lottery scraper."""
    state = 'CO'


@register_scraper('FL')
class FLScraper(GenericStateScraper):
    """Florida Lottery scraper."""
    state = 'FL'


@register_scraper('GA')
class GAScraper(GenericStateScraper):
    """Georgia Lottery scraper."""
    state = 'GA'


@register_scraper('ID')
class IDScraper(GenericStateScraper):
    """Idaho Lottery scraper."""
    state = 'ID'


@register_scraper('IL')
class ILScraper(GenericStateScraper):
    """Illinois Lottery scraper."""
    state = 'IL'


@register_scraper('IN')
class INScraper(GenericStateScraper):
    """Indiana Lottery scraper."""
    state = 'IN'


@register_scraper('KS')
class KSScraper(GenericStateScraper):
    """Kansas Lottery scraper."""
    state = 'KS'


@register_scraper('LA')
class LAScraper(GenericStateScraper):
    """Louisiana Lottery scraper."""
    state = 'LA'


@register_scraper('ME')
class MEScraper(GenericStateScraper):
    """Maine Lottery scraper (Tri-State)."""
    state = 'ME'


# MD has custom scraper in md.py

@register_scraper('MA')
class MAScraper(GenericStateScraper):
    """Massachusetts Lottery scraper."""
    state = 'MA'


@register_scraper('MI')
class MIScraper(GenericStateScraper):
    """Michigan Lottery scraper."""
    state = 'MI'


@register_scraper('MN')
class MNScraper(GenericStateScraper):
    """Minnesota Lottery scraper."""
    state = 'MN'


@register_scraper('MO')
class MOScraper(GenericStateScraper):
    """Missouri Lottery scraper."""
    state = 'MO'


@register_scraper('NE')
class NEScraper(GenericStateScraper):
    """Nebraska Lottery scraper."""
    state = 'NE'


@register_scraper('NJ')
class NJScraper(GenericStateScraper):
    """New Jersey Lottery scraper."""
    state = 'NJ'


@register_scraper('NM')
class NMScraper(GenericStateScraper):
    """New Mexico Lottery scraper."""
    state = 'NM'


@register_scraper('NC')
class NCScraper(GenericStateScraper):
    """North Carolina Lottery scraper."""
    state = 'NC'


@register_scraper('OH')
class OHScraper(GenericStateScraper):
    """Ohio Lottery scraper."""
    state = 'OH'


@register_scraper('OK')
class OKScraper(GenericStateScraper):
    """Oklahoma Lottery scraper."""
    state = 'OK'


@register_scraper('OR')
class ORScraper(GenericStateScraper):
    """Oregon Lottery scraper."""
    state = 'OR'


@register_scraper('PA')
class PAScraper(GenericStateScraper):
    """Pennsylvania Lottery scraper."""
    state = 'PA'


@register_scraper('PR')
class PRScraper(GenericStateScraper):
    """Puerto Rico Lottery scraper."""
    state = 'PR'


@register_scraper('RI')
class RIScraper(GenericStateScraper):
    """Rhode Island Lottery scraper."""
    state = 'RI'


@register_scraper('SC')
class SCScraper(GenericStateScraper):
    """South Carolina Lottery scraper."""
    state = 'SC'


@register_scraper('SD')
class SDScraper(GenericStateScraper):
    """South Dakota Lottery scraper."""
    state = 'SD'


@register_scraper('TN')
class TNScraper(GenericStateScraper):
    """Tennessee Lottery scraper."""
    state = 'TN'


@register_scraper('TX')
class TXScraper(GenericStateScraper):
    """Texas Lottery scraper."""
    state = 'TX'


@register_scraper('VA')
class VAScraper(GenericStateScraper):
    """Virginia Lottery scraper."""
    state = 'VA'


@register_scraper('WA')
class WAScraper(GenericStateScraper):
    """Washington Lottery scraper."""
    state = 'WA'


@register_scraper('WV')
class WVScraper(GenericStateScraper):
    """West Virginia Lottery scraper."""
    state = 'WV'


@register_scraper('WI')
class WIScraper(GenericStateScraper):
    """Wisconsin Lottery scraper."""
    state = 'WI'
