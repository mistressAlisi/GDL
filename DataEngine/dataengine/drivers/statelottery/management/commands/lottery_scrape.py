import asyncio
import logging

from django.core.management.base import BaseCommand, CommandError

from dataengine.drivers.statelottery.models import LotteryGame, LotteryDraw
from dataengine.drivers.statelottery.scrapers import get_scraper_for_state
from dataengine.drivers.statelottery.driver.validator import validate_scrape_result
from parameters.models import VHost


class Command(BaseCommand):
    help = 'Manually scrape lottery results for a specific game'

    def add_arguments(self, parser):
        parser.add_argument("vhost", type=str, nargs="+")
        parser.add_argument(
            'game_slug',
            type=str,
            help='Slug of the game to scrape (e.g., ny-lotto)'
        )
        parser.add_argument(
            '-s', '--save',
            action='store_true',
            help='Save results to database (default: just display)'
        )
        parser.add_argument(
            '-vv', '--verbose',
            action='store_true',
            help='Verbose output'
        )

    def handle(self, *args, **options):
        vHost = VHost.objects.get(pk=options["vhost"][0])
        game_slug = options['game_slug']
        save = options['save']
        verbose = options['verbose']

        # Set up logging
        if verbose:
            logging.basicConfig(level=logging.DEBUG)
        else:
            logging.basicConfig(level=logging.INFO)

        # Get the game
        try:
            game = LotteryGame.objects.get(slug=game_slug,vhost_id=vHost.uuid)
        except LotteryGame.DoesNotExist:
            raise CommandError(f"Game '{game_slug}' not found in Vhost '{vHost}'")

        self.stdout.write(f"Scraping: {game.name} ({game.state})")
        self.stdout.write(f"URL: {game.url}")
        self.stdout.write("")

        # Run the scrape
        result = asyncio.run(self._scrape(game))

        if result.success:
            self.stdout.write(self.style.SUCCESS("Scrape successful!"))
            self.stdout.write("")
            self.stdout.write(f"Main numbers: {result.main_numbers}")
            self.stdout.write(f"Bonus numbers: {result.bonus_numbers}")
            self.stdout.write(f"Draw date: {result.draw_date}")
            self.stdout.write(f"Draw number: {result.draw_number}")
            self.stdout.write(f"Draw label: {result.draw_label}")
            self.stdout.write(f"Duration: {result.duration_ms}ms")

            # Validate
            validation = validate_scrape_result(game, result)
            if validation.valid:
                self.stdout.write(self.style.SUCCESS("\nValidation: PASSED"))
            else:
                self.stdout.write(self.style.ERROR("\nValidation: FAILED"))
                for error in validation.errors:
                    self.stdout.write(f"  - {error}")

            if validation.warnings:
                self.stdout.write(self.style.WARNING("\nWarnings:"))
                for warning in validation.warnings:
                    self.stdout.write(f"  - {warning}")

            # Save if requested
            if save and validation.valid:
                draw = self._save_draw(game, result,vHost)
                self.stdout.write(self.style.SUCCESS(f"\nSaved as draw: {draw.uuid}"))

        else:
            self.stdout.write(self.style.ERROR("Scrape failed!"))
            self.stdout.write(f"Error: {result.error_message}")
            self.stdout.write(f"Duration: {result.duration_ms}ms")

    async def _scrape(self, game):
        """Run the scraper."""
        scraper_cls = get_scraper_for_state(game.state)

        async with scraper_cls() as scraper:
            return await scraper.scrape(game)

    def _save_draw(self, game, result,vHost):
        """Save the scrape result to database."""
        from django.utils import timezone

        draw_date = result.draw_date.date() if result.draw_date else timezone.now().date()

        draw, created = LotteryDraw.objects.update_or_create(
            vhost_id=vHost.uuid,
            game=game,
            draw_date=draw_date,
            draw_label=result.draw_label,
            defaults={
                'draw_datetime': result.draw_date,
                'draw_number': result.draw_number,
                'main_numbers': result.main_numbers,
                'bonus_numbers': result.bonus_numbers,
                'raw_response': result.raw_html[:50000] if result.raw_html else '',
                'scrape_success': True,
            }
        )
        draw.save()
        return draw
