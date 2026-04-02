import logging
import time
from datetime import datetime, timedelta
from multiprocessing import Process, Event
from django.utils.timezone import now
from django.conf import settings

from dataengine.drivers.collectapi.driver.sync import CollectAPIDriver
from dataengine.drivers.collectapi.operations import (
    sync_lottery_draws,
    qualify_lottery_draw,
    create_upcoming_lottery_matches
)
from parameters.models import VHost, VHostParameterRegistry


class CollectAPIHTTPd(Process):
    """
    Daemon process for continuously syncing lottery data from CollectAPI.
    Similar to APITennisHTTPd but for lottery operations.
    """
    
    def __init__(self, vhost=None, verbose=False, interval_between_runs=3600, 
                 enable_multi_vhost=False, **kwargs):
        Process.__init__(self, **kwargs)
        self.vhost = vhost
        self.verbose = verbose
        self.interval_between_runs = interval_between_runs
        self.enable_multi_vhost = enable_multi_vhost
        self.logger = logging.getLogger(f"dataengine.drivers.collectapi.daemons.{self.__class__.__name__}")
        
        # Exit signal for clean shutdown
        self._stop_event = Event()
        
        # Track last time we created upcoming matches (once per day)
        self.last_match_creation = None
        self.match_creation_interval = 86400  # 24 hours in seconds
        
    def stop(self):
        """Signal the process to stop on next loop."""
        self._stop_event.set()
        
    def get_sync_interval(self):
        """Get sync interval from database or use default."""
        if self.vhost:
            try:
                interval_param = VHostParameterRegistry.objects.get(
                    vhost=self.vhost,
                    application="dataengine.drivers.collectapi",
                    name="sync_interval"
                )
                return int(interval_param.value_text)
            except (VHostParameterRegistry.DoesNotExist, ValueError):
                pass
        return self.interval_between_runs
        
    def sync_single_vhost(self, vhost):
        """Sync lottery data for a single VHost."""
        try:
            self.logger.info(f"Syncing lottery data for VHost: {vhost}")
            
            # Initialize driver
            driver = CollectAPIDriver(vhost, self.logger)
            
            # Perform sync
            sync_start = now()
            results = driver.sync_all()
            
            # Log results
            for lottery, result in results.items():
                if result:
                    self.logger.info(f"✓ {lottery} synced successfully for {vhost}")
                    
                    # Check if we need to qualify
                    # The result is a tuple (draw, match) from sync operations
                    if isinstance(result, tuple) and len(result) == 2:
                        draw, match = result
                        if match and match.finished:
                            self.logger.info(f"Qualifying lottery draw for match {match.id}")
                            qualify_lottery_draw(str(match.uuid))
                else:
                    self.logger.error(f"✗ {lottery} sync failed for {vhost}")
                    
            sync_duration = (now() - sync_start).total_seconds()
            self.logger.info(f"VHost {vhost} sync completed in {sync_duration:.2f} seconds")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error syncing VHost {vhost}: {e}", exc_info=True)
            return False
            
    def sync_all_vhosts(self):
        """Sync lottery data for all active VHosts."""
        if self.enable_multi_vhost:
            vhosts = VHost.objects.filter(active=True)
            self.logger.info(f"Syncing {vhosts.count()} active VHosts")
            
            success_count = 0
            for vhost in vhosts:
                if self.sync_single_vhost(vhost):
                    success_count += 1
                    
            self.logger.info(f"Multi-VHost sync completed: {success_count}/{vhosts.count()} successful")
            
        elif self.vhost:
            self.sync_single_vhost(self.vhost)
        else:
            self.logger.warning("No VHost specified and multi-VHost mode disabled")
            
    def check_and_create_upcoming_matches(self):
        """Check if we need to create upcoming lottery matches."""
        current_time = now()
        
        # Check if it's time to create upcoming matches
        if self.last_match_creation is None or \
           (current_time - self.last_match_creation).total_seconds() > self.match_creation_interval:
            
            self.logger.info("Creating upcoming lottery matches...")
            
            try:
                results = create_upcoming_lottery_matches()
                
                if results.get("created_matches"):
                    for match_info in results["created_matches"]:
                        self.logger.info(f"Created match: {match_info}")
                        
                if results.get("errors"):
                    for error in results["errors"]:
                        self.logger.error(f"Match creation error: {error}")
                        
                self.last_match_creation = current_time
                self.logger.info(f"Next match creation scheduled for {current_time + timedelta(seconds=self.match_creation_interval)}")
                
            except Exception as e:
                self.logger.error(f"Failed to create upcoming matches: {e}", exc_info=True)
                
    def run(self):
        """Main daemon loop."""
        try:
            self.logger.info(f"{self.__class__.__name__} starting...")
            
            # Get sync interval
            sync_interval = self.get_sync_interval()
            self.logger.info(f"Using sync interval: {sync_interval} seconds")
            
            while not self._stop_event.is_set():
                try:
                    sync_start = now()
                    self.logger.info(f"Starting sync cycle at {sync_start}")
                    
                    # Main sync operation
                    self.sync_all_vhosts()
                    
                    # Check if we need to create upcoming matches
                    self.check_and_create_upcoming_matches()
                    
                    # Calculate next sync time
                    sync_duration = (now() - sync_start).total_seconds()
                    next_sync = sync_start + timedelta(seconds=sync_interval)
                    wait_time = max(0, (next_sync - now()).total_seconds())
                    
                    if wait_time > 0:
                        self.logger.info(
                            f"Sync cycle completed in {sync_duration:.2f}s. "
                            f"Next sync at {next_sync}. Waiting {wait_time:.0f}s..."
                        )
                        # Use wait instead of sleep for interruptible waiting
                        self._stop_event.wait(wait_time)
                    else:
                        self.logger.warning(
                            f"Sync cycle took {sync_duration:.2f}s, "
                            f"longer than interval {sync_interval}s. Starting next cycle immediately."
                        )
                        
                except KeyboardInterrupt:
                    self.logger.info("Received keyboard interrupt")
                    break
                    
                except Exception as e:
                    self.logger.exception(f"Error in daemon loop: {e}")
                    self.logger.info(f"Retrying in {sync_interval} seconds...")
                    self._stop_event.wait(sync_interval)
                    
        except Exception as e:
            self.logger.exception(f"Fatal error in {self.__class__.__name__}: {e}")
            
        finally:
            self.logger.info(f"{self.__class__.__name__} shutting down")
            
    def get_fixtures(self):
        """Compatibility method - syncs lottery draws."""
        if self.vhost:
            return sync_lottery_draws(str(self.vhost.uuid))
        else:
            return sync_lottery_draws()
            
    def get_livescores(self):
        """
        Compatibility method - for lottery there's no live scores,
        but we can check for recently finished draws.
        """
        self.logger.info("Checking for recently finished lottery draws...")
        return self.get_fixtures()