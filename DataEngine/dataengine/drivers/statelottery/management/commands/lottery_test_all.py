import asyncio
import logging
from datetime import datetime

from django.core.management.base import BaseCommand

from parameters.models import VHost
from dataengine.drivers.statelottery.models import LotteryGame
from dataengine.drivers.statelottery.scrapers import get_scraper_for_state
from dataengine.drivers.statelottery.driver.validator import validate_scrape_result


class Command(BaseCommand):
    help = 'Test all scrapers without saving to database (dry run for all games)'

    def add_arguments(self, parser):
        parser.add_argument(
            'vhost',
            type=str,
            help='VHost UUID'
        )
        parser.add_argument(
            '--state',
            type=str,
            help='Filter by state code (e.g., NY, CA, MULTI)'
        )
        parser.add_argument(
            '--parallel',
            type=int,
            default=3,
            help='Number of concurrent scrapes (default: 3)'
        )
        parser.add_argument(
            '--timeout',
            type=int,
            default=60,
            help='Timeout per scrape in seconds (default: 60)'
        )

    def handle(self, *args, **options):
        vhost_uuid = options['vhost']
        state_filter = options.get('state')
        parallel = options['parallel']
        timeout = options['timeout']

        logging.basicConfig(level=logging.WARNING)

        # Get vhost
        try:
            vhost = VHost.objects.get(uuid=vhost_uuid)
        except VHost.DoesNotExist:
            self.stderr.write(f"VHost '{vhost_uuid}' not found")
            return

        # Get games
        games = LotteryGame.objects.filter(active=True, vhost_id=vhost.uuid)
        if state_filter:
            games = games.filter(state=state_filter.upper())

        games = list(games.order_by('state', 'name'))

        if not games:
            self.stderr.write("No active games found")
            return

        self.stdout.write("=" * 80)
        self.stdout.write(f"LOTTERY SCRAPER TEST - {len(games)} games")
        self.stdout.write(f"Parallel: {parallel}, Timeout: {timeout}s")
        self.stdout.write("=" * 80)
        self.stdout.write("")

        # Run tests
        results = asyncio.run(self._test_all(games, parallel, timeout))

        # Summary
        self.stdout.write("")
        self.stdout.write("=" * 80)
        self.stdout.write("SUMMARY")
        self.stdout.write("=" * 80)

        success = [r for r in results if r['status'] == 'SUCCESS']
        failed = [r for r in results if r['status'] == 'FAILED']
        errors = [r for r in results if r['status'] == 'ERROR']

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS(f"SUCCESS: {len(success)}"))
        self.stdout.write(self.style.WARNING(f"FAILED:  {len(failed)}"))
        self.stdout.write(self.style.ERROR(f"ERROR:   {len(errors)}"))
        self.stdout.write("")

        if success:
            self.stdout.write(self.style.SUCCESS("Successful scrapes:"))
            for r in success:
                self.stdout.write(f"  {r['state']:5} {r['name'][:30]:30} -> {r['numbers']}")

        if failed:
            self.stdout.write("")
            self.stdout.write(self.style.WARNING("Failed validations:"))
            for r in failed:
                self.stdout.write(f"  {r['state']:5} {r['name'][:30]:30} -> {r['error'][:50]}")

        if errors:
            self.stdout.write("")
            self.stdout.write(self.style.ERROR("Errors:"))
            for r in errors:
                self.stdout.write(f"  {r['state']:5} {r['name'][:30]:30} -> {r['error'][:50]}")

    async def _test_all(self, games, parallel, timeout):
        """Test all games with limited concurrency."""
        semaphore = asyncio.Semaphore(parallel)
        results = []
        scrapers = {}

        async def test_game(game):
            async with semaphore:
                result = await self._test_single(game, scrapers, timeout)
                results.append(result)

                # Print progress
                status_char = {
                    'SUCCESS': self.style.SUCCESS('✓'),
                    'FAILED': self.style.WARNING('✗'),
                    'ERROR': self.style.ERROR('!'),
                }[result['status']]

                detail = result.get('numbers') or (result.get('error') or '')[:50]
                self.stdout.write(
                    f"{status_char} {result['state']:5} {result['name'][:40]:40} {detail}"
                )

        # Run all tests
        await asyncio.gather(*[test_game(g) for g in games],return_exceptions=True)

        # Cleanup scrapers
        for scraper in scrapers.values():
            try:
                await scraper.stop()
            except Exception:
                pass

        return results

    async def _test_single(self, game, scrapers, timeout):
        """Test a single game."""
        result = {
            'state': game.state,
            'name': game.name,
            'slug': game.slug,
            'status': 'ERROR',
            'numbers': None,
            'error': None,
        }

        try:
            # Get or create scraper
            if game.state not in scrapers:
                scraper_cls = get_scraper_for_state(game.state)
                scraper = scraper_cls()
                await scraper.start()
                scrapers[game.state] = scraper

            scraper = scrapers[game.state]

            # Run scrape with timeout
            scrape_result = await asyncio.wait_for(
                scraper.scrape(game),
                timeout=timeout
            )

            if scrape_result.success:
                # Validate
                validation = validate_scrape_result(game, scrape_result)

                if validation.valid:
                    result['status'] = 'SUCCESS'
                    bonus = f" + {scrape_result.bonus_numbers}" if scrape_result.bonus_numbers else ""
                    result['numbers'] = f"{scrape_result.main_numbers}{bonus}"
                else:
                    result['status'] = 'FAILED'
                    result['error'] = "; ".join(validation.errors)
            else:
                result['status'] = 'ERROR'
                result['error'] = scrape_result.error_message

        except asyncio.TimeoutError:
            result['status'] = 'ERROR'
            result['error'] = f"Timeout after {timeout}s"
        except Exception as e:
            result['status'] = 'ERROR'
            result['error'] = str(e)[:100]

        return result
