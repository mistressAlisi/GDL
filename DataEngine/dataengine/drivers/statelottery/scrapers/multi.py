import logging
import re
from datetime import datetime
from typing import List, Optional, Tuple

from playwright.async_api import Page

from . import BaseScraper, register_scraper, ScrapeResult, DrawInfo

logger = logging.getLogger(__name__)


@register_scraper('MULTI')
class MultiStateScraper(BaseScraper):
    """
    Scraper for multi-state lottery games.
    Handles powerball.com, megamillions.com, lottoamerica.com.
    """
    state = 'MULTI'

    async def _wait_for_content(self, page: Page, game) -> None:
        """Wait for lottery content to load."""
        url = game.url.lower()

        try:
            if 'powerball.com' in url:
                # Wait for ball elements to appear
                await page.wait_for_selector(
                    '.item-powerball, .item-2by2',
                    timeout=15000
                )
                await page.wait_for_timeout(1500)
            elif 'megamillions.com' in url:
                await page.wait_for_selector('.ball', timeout=15000)
                await page.wait_for_timeout(1500)
            elif 'lottoamerica.com' in url:
                await page.wait_for_selector('.balls', timeout=15000)
                await page.wait_for_timeout(1000)
            else:
                await page.wait_for_load_state('networkidle')
                await page.wait_for_timeout(1500)
        except Exception as e:
            logger.warning(f"Timeout waiting for multi-state content: {e}")

    async def parse_all_numbers(
        self,
        page: Page,
        game,
        target_draw_label: Optional[str] = None
    ) -> Tuple[List[int], List[int]]:
        """Route to appropriate parser based on game slug."""
        slug = game.slug.lower()
        url = game.url.lower()

        if slug == 'powerball':
            return await self._parse_powerball(page, game)
        elif slug == 'mega-millions':
            return await self._parse_megamillions(page, game)
        elif slug == 'lotto-america':
            return await self._parse_lottoamerica(page, game)
        elif slug == '2by2':
            return await self._parse_2by2(page, game)
        elif slug == 'lucky-for-life':
            return await self._parse_luckyforlife(page, game)
        else:
            return await self._parse_generic(page, game)

    async def _parse_powerball(self, page: Page, game) -> Tuple[List[int], List[int]]:
        """Parse Powerball numbers from powerball.com."""
        try:
            main_numbers = []
            bonus_numbers = []

            # Try CSS selectors first
            white_balls = await page.query_selector_all('.white-balls.item-powerball')
            for ball in white_balls[:5]:
                text = await ball.text_content()
                if text and text.strip().isdigit():
                    main_numbers.append(int(text.strip()))

            red_balls = await page.query_selector_all('.powerball.item-powerball')
            for ball in red_balls[:1]:
                text = await ball.text_content()
                if text and text.strip().isdigit():
                    bonus_numbers.append(int(text.strip()))

            if len(main_numbers) == game.main_count and len(bonus_numbers) == game.bonus_count:
                logger.info(f"Parsed Powerball (CSS): {main_numbers} + {bonus_numbers}")
                return main_numbers, bonus_numbers

            # Fallback: text-based parsing
            body = await page.query_selector('body')
            if body:
                content = await body.inner_text()
                lines = content.split('\n')

                found_date = False
                main_numbers = []
                bonus_numbers = []

                for line in lines:
                    line_stripped = line.strip()

                    # Look for date pattern to mark start of results
                    if re.match(r'^(Mon|Tue|Wed|Thu|Fri|Sat|Sun),?\s+', line_stripped):
                        found_date = True
                        main_numbers = []
                        bonus_numbers = []
                        continue

                    if not found_date:
                        continue

                    # Stop at "Power Play" which comes after the bonus
                    if 'power play' in line_stripped.lower():
                        break

                    # Parse numbers
                    if line_stripped.isdigit():
                        num = int(line_stripped)
                        if len(main_numbers) < game.main_count:
                            if game.main_range_min <= num <= game.main_range_max:
                                main_numbers.append(num)
                        elif len(bonus_numbers) < game.bonus_count:
                            if game.bonus_range_min <= num <= game.bonus_range_max:
                                bonus_numbers.append(num)

                    # Check if we have all numbers
                    if len(main_numbers) == game.main_count and len(bonus_numbers) == game.bonus_count:
                        break

            if len(main_numbers) == game.main_count:
                logger.info(f"Parsed Powerball (text): {main_numbers} + {bonus_numbers}")
                return main_numbers, bonus_numbers

            logger.warning("Powerball: Could not find valid numbers")
            return [], []

        except Exception as e:
            logger.error(f"Error parsing Powerball: {e}")
            return [], []

    async def _parse_megamillions(self, page: Page, game) -> Tuple[List[int], List[int]]:
        """Parse Mega Millions numbers from megamillions.com."""
        try:
            main_numbers = []
            bonus_numbers = []

            # White balls: .ball.winNum1 through .ball.winNum5
            for i in range(1, 6):
                ball = await page.query_selector(f'.ball.winNum{i}')
                if ball:
                    text = await ball.text_content()
                    if text and text.strip().isdigit():
                        main_numbers.append(int(text.strip()))

            # Mega Ball (gold): .yellowBall.winNumMB
            mega_ball = await page.query_selector('.yellowBall.winNumMB')
            if mega_ball:
                text = await mega_ball.text_content()
                if text and text.strip().isdigit():
                    bonus_numbers.append(int(text.strip()))

            logger.info(f"Parsed Mega Millions: {main_numbers} + {bonus_numbers}")
            return main_numbers, bonus_numbers

        except Exception as e:
            logger.error(f"Error parsing Mega Millions: {e}")
            return [], []

    async def _parse_lottoamerica(self, page: Page, game) -> Tuple[List[int], List[int]]:
        """Parse Lotto America numbers from lottoamerica.com."""
        try:
            main_numbers = []
            bonus_numbers = []

            # Numbers are in .balls div, separated by whitespace
            balls_div = await page.query_selector('.balls')
            if balls_div:
                text = await balls_div.text_content()
                if text:
                    # Extract all numbers from the text
                    numbers = re.findall(r'\d+', text)
                    numbers = [int(n) for n in numbers]

                    # Lotto America: 5 main + 1 Star Ball
                    if len(numbers) >= 6:
                        main_numbers = numbers[:5]
                        bonus_numbers = [numbers[5]]

            logger.info(f"Parsed Lotto America: {main_numbers} + {bonus_numbers}")
            return main_numbers, bonus_numbers

        except Exception as e:
            logger.error(f"Error parsing Lotto America: {e}")
            return [], []

    async def _parse_2by2(self, page: Page, game) -> Tuple[List[int], List[int]]:
        """Parse 2by2 numbers from powerball.com/2by2."""
        try:
            main_numbers = []
            bonus_numbers = []

            # Red balls (first 2): .red-balls.item-2by2
            red_balls = await page.query_selector_all('.red-balls.item-2by2')
            for ball in red_balls[:2]:
                text = await ball.text_content()
                if text and text.strip().isdigit():
                    main_numbers.append(int(text.strip()))

            # White balls (second 2): .white-balls.item-2by2
            white_balls = await page.query_selector_all('.white-balls.item-2by2')
            for ball in white_balls[:2]:
                text = await ball.text_content()
                if text and text.strip().isdigit():
                    bonus_numbers.append(int(text.strip()))

            logger.info(f"Parsed 2by2: {main_numbers} + {bonus_numbers}")
            return main_numbers, bonus_numbers

        except Exception as e:
            logger.error(f"Error parsing 2by2: {e}")
            return [], []

    async def _parse_luckyforlife(self, page: Page, game) -> Tuple[List[int], List[int]]:
        """Parse Lucky for Life numbers from NH Lottery."""
        try:
            main_numbers = []
            bonus_numbers = []

            # Main numbers: .winning-numbers__single-number (first 5)
            all_nums = await page.query_selector_all('.winning-numbers__single-number')
            for num in all_nums[:5]:
                text = await num.text_content()
                if text and text.strip().isdigit():
                    main_numbers.append(int(text.strip()))

            # Lucky Ball: .winning-numbers__single-number--luckyball
            lucky_ball = await page.query_selector('.winning-numbers__single-number--luckyball')
            if lucky_ball:
                text = await lucky_ball.text_content()
                if text and text.strip().isdigit():
                    bonus_numbers.append(int(text.strip()))

            logger.info(f"Parsed Lucky for Life: {main_numbers} + {bonus_numbers}")
            return main_numbers, bonus_numbers

        except Exception as e:
            logger.error(f"Error parsing Lucky for Life: {e}")
            return [], []

    async def _parse_generic(self, page: Page, game) -> Tuple[List[int], List[int]]:
        """Generic parser using configured selectors."""
        selectors = game.selectors
        selector = selectors.get('all_numbers')

        if not selector:
            return [], []

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

            main_count = game.main_count
            bonus_count = getattr(game, 'bonus_count', 0) or 0

            main_numbers = all_numbers[:main_count]
            bonus_numbers = all_numbers[main_count:main_count + bonus_count] if bonus_count else []

            return main_numbers, bonus_numbers

        except Exception as e:
            logger.error(f"Error in generic parser: {e}")
            return [], []

    async def _parse_draw_info(self, page: Page, selectors: dict) -> DrawInfo:
        """Parse draw information."""
        draw_info = DrawInfo()

        date_selector = selectors.get('draw_date')
        if date_selector:
            try:
                element = await page.query_selector(date_selector)
                if element:
                    text = await element.text_content()
                    draw_info.draw_date = self._parse_date(text)
            except Exception as e:
                logger.warning(f"Error parsing draw date: {e}")

        if not draw_info.draw_date:
            draw_info.draw_date = await self._find_draw_date(page)

        return draw_info

    async def _find_draw_date(self, page: Page) -> Optional[datetime]:
        """Try to find draw date using common patterns."""
        try:
            date_selectors = [
                '.draw-date', '.date', '.card-header',
                '[class*="date"]', 'h2', 'h3',
            ]

            for selector in date_selectors:
                elements = await page.query_selector_all(selector)
                for element in elements:
                    text = await element.text_content()
                    if text:
                        parsed = self._parse_date(text)
                        if parsed:
                            return parsed

            return None

        except Exception as e:
            logger.warning(f"Error finding draw date: {e}")
            return None

    async def get_draw_label(self, page: Page, game) -> Optional[str]:
        """Multi-state games typically have single daily draws."""
        return None

    def _parse_date(self, date_string: Optional[str]) -> Optional[datetime]:
        """Parse date strings."""
        if not date_string:
            return None

        date_string = date_string.strip()

        formats = [
            '%a, %b %d, %Y',      # "Wed, Jan 7, 2026"
            '%A, %B %d, %Y',      # "Wednesday, January 7, 2026"
            '%B %d, %Y',          # "January 7, 2026"
            '%b %d, %Y',          # "Jan 7, 2026"
            '%m/%d/%Y',           # "01/07/2026"
            '%m-%d-%Y',           # "01-07-2026"
            '%Y-%m-%d',           # "2026-01-07"
        ]

        date_string = re.sub(r'\s+', ' ', date_string)

        for fmt in formats:
            try:
                return datetime.strptime(date_string, fmt)
            except ValueError:
                continue

        # Try regex extraction
        match = re.search(r'(\w{3}),?\s+(\w{3})\s+(\d{1,2}),?\s+(\d{4})', date_string)
        if match:
            try:
                clean_date = f"{match.group(2)} {match.group(3)}, {match.group(4)}"
                return datetime.strptime(clean_date, '%b %d, %Y')
            except ValueError:
                pass

        match = re.search(r'(\w+)\s+(\d{1,2}),?\s+(\d{4})', date_string)
        if match:
            try:
                clean_date = f"{match.group(1)} {match.group(2)}, {match.group(3)}"
                return datetime.strptime(clean_date, '%B %d, %Y')
            except ValueError:
                pass

        return None
