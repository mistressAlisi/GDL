"""
Custom scrapers for state lottery websites that need specific handling.
Each scraper handles the unique HTML structure of its respective state lottery site.
"""
import logging
import re
from datetime import datetime
from typing import List, Optional, Tuple

from playwright.async_api import Page

from . import BaseScraper, register_scraper, DrawInfo

logger = logging.getLogger(__name__)


@register_scraper('TX')
class TXScraper(BaseScraper):
    """
    Texas Lottery scraper.
    Texas uses simple ol/li elements for winning numbers.
    """
    state = 'TX'

    async def _wait_for_content(self, page: Page, game) -> None:
        try:
            await page.wait_for_load_state('domcontentloaded', timeout=15000)
            await page.wait_for_selector('ol li', timeout=10000)
            await page.wait_for_timeout(1000)
        except Exception as e:
            logger.warning(f"Timeout waiting for TX content: {e}")

    async def parse_all_numbers(
        self,
        page: Page,
        game,
        target_draw_label: Optional[str] = None
    ) -> Tuple[List[int], List[int]]:
        try:
            # Texas uses ol li for numbers
            elements = await page.query_selector_all('ol li')
            numbers = []

            for element in elements:
                text = await element.text_content()
                if text:
                    text = text.strip()
                    if text.isdigit():
                        num = int(text)
                        if 1 <= num <= 60:  # Reasonable range for TX games
                            numbers.append(num)

                # Stop after getting enough numbers for this game
                expected = game.main_count + (game.bonus_count or 0)
                if len(numbers) >= expected:
                    break

            if not numbers:
                logger.warning("TX: No numbers found in ol li elements")
                return [], []

            main_count = game.main_count
            bonus_count = game.bonus_count or 0

            main_numbers = numbers[:main_count]
            bonus_numbers = numbers[main_count:main_count + bonus_count] if bonus_count else []

            logger.info(f"TX parsed: main={main_numbers}, bonus={bonus_numbers}")
            return main_numbers, bonus_numbers

        except Exception as e:
            logger.error(f"Error parsing TX numbers: {e}")
            return [], []

    async def _parse_draw_info(self, page: Page, selectors: dict) -> DrawInfo:
        draw_info = DrawInfo()
        try:
            # Look for date in h3 heading
            h3_elements = await page.query_selector_all('h3')
            for h3 in h3_elements:
                text = await h3.text_content()
                if text and 'winning numbers' in text.lower():
                    # Extract date from "Lotto Texas Winning Numbers for 01/07/2026"
                    match = re.search(r'(\d{1,2}/\d{1,2}/\d{4})', text)
                    if match:
                        try:
                            draw_info.draw_date = datetime.strptime(match.group(1), '%m/%d/%Y')
                        except ValueError:
                            pass
                    break
        except Exception as e:
            logger.warning(f"Error parsing TX draw date: {e}")
        return draw_info

    async def get_draw_label(self, page: Page, game) -> Optional[str]:
        return None


@register_scraper('NC')
class NCScraper(BaseScraper):
    """
    North Carolina Lottery scraper.
    NC displays multiple games - need to find the specific game section by jackpot/identifier.
    Cash 5 has $225,000 jackpot, numbers appear on separate lines before DOUBLEPLAY.
    """
    state = 'NC'

    async def _wait_for_content(self, page: Page, game) -> None:
        try:
            await page.wait_for_load_state('domcontentloaded', timeout=15000)
            await page.wait_for_timeout(4000)
        except Exception as e:
            logger.warning(f"Timeout waiting for NC content: {e}")

    async def parse_all_numbers(
        self,
        page: Page,
        game,
        target_draw_label: Optional[str] = None
    ) -> Tuple[List[int], List[int]]:
        try:
            body = await page.query_selector('body')
            if not body:
                return [], []

            content = await body.inner_text()
            lines = content.split('\n')

            # Find the game section by looking for identifying markers
            # Cash 5: look for $225,000 jackpot
            game_markers = {
                'cash 5': ['225,000', '250,000', '300,000'],  # Cash 5 jackpots vary
            }

            game_name_lower = game.name.lower()
            markers = game_markers.get(game_name_lower, [])

            found_section = False
            numbers = []

            for i, line in enumerate(lines):
                line_stripped = line.strip()

                # Check for game marker
                if not found_section:
                    for marker in markers:
                        if marker in line_stripped:
                            found_section = True
                            break
                    continue

                # Collecting numbers
                if found_section:
                    if line_stripped.isdigit():
                        num = int(line_stripped)
                        if game.main_range_min <= num <= game.main_range_max:
                            numbers.append(num)
                            if len(numbers) >= game.main_count:
                                logger.info(f"NC parsed {game.name}: {numbers}")
                                return numbers[:game.main_count], []
                    elif 'DOUBLEPLAY' in line_stripped.upper() or 'Game Info' in line_stripped:
                        # End of main numbers
                        if len(numbers) >= game.main_count:
                            logger.info(f"NC parsed {game.name}: {numbers[:game.main_count]}")
                            return numbers[:game.main_count], []
                        break

            logger.warning(f"NC: Could not find {game.name} numbers")
            return [], []

        except Exception as e:
            logger.error(f"Error parsing NC numbers: {e}")
            return [], []

    async def _parse_draw_info(self, page: Page, selectors: dict) -> DrawInfo:
        draw_info = DrawInfo()
        try:
            body = await page.query_selector('body')
            if body:
                content = await body.inner_text()
                match = re.search(r'(\w+,?\s+\w+\s+\d{1,2},?\s+\d{4})', content)
                if match:
                    date_str = match.group(1)
                    for fmt in ['%A, %b %d, %Y', '%A %b %d, %Y', '%B %d, %Y']:
                        try:
                            draw_info.draw_date = datetime.strptime(date_str, fmt)
                            break
                        except ValueError:
                            continue
        except Exception as e:
            logger.warning(f"Error parsing NC draw date: {e}")
        return draw_info

    async def get_draw_label(self, page: Page, game) -> Optional[str]:
        return None


@register_scraper('KS')
class KSScraper(BaseScraper):
    """
    Kansas Lottery scraper.
    Uses game-specific selectors to avoid picking up multi-state game numbers.
    """
    state = 'KS'

    async def _wait_for_content(self, page: Page, game) -> None:
        try:
            await page.wait_for_load_state('networkidle', timeout=20000)
            await page.wait_for_timeout(2000)
        except Exception as e:
            logger.warning(f"Timeout waiting for KS content: {e}")

    async def parse_all_numbers(
        self,
        page: Page,
        game,
        target_draw_label: Optional[str] = None
    ) -> Tuple[List[int], List[int]]:
        try:
            # Parse page text to find numbers after "Winning Numbers" section
            body = await page.query_selector('body')
            if not body:
                logger.warning("KS: No body element found")
                return [], []

            content = await body.inner_text()
            lines = content.split('\n')

            found_winning_numbers = False
            found_date = False
            main_numbers = []
            bonus_numbers = []

            for line in lines:
                line_stripped = line.strip()
                line_lower = line_stripped.lower()

                # Look for "Winning Numbers" section
                if 'winning numbers' in line_lower and 'check' not in line_lower:
                    found_winning_numbers = True
                    continue

                if not found_winning_numbers:
                    continue

                # Look for date after "Winning Numbers"
                if not found_date:
                    if re.match(r'\d{1,2}/\d{1,2}/\d{4}', line_stripped):
                        found_date = True
                        continue

                # Stop at certain sections
                if 'game odds' in line_lower or 'prize' in line_lower or 'jackpot' in line_lower:
                    break

                # Parse numbers - each on its own line
                if line_stripped.isdigit():
                    num = int(line_stripped)
                    if len(main_numbers) < game.main_count:
                        if game.main_range_min <= num <= game.main_range_max:
                            main_numbers.append(num)
                    elif game.bonus_count and len(bonus_numbers) < game.bonus_count:
                        if game.bonus_range_min <= num <= game.bonus_range_max:
                            bonus_numbers.append(num)

                # Stop when we have all numbers
                if len(main_numbers) == game.main_count:
                    if not game.bonus_count or len(bonus_numbers) == game.bonus_count:
                        break

            if len(main_numbers) == game.main_count:
                logger.info(f"KS parsed: main={main_numbers}, bonus={bonus_numbers}")
                return main_numbers, bonus_numbers

            logger.warning(f"KS: Found only {len(main_numbers)} main numbers")
            return [], []

        except Exception as e:
            logger.error(f"Error parsing KS numbers: {e}")
            return [], []

    async def _parse_draw_info(self, page: Page, selectors: dict) -> DrawInfo:
        return DrawInfo()

    async def get_draw_label(self, page: Page, game) -> Optional[str]:
        return None


@register_scraper('LA')
class LAScraper(BaseScraper):
    """
    Louisiana Lottery scraper.
    LA uses table format for winning numbers.
    """
    state = 'LA'

    async def _wait_for_content(self, page: Page, game) -> None:
        try:
            await page.wait_for_load_state('networkidle', timeout=15000)
            await page.wait_for_timeout(2000)
        except Exception as e:
            logger.warning(f"Timeout waiting for LA content: {e}")

    async def parse_all_numbers(
        self,
        page: Page,
        game,
        target_draw_label: Optional[str] = None
    ) -> Tuple[List[int], List[int]]:
        try:
            # LA page shows multiple games - need to find the correct section
            body = await page.query_selector('body')
            if not body:
                logger.warning("LA: No body element found")
                return [], []

            content = await body.inner_text()
            lines = content.split('\n')

            # Game identifiers for each LA game
            game_markers = {
                'la-lotto': ['$550,000', 'cash prize'],
                'la-easy5': ['$60,000', 'cash prize'],
            }

            game_name_lower = game.slug.lower()
            markers = game_markers.get(game_name_lower, [])

            # Find the game section by looking for its jackpot marker
            found_section = False
            numbers = []

            for i, line in enumerate(lines):
                line_stripped = line.strip()
                line_lower = line_stripped.lower()

                # For Lotto and Easy5, find by jackpot amount
                if markers:
                    for marker in markers:
                        if marker.lower() in line_lower:
                            # Look backwards for numbers before this marker
                            found_section = True
                            # Collect numbers from the lines above
                            for j in range(max(0, i - 10), i):
                                prev_line = lines[j].strip()
                                if prev_line.isdigit():
                                    num = int(prev_line)
                                    if game.main_range_min <= num <= game.main_range_max:
                                        numbers.append(num)
                            break

                if found_section and len(numbers) >= game.main_count:
                    break

            # Take the last N numbers (the ones closest to the marker)
            if len(numbers) >= game.main_count:
                main = numbers[-game.main_count:]
                if len(set(main)) == len(main):  # No duplicates
                    logger.info(f"LA parsed: {main}")
                    return main, []

            logger.warning("LA: Could not find valid numbers")
            return [], []

        except Exception as e:
            logger.error(f"Error parsing LA numbers: {e}")
            return [], []

    async def _parse_draw_info(self, page: Page, selectors: dict) -> DrawInfo:
        return DrawInfo()

    async def get_draw_label(self, page: Page, game) -> Optional[str]:
        return None


@register_scraper('VA')
class VAScraper(BaseScraper):
    """
    Virginia Lottery scraper.
    VA displays numbers on separate lines after "Winning Numbers" heading.
    """
    state = 'VA'

    async def _wait_for_content(self, page: Page, game) -> None:
        try:
            await page.wait_for_load_state('domcontentloaded', timeout=15000)
            await page.wait_for_timeout(3000)
        except Exception as e:
            logger.warning(f"Timeout waiting for VA content: {e}")

    async def parse_all_numbers(
        self,
        page: Page,
        game,
        target_draw_label: Optional[str] = None
    ) -> Tuple[List[int], List[int]]:
        try:
            body = await page.query_selector('body')
            if not body:
                return [], []

            content = await body.inner_text()
            lines = content.split('\n')

            # Look for "Winning Numbers" section and collect numbers on following lines
            found_winning = False
            numbers = []

            for i, line in enumerate(lines):
                line_stripped = line.strip()

                # Look for "Winning Numbers" heading
                if 'winning number' in line_stripped.lower():
                    found_winning = True
                    continue

                if found_winning:
                    # Check if this line is just a number
                    if line_stripped.isdigit():
                        num = int(line_stripped)
                        if game.main_range_min <= num <= game.main_range_max:
                            numbers.append(num)
                            if len(numbers) >= game.main_count + (game.bonus_count or 0):
                                break
                    elif numbers and not line_stripped.isdigit():
                        # Non-number found after collecting some numbers - might be end of sequence
                        if len(numbers) >= game.main_count:
                            break

            if len(numbers) >= game.main_count:
                main = numbers[:game.main_count]
                bonus = numbers[game.main_count:game.main_count + (game.bonus_count or 0)] if game.bonus_count else []
                if len(set(main)) == len(main):  # No duplicates
                    logger.info(f"VA parsed: main={main}, bonus={bonus}")
                    return main, bonus

            logger.warning("VA: Could not find valid numbers")
            return [], []

        except Exception as e:
            logger.error(f"Error parsing VA numbers: {e}")
            return [], []

    async def _parse_draw_info(self, page: Page, selectors: dict) -> DrawInfo:
        return DrawInfo()

    async def get_draw_label(self, page: Page, game) -> Optional[str]:
        return None


@register_scraper('SD')
class SDScraper(BaseScraper):
    """
    South Dakota Lottery scraper.
    """
    state = 'SD'

    async def _wait_for_content(self, page: Page, game) -> None:
        try:
            await page.wait_for_load_state('networkidle', timeout=15000)
            await page.wait_for_timeout(2000)
        except Exception as e:
            logger.warning(f"Timeout waiting for SD content: {e}")

    async def parse_all_numbers(
        self,
        page: Page,
        game,
        target_draw_label: Optional[str] = None
    ) -> Tuple[List[int], List[int]]:
        try:
            # Try common selectors
            selectors = [
                '.winning-numbers li',
                '.ball',
                '.number',
                '.results .num',
            ]

            for selector in selectors:
                elements = await page.query_selector_all(selector)
                if elements:
                    numbers = []
                    for el in elements[:game.main_count]:
                        text = await el.text_content()
                        if text:
                            text = text.strip()
                            if text.isdigit():
                                num = int(text)
                                if game.main_range_min <= num <= game.main_range_max:
                                    numbers.append(num)

                    if len(numbers) == game.main_count and len(set(numbers)) == len(numbers):
                        logger.info(f"SD parsed: {numbers}")
                        return numbers, []

            # Fallback: extract from page content
            body = await page.query_selector('body')
            if body:
                content = await body.inner_text()
                # Find number sequences
                matches = re.findall(r'\b(\d{1,2})\b', content)
                seen = set()
                numbers = []
                for m in matches:
                    num = int(m)
                    if (game.main_range_min <= num <= game.main_range_max and
                        num not in seen):
                        numbers.append(num)
                        seen.add(num)
                        if len(numbers) == game.main_count:
                            logger.info(f"SD parsed from text: {numbers}")
                            return numbers, []

            logger.warning("SD: Could not find valid numbers")
            return [], []

        except Exception as e:
            logger.error(f"Error parsing SD numbers: {e}")
            return [], []

    async def _parse_draw_info(self, page: Page, selectors: dict) -> DrawInfo:
        return DrawInfo()

    async def get_draw_label(self, page: Page, game) -> Optional[str]:
        return None


@register_scraper('AZ')
class AZScraper(BaseScraper):
    """
    Arizona Lottery scraper.
    AZ uses dynamic content loaded via JavaScript.
    """
    state = 'AZ'

    async def _wait_for_content(self, page: Page, game) -> None:
        try:
            await page.wait_for_load_state('networkidle', timeout=20000)
            await page.wait_for_timeout(3000)
        except Exception as e:
            logger.warning(f"Timeout waiting for AZ content: {e}")

    async def parse_all_numbers(
        self,
        page: Page,
        game,
        target_draw_label: Optional[str] = None
    ) -> Tuple[List[int], List[int]]:
        try:
            # Try various selectors for AZ site
            selectors = [
                'table td',
                '.winning-numbers td',
                '.ball',
                '.number',
                'ol li',
                'ul.numbers li',
            ]

            for selector in selectors:
                elements = await page.query_selector_all(selector)
                if elements:
                    numbers = []
                    for el in elements:
                        text = await el.text_content()
                        if text:
                            text = text.strip()
                            if text.isdigit():
                                num = int(text)
                                if game.main_range_min <= num <= game.main_range_max:
                                    numbers.append(num)
                                    if len(numbers) >= game.main_count:
                                        break

                    if len(numbers) >= game.main_count:
                        main = numbers[:game.main_count]
                        if len(set(main)) == len(main):
                            logger.info(f"AZ parsed: {main}")
                            return main, []

            # Fallback: extract from page content
            body = await page.query_selector('body')
            if body:
                content = await body.inner_text()
                # Find first sequence of valid numbers
                matches = re.findall(r'\b(\d{1,2})\b', content)
                numbers = []
                for m in matches:
                    num = int(m)
                    if game.main_range_min <= num <= game.main_range_max:
                        numbers.append(num)
                        if len(numbers) >= game.main_count:
                            if len(set(numbers)) == len(numbers):
                                logger.info(f"AZ parsed from text: {numbers}")
                                return numbers, []
                            numbers = []  # Had duplicates, try again

            logger.warning("AZ: Could not find valid numbers")
            return [], []

        except Exception as e:
            logger.error(f"Error parsing AZ numbers: {e}")
            return [], []

    async def _parse_draw_info(self, page: Page, selectors: dict) -> DrawInfo:
        return DrawInfo()

    async def get_draw_label(self, page: Page, game) -> Optional[str]:
        return None


@register_scraper('IL')
class ILScraper(BaseScraper):
    """
    Illinois Lottery scraper.
    IL site blocks automated access - needs specific handling.
    """
    state = 'IL'

    async def _wait_for_content(self, page: Page, game) -> None:
        try:
            await page.wait_for_load_state('networkidle', timeout=20000)
            await page.wait_for_timeout(3000)
        except Exception as e:
            logger.warning(f"Timeout waiting for IL content: {e}")

    async def parse_all_numbers(
        self,
        page: Page,
        game,
        target_draw_label: Optional[str] = None
    ) -> Tuple[List[int], List[int]]:
        try:
            # IL uses specific classes for their balls
            selectors = [
                '.ball',
                '.winning-number',
                '.lotto-ball',
                '.number-ball',
                '.results-ball',
            ]

            for selector in selectors:
                elements = await page.query_selector_all(selector)
                if elements:
                    numbers = []
                    for el in elements[:game.main_count + (game.bonus_count or 0)]:
                        text = await el.text_content()
                        if text:
                            text = text.strip()
                            if text.isdigit():
                                numbers.append(int(text))

                    if len(numbers) >= game.main_count:
                        main = numbers[:game.main_count]
                        bonus = numbers[game.main_count:] if game.bonus_count else []
                        logger.info(f"IL parsed: main={main}, bonus={bonus}")
                        return main, bonus

            logger.warning("IL: Could not find valid numbers")
            return [], []

        except Exception as e:
            logger.error(f"Error parsing IL numbers: {e}")
            return [], []

    async def _parse_draw_info(self, page: Page, selectors: dict) -> DrawInfo:
        return DrawInfo()

    async def get_draw_label(self, page: Page, game) -> Optional[str]:
        return None


@register_scraper('MI')
class MIScraper(BaseScraper):
    """
    Michigan Lottery scraper.
    MI shows multiple games - find section by game name, numbers follow "Showing:" date.
    """
    state = 'MI'

    async def _wait_for_content(self, page: Page, game) -> None:
        try:
            await page.wait_for_load_state('domcontentloaded', timeout=20000)
            await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            await page.wait_for_timeout(4000)
        except Exception as e:
            logger.warning(f"Timeout waiting for MI content: {e}")

    async def parse_all_numbers(
        self,
        page: Page,
        game,
        target_draw_label: Optional[str] = None
    ) -> Tuple[List[int], List[int]]:
        try:
            body = await page.query_selector('body')
            if not body:
                return [], []

            content = await body.inner_text()
            lines = content.split('\n')

            # Find section for our game - look for "buy {game_name} now" pattern
            game_name_lower = game.name.lower()
            found_game = False
            found_showing = False
            numbers = []

            for i, line in enumerate(lines):
                line_stripped = line.strip()
                line_lower = line_stripped.lower()

                # Find game section
                if not found_game:
                    if f'buy {game_name_lower}' in line_lower or game_name_lower in line_lower:
                        found_game = True
                    continue

                # In game section, look for "Showing:" date line
                if found_game and not found_showing:
                    if 'showing:' in line_lower:
                        found_showing = True
                        continue

                # Collect numbers after "Showing:" line
                if found_showing:
                    if line_stripped.isdigit():
                        num = int(line_stripped)
                        if game.main_range_min <= num <= game.main_range_max:
                            numbers.append(num)
                            if len(numbers) >= game.main_count:
                                break
                    elif numbers and ('past drawings' in line_lower or 'double play' in line_lower):
                        # End of main numbers
                        break

            if len(numbers) >= game.main_count:
                main = numbers[:game.main_count]
                logger.info(f"MI parsed {game.name}: {main}")
                return main, []

            logger.warning(f"MI: Could not find {game.name} numbers")
            return [], []

        except Exception as e:
            logger.error(f"Error parsing MI numbers: {e}")
            return [], []

    async def _parse_draw_info(self, page: Page, selectors: dict) -> DrawInfo:
        return DrawInfo()

    async def get_draw_label(self, page: Page, game) -> Optional[str]:
        return None


@register_scraper('MO')
class MOScraper(BaseScraper):
    """
    Missouri Lottery scraper.
    Note: MO Lotto game has ended as of Oct 2025.
    """
    state = 'MO'

    async def _wait_for_content(self, page: Page, game) -> None:
        try:
            await page.wait_for_load_state('networkidle', timeout=15000)
            await page.wait_for_timeout(2000)
        except Exception as e:
            logger.warning(f"Timeout waiting for MO content: {e}")

    async def parse_all_numbers(
        self,
        page: Page,
        game,
        target_draw_label: Optional[str] = None
    ) -> Tuple[List[int], List[int]]:
        try:
            # Check if game has ended
            body = await page.query_selector('body')
            if body:
                content = await body.inner_text()
                if 'game has ended' in content.lower():
                    logger.warning(f"MO: {game.name} game has ended")
                    return [], []

            selectors = [
                '.winning-numbers li',
                '.ball',
                '.number',
            ]

            for selector in selectors:
                elements = await page.query_selector_all(selector)
                if elements:
                    numbers = []
                    for el in elements[:game.main_count]:
                        text = await el.text_content()
                        if text:
                            text = text.strip()
                            if text.isdigit():
                                numbers.append(int(text))

                    if len(numbers) >= game.main_count:
                        logger.info(f"MO parsed: {numbers}")
                        return numbers[:game.main_count], []

            logger.warning("MO: Could not find valid numbers")
            return [], []

        except Exception as e:
            logger.error(f"Error parsing MO numbers: {e}")
            return [], []

    async def _parse_draw_info(self, page: Page, selectors: dict) -> DrawInfo:
        return DrawInfo()

    async def get_draw_label(self, page: Page, game) -> Optional[str]:
        return None


@register_scraper('OH')
class OHScraper(BaseScraper):
    """
    Ohio Lottery scraper.
    OH displays multiple games on each page - need to find the specific game section.
    """
    state = 'OH'

    async def _wait_for_content(self, page: Page, game) -> None:
        try:
            await page.wait_for_load_state('networkidle', timeout=20000)
            await page.wait_for_timeout(3000)
        except Exception as e:
            logger.warning(f"Timeout waiting for OH content: {e}")

    async def parse_all_numbers(
        self,
        page: Page,
        game,
        target_draw_label: Optional[str] = None
    ) -> Tuple[List[int], List[int]]:
        try:
            # Ohio page displays multiple games - find the one matching our game name
            balls_lists = await page.query_selector_all('ul.balls')

            for ul in balls_lists:
                # Get game name from nearby elements
                game_name = await ul.evaluate('''el => {
                    let parent = el.parentElement;
                    for (let j = 0; j < 3 && parent; j++) {
                        let sibling = parent.previousElementSibling;
                        if (sibling) {
                            let text = sibling.textContent;
                            if (text && text.length < 100) return text.trim();
                        }
                        parent = parent.parentElement;
                    }
                    return "";
                }''')

                # Check if this is our game (case-insensitive match)
                if game.name.lower() in game_name.lower():
                    lis = await ul.query_selector_all('li')
                    numbers = []
                    for li in lis[:game.main_count + (game.bonus_count or 0)]:
                        text = await li.text_content()
                        if text:
                            text = text.strip()
                            if text.lstrip('-').isdigit():  # Handle negative numbers like -1
                                num = int(text)
                                if game.main_range_min <= num <= game.main_range_max:
                                    numbers.append(num)

                    if len(numbers) >= game.main_count:
                        main = numbers[:game.main_count]
                        bonus = numbers[game.main_count:] if game.bonus_count else []
                        logger.info(f"OH parsed {game.name}: main={main}, bonus={bonus}")
                        return main, bonus

            logger.warning(f"OH: Could not find {game.name} section")
            return [], []

        except Exception as e:
            logger.error(f"Error parsing OH numbers: {e}")
            return [], []

    async def _parse_draw_info(self, page: Page, selectors: dict) -> DrawInfo:
        return DrawInfo()

    async def get_draw_label(self, page: Page, game) -> Optional[str]:
        return None


@register_scraper('WA')
class WAScraper(BaseScraper):
    """
    Washington Lottery scraper.
    Numbers are in .game-balls ul li elements.
    """
    state = 'WA'

    async def _wait_for_content(self, page: Page, game) -> None:
        try:
            await page.wait_for_load_state('domcontentloaded', timeout=15000)
            await page.wait_for_timeout(3000)
        except Exception as e:
            logger.warning(f"Timeout waiting for WA content: {e}")

    async def parse_all_numbers(
        self,
        page: Page,
        game,
        target_draw_label: Optional[str] = None
    ) -> Tuple[List[int], List[int]]:
        try:
            # WA uses .game-balls ul li for numbers
            selectors = [
                '.game-balls ul li',
                '.game-balls li',
                'ul li',
            ]

            for selector in selectors:
                elements = await page.query_selector_all(selector)
                if elements:
                    numbers = []
                    for el in elements[:game.main_count + 5]:  # Extra buffer
                        text = await el.text_content()
                        if text:
                            text = text.strip()
                            if text.isdigit():
                                num = int(text)
                                if game.main_range_min <= num <= game.main_range_max:
                                    numbers.append(num)
                                    if len(numbers) >= game.main_count:
                                        break

                    if len(numbers) >= game.main_count:
                        main = numbers[:game.main_count]
                        logger.info(f"WA parsed: {main}")
                        return main, []

            logger.warning("WA: Could not find valid numbers")
            return [], []

        except Exception as e:
            logger.error(f"Error parsing WA numbers: {e}")
            return [], []

    async def _parse_draw_info(self, page: Page, selectors: dict) -> DrawInfo:
        return DrawInfo()

    async def get_draw_label(self, page: Page, game) -> Optional[str]:
        return None


@register_scraper('MA')
class MAScraper(BaseScraper):
    """
    Massachusetts Lottery scraper.
    Numbers appear in Results By Day section.
    For games like Mass Cash: under Midday/Evening Drawing headings.
    For games like Megabucks: directly after "Results By Day".
    """
    state = 'MA'

    async def _wait_for_content(self, page: Page, game) -> None:
        try:
            await page.wait_for_load_state('networkidle', timeout=20000)
            await page.wait_for_timeout(5000)
            # Scroll to load Results By Day section
            await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            await page.wait_for_timeout(2000)
        except Exception as e:
            logger.warning(f"Timeout waiting for MA content: {e}")

    async def parse_all_numbers(
        self,
        page: Page,
        game,
        target_draw_label: Optional[str] = None
    ) -> Tuple[List[int], List[int]]:
        try:
            text = await page.inner_text('body')
            lines = [l.strip() for l in text.split('\n') if l.strip()]

            numbers = []
            found_results = False
            found_drawing = False

            for line in lines:
                line_lower = line.lower()

                # For games with Midday/Evening Drawing (Mass Cash, etc.)
                if 'evening drawing' in line_lower or 'midday drawing' in line_lower:
                    found_drawing = True
                    numbers = []  # Reset for this drawing
                    continue

                # For games without Midday/Evening (Megabucks, etc.)
                if 'results by day' in line_lower:
                    found_results = True
                    continue

                # Collecting numbers
                if found_drawing or found_results:
                    if line.isdigit():
                        num = int(line)
                        if game.main_range_min <= num <= game.main_range_max:
                            numbers.append(num)
                            if len(numbers) >= game.main_count:
                                break
                    elif numbers and not line.isdigit():
                        # Non-number found after collecting numbers
                        if len(numbers) >= game.main_count:
                            break

            if len(numbers) >= game.main_count:
                main = numbers[:game.main_count]
                logger.info(f"MA parsed: main={main}")
                return main, []

            logger.warning("MA: Could not find valid numbers")
            return [], []

        except Exception as e:
            logger.error(f"Error parsing MA numbers: {e}")
            return [], []

    async def _parse_draw_info(self, page: Page, selectors: dict) -> DrawInfo:
        return DrawInfo()

    async def get_draw_label(self, page: Page, game) -> Optional[str]:
        try:
            text = await page.inner_text('body')
            if 'evening drawing' in text.lower():
                return 'evening'
            elif 'midday drawing' in text.lower():
                return 'midday'
        except:
            pass
        return None


@register_scraper('NE')
class NEScraper(BaseScraper):
    """
    Nebraska Lottery scraper.
    NE displays numbers in a table format: Date | Numbers (comma-separated)
    """
    state = 'NE'

    async def _wait_for_content(self, page: Page, game) -> None:
        try:
            await page.wait_for_load_state('domcontentloaded', timeout=20000)
            await page.wait_for_timeout(3000)
        except Exception as e:
            logger.warning(f"Timeout waiting for NE content: {e}")

    async def parse_all_numbers(self, page: Page, game, target_draw_label: Optional[str] = None) -> Tuple[List[int], List[int]]:
        try:
            body = await page.query_selector('body')
            if not body:
                return [], []

            content = await body.inner_text()
            lines = content.split('\n')

            # Look for lines with date and comma-separated numbers like "01/11/2026\t09, 15, 16, 18, 22"
            for line in lines:
                line = line.strip()
                # Check if line has date pattern (MM/DD/YYYY) and numbers
                if re.match(r'\d{2}/\d{2}/\d{4}', line) and ',' in line:
                    # Split by tab
                    parts = line.split('\t')
                    if len(parts) >= 2:
                        # Numbers are after the date
                        nums_part = parts[1]
                        try:
                            nums_str = nums_part.split(',')
                            numbers = [int(n.strip()) for n in nums_str]
                            if (len(numbers) == game.main_count and
                                all(game.main_range_min <= n <= game.main_range_max for n in numbers)):
                                logger.info(f"NE parsed: {numbers}")
                                return numbers, []
                        except ValueError:
                            continue

            logger.warning("NE: Could not find valid numbers")
            return [], []
        except Exception as e:
            logger.error(f"Error parsing NE numbers: {e}")
            return [], []

    async def _parse_draw_info(self, page: Page, selectors: dict) -> DrawInfo:
        return DrawInfo()

    async def get_draw_label(self, page: Page, game) -> Optional[str]:
        return None


@register_scraper('NM')
class NMScraper(BaseScraper):
    """New Mexico Lottery scraper."""
    state = 'NM'

    async def _wait_for_content(self, page: Page, game) -> None:
        try:
            await page.wait_for_load_state('networkidle', timeout=20000)
            await page.wait_for_timeout(3000)
        except Exception as e:
            logger.warning(f"Timeout waiting for NM content: {e}")

    async def parse_all_numbers(self, page: Page, game, target_draw_label: Optional[str] = None) -> Tuple[List[int], List[int]]:
        try:
            for selector in ['.winning-numbers .ball', '.ball', '.number', '.results-number']:
                elements = await page.query_selector_all(selector)
                if elements:
                    numbers = []
                    for el in elements[:game.main_count]:
                        text = await el.text_content()
                        if text and text.strip().isdigit():
                            numbers.append(int(text.strip()))
                    if len(numbers) >= game.main_count:
                        logger.info(f"NM parsed: {numbers}")
                        return numbers[:game.main_count], []
            logger.warning("NM: Could not find valid numbers")
            return [], []
        except Exception as e:
            logger.error(f"Error parsing NM numbers: {e}")
            return [], []

    async def _parse_draw_info(self, page: Page, selectors: dict) -> DrawInfo:
        return DrawInfo()

    async def get_draw_label(self, page: Page, game) -> Optional[str]:
        return None


@register_scraper('RI')
class RIScraper(BaseScraper):
    """
    Rhode Island Lottery scraper.
    Numbers appear on separate lines after 'Winning Numbers:' heading.
    Extra Ball appears after main numbers.
    """
    state = 'RI'

    async def _wait_for_content(self, page: Page, game) -> None:
        try:
            await page.wait_for_load_state('domcontentloaded', timeout=20000)
            await page.wait_for_timeout(4000)
        except Exception as e:
            logger.warning(f"Timeout waiting for RI content: {e}")

    async def parse_all_numbers(self, page: Page, game, target_draw_label: Optional[str] = None) -> Tuple[List[int], List[int]]:
        try:
            body = await page.query_selector('body')
            if not body:
                return [], []

            content = await body.inner_text()
            lines = content.split('\n')

            # Find 'Winning Numbers:' section and collect numbers
            found_winning = False
            numbers = []
            bonus = []

            for line in lines:
                line_stripped = line.strip()
                if 'winning numbers:' in line_stripped.lower():
                    found_winning = True
                    continue

                if found_winning:
                    # Check if line is just a number (possibly with leading zeros)
                    if line_stripped.lstrip('0').isdigit() or line_stripped == '0':
                        if line_stripped.isdigit():
                            num = int(line_stripped)
                        else:
                            num = int(line_stripped.lstrip('0')) if line_stripped.lstrip('0') else 0
                        if game.main_range_min <= num <= game.main_range_max:
                            numbers.append(num)
                    elif 'extra ball' in line_stripped.lower():
                        # Next number is the bonus
                        continue
                    elif numbers and line_stripped.isdigit():
                        # This might be the extra ball
                        num = int(line_stripped)
                        bonus.append(num)
                        if len(numbers) >= game.main_count:
                            break
                    elif '/' in line_stripped and len(numbers) >= game.main_count:
                        # Date line - stop
                        break

            if len(numbers) >= game.main_count:
                main = numbers[:game.main_count]
                bonus_nums = bonus[:game.bonus_count] if game.bonus_count and bonus else []
                logger.info(f"RI parsed: main={main}, bonus={bonus_nums}")
                return main, bonus_nums

            logger.warning("RI: Could not find valid numbers")
            return [], []
        except Exception as e:
            logger.error(f"Error parsing RI numbers: {e}")
            return [], []

    async def _parse_draw_info(self, page: Page, selectors: dict) -> DrawInfo:
        return DrawInfo()

    async def get_draw_label(self, page: Page, game) -> Optional[str]:
        return None


@register_scraper('OR')
class ORScraper(BaseScraper):
    """
    Oregon Lottery scraper.
    Numbers appear on separate lines after 'Results' heading.
    """
    state = 'OR'

    async def _wait_for_content(self, page: Page, game) -> None:
        try:
            await page.wait_for_load_state('domcontentloaded', timeout=20000)
            await page.wait_for_timeout(4000)
        except Exception as e:
            logger.warning(f"Timeout waiting for OR content: {e}")

    async def parse_all_numbers(self, page: Page, game, target_draw_label: Optional[str] = None) -> Tuple[List[int], List[int]]:
        try:
            body = await page.query_selector('body')
            if not body:
                return [], []

            content = await body.inner_text()
            lines = content.split('\n')

            # Find 'Results' section and collect numbers
            found_results = False
            numbers = []

            for line in lines:
                line_stripped = line.strip()
                if 'results' in line_stripped.lower() and '/' in line_stripped:
                    # Found date with Results like "1/10/2026 Results"
                    found_results = True
                    continue

                if found_results:
                    if line_stripped.isdigit():
                        num = int(line_stripped)
                        if game.main_range_min <= num <= game.main_range_max:
                            numbers.append(num)
                            if len(numbers) >= game.main_count:
                                break
                    elif line_stripped and not line_stripped.isdigit() and numbers:
                        # Non-number after numbers - stop collecting
                        break

            if len(numbers) >= game.main_count:
                main = numbers[:game.main_count]
                logger.info(f"OR parsed: {main}")
                return main, []

            logger.warning("OR: Could not find valid numbers")
            return [], []
        except Exception as e:
            logger.error(f"Error parsing OR numbers: {e}")
            return [], []

    async def _parse_draw_info(self, page: Page, selectors: dict) -> DrawInfo:
        return DrawInfo()

    async def get_draw_label(self, page: Page, game) -> Optional[str]:
        return None


@register_scraper('PR')
class PRScraper(BaseScraper):
    """Puerto Rico Lottery scraper."""
    state = 'PR'

    async def _wait_for_content(self, page: Page, game) -> None:
        try:
            await page.wait_for_load_state('networkidle', timeout=20000)
            await page.wait_for_timeout(3000)
        except Exception as e:
            logger.warning(f"Timeout waiting for PR content: {e}")

    async def parse_all_numbers(self, page: Page, game, target_draw_label: Optional[str] = None) -> Tuple[List[int], List[int]]:
        try:
            # Parse page text to find numbers after "NÚMEROS GANADORES" section
            body = await page.query_selector('body')
            if not body:
                logger.warning("PR: No body element found")
                return [], []

            content = await body.inner_text()
            lines = content.split('\n')

            found_section = False
            main_numbers = []
            bonus_numbers = []

            for line in lines:
                line_stripped = line.strip()
                line_lower = line_stripped.lower()

                # Look for winning numbers section header
                if 'números' in line_lower and 'ganadores' in line_lower:
                    found_section = True
                    continue

                if not found_section:
                    continue

                # Stop at multiplier (x2, x3, etc.) or next section
                if line_stripped.lower().startswith('x') and line_stripped[1:].isdigit():
                    break
                if 'próximo jackpot' in line_lower or 'jackpot' in line_lower:
                    break

                # Parse numbers - they appear as 2-digit strings (01, 02, etc.)
                if line_stripped.isdigit():
                    num = int(line_stripped)
                    if len(main_numbers) < game.main_count:
                        if game.main_range_min <= num <= game.main_range_max:
                            main_numbers.append(num)
                    elif game.bonus_count and len(bonus_numbers) < game.bonus_count:
                        if game.bonus_range_min <= num <= game.bonus_range_max:
                            bonus_numbers.append(num)

                # Stop when we have all numbers
                if len(main_numbers) == game.main_count:
                    if not game.bonus_count or len(bonus_numbers) == game.bonus_count:
                        break

            if len(main_numbers) == game.main_count:
                logger.info(f"PR parsed: main={main_numbers}, bonus={bonus_numbers}")
                return main_numbers, bonus_numbers

            logger.warning(f"PR: Found only {len(main_numbers)} main numbers")
            return [], []
        except Exception as e:
            logger.error(f"Error parsing PR numbers: {e}")
            return [], []

    async def _parse_draw_info(self, page: Page, selectors: dict) -> DrawInfo:
        return DrawInfo()

    async def get_draw_label(self, page: Page, game) -> Optional[str]:
        return None


@register_scraper('TN')
class TNScraper(BaseScraper):
    """Tennessee Lottery scraper."""
    state = 'TN'

    async def _wait_for_content(self, page: Page, game) -> None:
        try:
            await page.wait_for_load_state('networkidle', timeout=20000)
            await page.wait_for_timeout(3000)
        except Exception as e:
            logger.warning(f"Timeout waiting for TN content: {e}")

    async def parse_all_numbers(self, page: Page, game, target_draw_label: Optional[str] = None) -> Tuple[List[int], List[int]]:
        try:
            for selector in ['.winning-numbers .ball', '.ball', '.number', '.cash-number']:
                elements = await page.query_selector_all(selector)
                if elements:
                    numbers = []
                    for el in elements[:game.main_count + (game.bonus_count or 0)]:
                        text = await el.text_content()
                        if text and text.strip().isdigit():
                            numbers.append(int(text.strip()))
                    if len(numbers) >= game.main_count:
                        main = numbers[:game.main_count]
                        bonus = numbers[game.main_count:] if game.bonus_count else []
                        logger.info(f"TN parsed: main={main}, bonus={bonus}")
                        return main, bonus
            logger.warning("TN: Could not find valid numbers")
            return [], []
        except Exception as e:
            logger.error(f"Error parsing TN numbers: {e}")
            return [], []

    async def _parse_draw_info(self, page: Page, selectors: dict) -> DrawInfo:
        return DrawInfo()

    async def get_draw_label(self, page: Page, game) -> Optional[str]:
        return None


@register_scraper('WV')
class WVScraper(BaseScraper):
    """
    West Virginia Lottery scraper.
    WV displays numbers after 'Last Draw' section, each number on its own line.
    """
    state = 'WV'

    async def _wait_for_content(self, page: Page, game) -> None:
        try:
            await page.wait_for_load_state('domcontentloaded', timeout=20000)
            await page.wait_for_timeout(4000)
        except Exception as e:
            logger.warning(f"Timeout waiting for WV content: {e}")

    async def parse_all_numbers(self, page: Page, game, target_draw_label: Optional[str] = None) -> Tuple[List[int], List[int]]:
        try:
            body = await page.query_selector('body')
            if not body:
                return [], []

            content = await body.inner_text()
            lines = content.split('\n')

            # Find 'Last Draw' section and collect numbers
            found_last_draw = False
            numbers = []

            for line in lines:
                line_stripped = line.strip()
                if 'Last Draw' in line_stripped:
                    found_last_draw = True
                    continue

                if found_last_draw:
                    # Numbers appear on their own lines
                    if line_stripped.isdigit():
                        num = int(line_stripped)
                        if game.main_range_min <= num <= game.main_range_max:
                            numbers.append(num)
                            if len(numbers) >= game.main_count:
                                break
                    elif 'Check Numbers' in line_stripped or 'Past Draws' in line_stripped:
                        break

            if len(numbers) >= game.main_count:
                main = numbers[:game.main_count]
                logger.info(f"WV parsed: {main}")
                return main, []

            logger.warning("WV: Could not find valid numbers")
            return [], []
        except Exception as e:
            logger.error(f"Error parsing WV numbers: {e}")
            return [], []

    async def _parse_draw_info(self, page: Page, selectors: dict) -> DrawInfo:
        return DrawInfo()

    async def get_draw_label(self, page: Page, game) -> Optional[str]:
        return None


@register_scraper('ME')
class MEScraper(BaseScraper):
    """Maine / Tri-State Lottery scraper."""
    state = 'ME'

    async def _wait_for_content(self, page: Page, game) -> None:
        try:
            await page.wait_for_load_state('networkidle', timeout=20000)
            await page.wait_for_timeout(3000)
        except Exception as e:
            logger.warning(f"Timeout waiting for ME content: {e}")

    async def parse_all_numbers(self, page: Page, game, target_draw_label: Optional[str] = None) -> Tuple[List[int], List[int]]:
        try:
            # Parse page text to find numbers after "Winning Numbers" section
            body = await page.query_selector('body')
            if not body:
                logger.warning("ME: No body element found")
                return [], []

            content = await body.inner_text()
            lines = content.split('\n')

            found_section = False
            main_numbers = []
            bonus_numbers = []

            for line in lines:
                line_stripped = line.strip()
                line_lower = line_stripped.lower()

                # Look for "Winning Numbers" with date
                if 'winning numbers' in line_lower:
                    found_section = True
                    continue

                if not found_section:
                    continue

                # Stop at jackpot or other sections
                if 'jackpot' in line_lower or 'tri-state' in line_lower:
                    break

                # Parse numbers - they appear as digits on their own line
                if line_stripped.isdigit():
                    num = int(line_stripped)
                    if len(main_numbers) < game.main_count:
                        if game.main_range_min <= num <= game.main_range_max:
                            main_numbers.append(num)
                    elif game.bonus_count and len(bonus_numbers) < game.bonus_count:
                        if game.bonus_range_min <= num <= game.bonus_range_max:
                            bonus_numbers.append(num)

                # Stop when we have all numbers
                if len(main_numbers) == game.main_count:
                    if not game.bonus_count or len(bonus_numbers) == game.bonus_count:
                        break

            if len(main_numbers) == game.main_count:
                logger.info(f"ME parsed: main={main_numbers}, bonus={bonus_numbers}")
                return main_numbers, bonus_numbers

            logger.warning(f"ME: Found only {len(main_numbers)} main numbers")
            return [], []
        except Exception as e:
            logger.error(f"Error parsing ME numbers: {e}")
            return [], []

    async def _parse_draw_info(self, page: Page, selectors: dict) -> DrawInfo:
        return DrawInfo()

    async def get_draw_label(self, page: Page, game) -> Optional[str]:
        return None


@register_scraper('ID')
class IDScraper(BaseScraper):
    """Idaho Lottery scraper - handles multiple page structures."""
    state = 'ID'

    async def _wait_for_content(self, page: Page, game) -> None:
        try:
            await page.wait_for_load_state('networkidle', timeout=15000)
            await page.wait_for_timeout(2000)
        except Exception as e:
            logger.warning(f"Timeout waiting for ID content: {e}")

    async def parse_all_numbers(self, page: Page, game, target_draw_label: Optional[str] = None) -> Tuple[List[int], List[int]]:
        try:
            # Try multiple selector patterns
            selector_patterns = [
                '.gamepage--winningnumbers li',
                '.winning-numbers li',
                '.ball',
                'ul li',
            ]

            for selector in selector_patterns:
                elements = await page.query_selector_all(selector)
                if not elements:
                    continue

                numbers = []
                for el in elements:
                    text = await el.text_content()
                    if text:
                        text = text.strip().lstrip('*').strip()
                        if text.isdigit():
                            num = int(text)
                            max_val = game.bonus_range_max if game.bonus_count and game.bonus_range_max else game.main_range_max
                            if game.main_range_min <= num <= max_val:
                                numbers.append(num)

                    expected = game.main_count + (game.bonus_count or 0)
                    if len(numbers) >= expected:
                        break

                if len(numbers) >= game.main_count:
                    main = numbers[:game.main_count]
                    bonus = numbers[game.main_count:game.main_count + (game.bonus_count or 0)] if game.bonus_count else []
                    logger.info(f"ID parsed with {selector}: main={main}, bonus={bonus}")
                    return main, bonus

            logger.warning("ID: Could not find valid numbers")
            return [], []
        except Exception as e:
            logger.error(f"Error parsing ID numbers: {e}")
            return [], []

    async def _parse_draw_info(self, page: Page, selectors: dict) -> DrawInfo:
        return DrawInfo()

    async def get_draw_label(self, page: Page, game) -> Optional[str]:
        return None
