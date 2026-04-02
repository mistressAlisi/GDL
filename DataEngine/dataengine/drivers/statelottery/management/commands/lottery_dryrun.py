import asyncio
import logging

from django.core.management.base import BaseCommand, CommandError

from dataengine.drivers.statelottery.models import LotteryGame
from dataengine.drivers.statelottery.scrapers import get_scraper_for_state
from dataengine.drivers.statelottery.driver.validator import (
    validate_scrape_result,
    validate_game_config
)


class Command(BaseCommand):
    help = 'Test scraping for a game without saving to database (dry run)'

    def add_arguments(self, parser):
        parser.add_argument(
            'game_slug',
            type=str,
            help='Slug of the game to test (e.g., ny-lotto)'
        )
        parser.add_argument(
            '--show-html',
            action='store_true',
            help='Display raw HTML (first 5000 chars)'
        )
        parser.add_argument(
            '--screenshot',
            type=str,
            help='Save screenshot to specified path'
        )

    def handle(self, *args, **options):
        game_slug = options['game_slug']
        show_html = options['show_html']
        screenshot_path = options.get('screenshot')

        logging.basicConfig(level=logging.INFO)

        # Get the game
        try:
            game = LotteryGame.objects.get(slug=game_slug)
        except LotteryGame.DoesNotExist:
            raise CommandError(f"Game '{game_slug}' not found")

        self.stdout.write("=" * 60)
        self.stdout.write(f"DRY RUN: {game.name}")
        self.stdout.write("=" * 60)
        self.stdout.write("")

        # Validate game config first
        self.stdout.write("Checking game configuration...")
        config_validation = validate_game_config(game)

        if not config_validation.valid:
            self.stdout.write(self.style.ERROR("Configuration errors:"))
            for error in config_validation.errors:
                self.stdout.write(f"  - {error}")
            return

        if config_validation.warnings:
            self.stdout.write(self.style.WARNING("Configuration warnings:"))
            for warning in config_validation.warnings:
                self.stdout.write(f"  - {warning}")

        self.stdout.write(self.style.SUCCESS("Configuration OK"))
        self.stdout.write("")

        # Show game details
        self.stdout.write("Game details:")
        self.stdout.write(f"  State: {game.state}")
        self.stdout.write(f"  Type: {game.game_type}")
        self.stdout.write(f"  URL: {game.url}")
        self.stdout.write(f"  Main numbers: {game.main_count} from {game.main_range}")
        if game.bonus_count > 0:
            self.stdout.write(f"  Bonus numbers: {game.bonus_count} from {game.bonus_range}")
        self.stdout.write(f"  Positional: {game.is_positional}")
        self.stdout.write("")

        # Show selectors
        self.stdout.write("Selectors:")
        for key, selector in game.selectors.items():
            self.stdout.write(f"  {key}: {selector}")
        self.stdout.write("")

        # Run the scrape
        self.stdout.write("Running scrape...")
        result = asyncio.run(self._scrape(game, screenshot_path))

        self.stdout.write("")
        self.stdout.write("-" * 60)
        self.stdout.write("RESULTS")
        self.stdout.write("-" * 60)
        self.stdout.write("")

        if result.success:
            self.stdout.write(self.style.SUCCESS("Scrape: SUCCESS"))
            self.stdout.write(f"Duration: {result.duration_ms}ms")
            self.stdout.write("")
            self.stdout.write(f"Main numbers: {result.main_numbers}")
            self.stdout.write(f"Bonus numbers: {result.bonus_numbers}")
            self.stdout.write(f"Draw date: {result.draw_date}")
            self.stdout.write(f"Draw number: {result.draw_number}")
            self.stdout.write(f"Draw label: {result.draw_label}")

            # Validate result
            self.stdout.write("")
            validation = validate_scrape_result(game, result)

            if validation.valid:
                self.stdout.write(self.style.SUCCESS("Validation: PASSED"))
            else:
                self.stdout.write(self.style.ERROR("Validation: FAILED"))
                for error in validation.errors:
                    self.stdout.write(f"  - {error}")

            if validation.warnings:
                self.stdout.write(self.style.WARNING("Warnings:"))
                for warning in validation.warnings:
                    self.stdout.write(f"  - {warning}")

        else:
            self.stdout.write(self.style.ERROR("Scrape: FAILED"))
            self.stdout.write(f"Error: {result.error_message}")
            self.stdout.write(f"Duration: {result.duration_ms}ms")

        # Show HTML if requested
        if show_html and result.raw_html:
            self.stdout.write("")
            self.stdout.write("-" * 60)
            self.stdout.write("RAW HTML (first 5000 chars)")
            self.stdout.write("-" * 60)
            self.stdout.write(result.raw_html[:5000])

        self.stdout.write("")
        self.stdout.write("=" * 60)
        self.stdout.write("DRY RUN COMPLETE (no data saved)")
        self.stdout.write("=" * 60)

    async def _scrape(self, game, screenshot_path=None):
        """Run the scraper."""
        scraper_cls = get_scraper_for_state(game.state)

        async with scraper_cls() as scraper:
            result = await scraper.scrape(game)

            # Take screenshot if requested
            if screenshot_path and scraper.browser:
                try:
                    page = await scraper.browser.new_page()
                    await page.goto(game.url, wait_until='networkidle')
                    await page.screenshot(path=screenshot_path)
                    await page.close()
                    self.stdout.write(f"Screenshot saved to: {screenshot_path}")
                except Exception as e:
                    self.stdout.write(f"Screenshot failed: {e}")

            return result
