import asyncio
import logging
from datetime import datetime, timedelta, time as dt_time
from types import SimpleNamespace
from typing import Dict, List, Optional, Tuple

from asgiref.sync import sync_to_async
from django.db import connections
from django.utils import timezone

from asynctools.abc import AsyncWorkerABC

logger = logging.getLogger(__name__)


class LotteryScrapeDaemon(AsyncWorkerABC):
    """
    Async daemon for scraping lottery results from state websites.

    Behavior:
    - Loads active games from database
    - Calculates next scrape time for each game (draw_time + 5 minutes)
    - Sleeps until next scheduled scrape
    - On failure, retries every 5 minutes for 15 minutes max (3 attempts)
    - Logs all attempts to LotteryScrapeLog
    """

    SCRAPE_DELAY_MINUTES = 5  # Wait this long after draw time
    RETRY_INTERVAL_MINUTES = 5
    MAX_RETRIES = 3

    def __init__(self, vhost=None, logger=None, name: str = "worker", interval: float = 120,
                 run_in_process: bool = True, loki_url=None):
        AsyncWorkerABC.__init__(self, vhost, logger, name, interval, run_in_process, loki_url)

        # State
        self._scrapers: Dict[str, object] = {}  # state -> scraper instance
        self._pending_retries: Dict[str, Tuple[datetime, int]] = {}  # game_slug -> (next_retry, retry_count)

    def _child_init(self):
        """
        Runs inside the forked child *after* django.setup().
        Safe place for model imports.
        """
        super()._child_init()

        from ..models import LotteryGame, LotteryDraw, LotteryScrapeLog
        from ..scrapers import get_scraper_for_state, ScrapeResult
        from ..driver.validator import validate_scrape_result

        self.models = SimpleNamespace(
            LotteryGame=LotteryGame,
            LotteryDraw=LotteryDraw,
            LotteryScrapeLog=LotteryScrapeLog,
        )
        self.get_scraper_for_state = get_scraper_for_state
        self.ScrapeResult = ScrapeResult
        self.validate_scrape_result = validate_scrape_result

    async def _work_cycle(self):
        """Main daemon loop."""
        while self._running and not self._exit:
            try:
                # Load active games
                games = await self._get_active_games()

                if not games:
                    self.logger.info("No active games found. Sleeping...")
                    await asyncio.sleep(self.interval)
                    continue

                # Check for games that need scraping
                now = timezone.now()
                games_to_scrape = []

                for game in games:
                    if self._should_scrape(game, now):
                        games_to_scrape.append(game)

                # Also check for retries
                for slug, (retry_time, retry_count) in list(self._pending_retries.items()):
                    if now >= retry_time:
                        game = await self._get_game_by_slug(slug)
                        if game and game not in games_to_scrape:
                            games_to_scrape.append(game)

                # Scrape games
                for game in games_to_scrape:
                    await self._scrape_game(game)

                # Close DB connections before sleeping
                await sync_to_async(lambda: connections.close_all(), thread_sensitive=False)()

                # Sleep until next check
                await asyncio.sleep(self.interval)

            except Exception as e:
                self.logger.exception(f"Error in daemon loop: {e}")
                await asyncio.sleep(self.interval)

    async def _cleanup(self):
        """Cleanup resources."""
        # Stop all scrapers
        for state, scraper in self._scrapers.items():
            try:
                await scraper.stop()
            except Exception as e:
                self.logger.warning(f"Error stopping {state} scraper: {e}")

        self._scrapers.clear()
        self.logger.info(f"{self.name} cleaned up")

    @sync_to_async
    def _get_active_games(self):
        """Get all active lottery games."""
        return list(self.models.LotteryGame.objects.filter(active=True, vhost_id=self.vhost.uuid))

    @sync_to_async
    def _get_game_by_slug(self, slug: str):
        """Get a game by its slug."""
        try:
            return self.models.LotteryGame.objects.get(slug=slug, vhost_id=self.vhost.uuid)
        except self.models.LotteryGame.DoesNotExist:
            return None

    def _should_scrape(self, game, now: datetime) -> bool:
        """
        Determine if a game should be scraped now based on its schedule.

        Returns True if:
        - Current time is past draw_time + SCRAPE_DELAY_MINUTES
        - We haven't already scraped for this draw
        """
        schedule = game.schedule
        if not schedule:
            return False

        # Get schedule details
        days = schedule.get('days', [])
        times = schedule.get('times', [])
        tz_name = schedule.get('timezone', 'UTC')

        # Get current day and time
        current_day = now.strftime('%A').lower()

        # Check if today is a draw day
        if days and current_day not in [d.lower() for d in days]:
            # Not "daily" and not a scheduled day
            if 'daily' not in [d.lower() for d in days]:
                return False

        # Check each draw time
        for time_config in times:
            draw_time_str = time_config.get('time')
            draw_label = time_config.get('label')

            if not draw_time_str:
                continue

            # Parse draw time
            try:
                hour, minute = map(int, draw_time_str.split(':'))
                draw_time = dt_time(hour, minute)
            except (ValueError, AttributeError):
                continue

            # Calculate scrape time (draw_time + delay)
            draw_datetime = now.replace(
                hour=draw_time.hour,
                minute=draw_time.minute,
                second=0,
                microsecond=0
            )
            scrape_time = draw_datetime + timedelta(minutes=self.SCRAPE_DELAY_MINUTES)

            # Check if we're past scrape time
            if now >= scrape_time:
                # Check if we already have this draw
                has_draw = self._check_existing_draw(
                    game,
                    now.date(),
                    draw_label
                )
                if not has_draw:
                    return True

        return False

    def _check_existing_draw(self, game, draw_date, draw_label: Optional[str]) -> bool:
        """Check if we already have a draw for this game/date/label."""
        try:
            filters = {
                'vhost_id': self.vhost.uuid,
                'game': game,
                'draw_date': draw_date,
                'scrape_success': True,
            }
            if draw_label:
                filters['draw_label'] = draw_label

            return self.models.LotteryDraw.objects.filter(**filters).exists()
        except Exception:
            return False

    async def _scrape_game(self, game) -> bool:
        """
        Scrape results for a single game.

        Returns True if successful, False otherwise.
        """
        start_time = timezone.now()
        retry_count = self._pending_retries.get(game.slug, (None, 0))[1]

        self.logger.info(f"Scraping {game.name} (attempt {retry_count + 1}/{self.MAX_RETRIES})")

        try:
            # Get or create scraper for this state
            scraper = await self._get_scraper(game.state)

            # Perform scrape
            result = await scraper.scrape(game)

            # Validate result
            validation = self.validate_scrape_result(game, result)

            if validation.valid:
                # Save the draw
                draw = await self._save_draw(game, result)

                # Log success
                await self._log_scrape(
                    game=game,
                    success=True,
                    retry_count=retry_count,
                    draw=draw,
                    duration_ms=result.duration_ms
                )

                # Clear retry state
                if game.slug in self._pending_retries:
                    del self._pending_retries[game.slug]

                self.logger.info(f"Successfully scraped {game.name}: {result.main_numbers}")
                return True

            else:
                # Validation failed
                error_msg = "; ".join(validation.errors)
                self.logger.warning(f"Validation failed for {game.name}: {error_msg}")

                await self._handle_failure(game, error_msg, retry_count, result.duration_ms)
                return False

        except Exception as e:
            error_msg = str(e)
            self.logger.error(f"Scrape error for {game.name}: {error_msg}")

            duration_ms = int((timezone.now() - start_time).total_seconds() * 1000)
            await self._handle_failure(game, error_msg, retry_count, duration_ms)
            return False

    async def _handle_failure(self, game, error_msg: str, retry_count: int, duration_ms: int):
        """Handle a scrape failure, scheduling retry if appropriate."""
        # Log the failure
        await self._log_scrape(
            game=game,
            success=False,
            error_message=error_msg,
            retry_count=retry_count,
            duration_ms=duration_ms
        )

        # Schedule retry if under max
        if retry_count < self.MAX_RETRIES - 1:
            next_retry = timezone.now() + timedelta(minutes=self.RETRY_INTERVAL_MINUTES)
            self._pending_retries[game.slug] = (next_retry, retry_count + 1)
            self.logger.info(
                f"Scheduling retry {retry_count + 2}/{self.MAX_RETRIES} "
                f"for {game.name} at {next_retry}"
            )
        else:
            # Max retries reached
            if game.slug in self._pending_retries:
                del self._pending_retries[game.slug]
            self.logger.error(
                f"Max retries reached for {game.name}. Giving up until next draw."
            )

    async def _get_scraper(self, state: str):
        """Get or create a scraper for a state."""
        if state not in self._scrapers:
            scraper_cls = self.get_scraper_for_state(state)
            scraper = scraper_cls()
            await scraper.start()
            self._scrapers[state] = scraper

        return self._scrapers[state]

    @sync_to_async
    def _save_draw(self, game, result):
        """Save a successful scrape result as a LotteryDraw."""
        draw_date = result.draw_date.date() if result.draw_date else timezone.now().date()

        draw, created = self.models.LotteryDraw.objects.update_or_create(
            vhost_id=self.vhost.uuid,
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

        return draw

    @sync_to_async
    def _log_scrape(self, game, success: bool, retry_count: int = 0,
                    error_message: str = '', draw=None, duration_ms: int = 0):
        """Log a scrape attempt."""
        return self.models.LotteryScrapeLog.objects.create(
            vhost_id=self.vhost.uuid,
            game=game,
            success=success,
            error_message=error_message,
            retry_count=retry_count,
            draw_found=draw,
            scrape_duration_ms=duration_ms,
        )
