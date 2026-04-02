import logging
import re
from datetime import datetime
from typing import List, Optional, Tuple

from playwright.async_api import Page

from . import BaseScraper, register_scraper, DrawInfo

logger = logging.getLogger(__name__)


@register_scraper('MD')
class MDScraper(BaseScraper):
    """
    Maryland Lottery scraper.
    MD Lottery uses a tabbed interface - must click Multi-Match tab.
    Numbers are displayed in concatenated format (e.g., "313435374041" for 31-34-35-37-40-41).
    """
    state = 'MD'

    async def _wait_for_content(self, page: Page, game) -> None:
        """Wait for page content to load and click Multi-Match tab."""
        try:
            await page.wait_for_load_state('domcontentloaded', timeout=15000)
            await page.wait_for_timeout(2000)

            # Click the Multi-Match tab using correct selector
            tab_link = await page.query_selector('a[href="#multi-match"]')
            if tab_link:
                logger.info("MD: Clicking Multi-Match tab")
                await tab_link.click()
                await page.wait_for_timeout(2000)
            else:
                logger.warning("MD: Multi-Match tab not found")

        except Exception as e:
            logger.warning(f"Timeout waiting for MD content: {e}")

    async def parse_all_numbers(
        self,
        page: Page,
        game,
        target_draw_label: Optional[str] = None
    ) -> Tuple[List[int], List[int]]:
        """Parse winning numbers from MD Lottery.

        Numbers are displayed in concatenated format: "313435374041"
        representing 6 two-digit numbers: 31, 34, 35, 37, 40, 41
        """
        try:
            # Get the Multi-Match table content
            table = await page.query_selector('#table_multi-match')
            if table:
                content = await table.inner_text()
                logger.info(f"MD table content length: {len(content)}")
            else:
                # Fallback to the panel
                panel = await page.query_selector('#multi-match')
                if panel:
                    content = await panel.inner_text()
                else:
                    body = await page.query_selector('body')
                    content = await body.inner_text() if body else ''

            # Look for concatenated 12-digit sequences (6 two-digit numbers 01-43)
            matches = re.findall(r'(\d{12})', content)

            logger.info(f"MD found {len(matches)} 12-digit matches")

            if matches:
                # Parse the first match (most recent draw)
                concat_nums = matches[0]
                # Split into 6 two-digit numbers
                numbers = []
                for i in range(0, 12, 2):
                    num = int(concat_nums[i:i+2])
                    numbers.append(num)

                # Validate numbers are in range 1-43
                if all(1 <= n <= 43 for n in numbers):
                    logger.info(f"Parsed MD Multi-Match numbers: {numbers}")
                    return numbers, []
                else:
                    logger.warning(f"MD numbers out of range: {numbers}")

            logger.warning(f"MD: Could not find valid number sequence")
            return [], []

        except Exception as e:
            logger.error(f"Error parsing MD Multi-Match numbers: {e}")
            return [], []

    async def _parse_draw_info(self, page: Page, selectors: dict) -> DrawInfo:
        """Parse draw date from MD Lottery page."""
        draw_info = DrawInfo()

        try:
            table = await page.query_selector('#table_multi-match')
            if table:
                content = await table.inner_text()
                # Look for date patterns like "01/08/26" or "01/08/2026"
                date_match = re.search(r'(\d{1,2}/\d{1,2}/\d{2,4})', content)
                if date_match:
                    date_str = date_match.group(1)
                    try:
                        if len(date_str.split('/')[-1]) == 2:
                            draw_info.draw_date = datetime.strptime(date_str, '%m/%d/%y')
                        else:
                            draw_info.draw_date = datetime.strptime(date_str, '%m/%d/%Y')
                    except ValueError:
                        pass
        except Exception as e:
            logger.warning(f"Error parsing MD draw date: {e}")

        return draw_info

    async def get_draw_label(self, page: Page, game) -> Optional[str]:
        """MD Multi-Match has single evening draws."""
        return None
