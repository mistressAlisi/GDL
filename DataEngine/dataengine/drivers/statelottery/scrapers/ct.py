import logging
import re
from datetime import datetime
from typing import List, Optional, Tuple

from playwright.async_api import Page

from . import BaseScraper, register_scraper, DrawInfo

logger = logging.getLogger(__name__)


@register_scraper('CT')
class CTScraper(BaseScraper):
    """
    Connecticut Lottery scraper.
    CT Lottery uses AJAX to load winning numbers dynamically.
    """
    state = 'CT'

    async def _wait_for_content(self, page: Page, game) -> None:
        """Wait for page content to load."""
        try:
            # Wait longer for page to load and AJAX to complete
            await page.wait_for_load_state('domcontentloaded', timeout=15000)
            # Wait for table data to appear (look for dash-separated numbers)
            await page.wait_for_function(
                "document.body.innerText.includes(' - ')",
                timeout=20000
            )
            await page.wait_for_timeout(1500)
        except Exception as e:
            logger.warning(f"Timeout waiting for CT content: {e}")

    async def parse_all_numbers(
        self,
        page: Page,
        game,
        target_draw_label: Optional[str] = None
    ) -> Tuple[List[int], List[int]]:
        """Parse winning numbers from CT Lottery table.

        Numbers are displayed as: "3 - 4 - 6 - 7 - 34 - 38" in table rows.
        """
        try:
            # Try gridview first, fall back to body
            gridview = await page.query_selector('#gridview')
            if gridview:
                content = await gridview.inner_text()
            else:
                # Fall back to getting body content
                body = await page.query_selector('body')
                if body:
                    content = await body.inner_text()
                else:
                    logger.warning("CT: Could not find page content")
                    return [], []

            logger.info(f"CT content length: {len(content)}, preview: {content[:200]}")

            # CT displays numbers as "3 - 4 - 6 - 7 - 34 - 38" format
            # Use findall to get all 6-number sequences, take the first one (most recent draw)
            matches = re.findall(
                r'(\d+\s*-\s*\d+\s*-\s*\d+\s*-\s*\d+\s*-\s*\d+\s*-\s*\d+)',
                content
            )

            logger.info(f"CT found {len(matches)} matches")

            if matches:
                # Parse the first match (most recent draw)
                numbers = [int(n.strip()) for n in matches[0].split('-')]
                logger.info(f"Parsed CT Lotto! numbers: {numbers}")
                return numbers, []

            logger.warning(f"CT: Could not find 6-number sequence. Content length: {len(content)}")
            return [], []

        except Exception as e:
            logger.error(f"Error parsing CT Lotto! numbers: {e}")
            return [], []

    async def _parse_draw_info(self, page: Page, selectors: dict) -> DrawInfo:
        """Parse draw date from CT Lottery page."""
        draw_info = DrawInfo()

        try:
            # Try to find date in gridview content
            gridview = await page.query_selector('#gridview')
            if gridview:
                content = await gridview.inner_text()
                # Look for date patterns like "01/07/2026" or "Tuesday, January 7, 2026"
                date_match = re.search(r'(\d{1,2}/\d{1,2}/\d{4})', content)
                if date_match:
                    try:
                        draw_info.draw_date = datetime.strptime(
                            date_match.group(1), '%m/%d/%Y'
                        )
                    except ValueError:
                        pass
        except Exception as e:
            logger.warning(f"Error parsing CT draw date: {e}")

        return draw_info

    async def get_draw_label(self, page: Page, game) -> Optional[str]:
        """CT Lotto! has single evening draws."""
        return None
