from multiprocessing import Process, Event
import time
import logging
from dataengine.drivers.apisports.driver import american_football,basketball,baseball,football,hockey
class APISportsHTTPd(Process):
    def __init__(self, vhost, verbose=False, interval_between_runs=1200, **kwargs):
        Process.__init__(self,**kwargs)
        self.vhost = vhost
        self.verbose = verbose
        self.vhost = vhost
        self.verbose = verbose
        self.interval_between_runs = interval_between_runs
        self.sports_api = {
            "american_football":american_football.APISportsDriver(self.vhost),
            "basketball":basketball.APISportsDriver(self.vhost),
            "baseball":baseball.APISportsDriver(self.vhost),
            "football":football.APISportsDriver(self.vhost),
            "hockey":hockey.APISportsDriver(self.vhost),
        }
        self.logger = logging.getLogger(f"dataengine.drivers.apisport.daemons.{self.__class__.__name__}")
        # exit signal for clean shutdown
        self._stop_event = Event()

    def stop(self):
        """Signal the process to stop on next loop."""
        self._stop_event.set()

    def get_leagues(self):
        for k,v in self.sports_api.items():
            self.sports_api[k].get_leagues()


    def get_teams(self):
        for k,v in self.sports_api.items():
            self.sports_api[k].get_teams()

    def get_players(self):
        for k,v in self.sports_api.items():
            self.sports_api[k].get_players()

    def fetch_period_games(self,start,stop):
        results = []
        for k,v in self.sports_api.items():
            results.append(self.sports_api[k].get_games(date_start=start,date_stop=stop))
        return results

    def get_games(self):
        for k,v in self.sports_api.items():
            self.sports_api[k].get_games()

    def run(self):

        try:
            while not self._stop_event.is_set():
                try:
                    self.logger.info("Updating ApiSports Data....")
                    self.get_games()
                except Exception as e:
                    self.logger.exception(f"Update Data run failed: {e}")

                self.logger.info(f"Sleeping {self.interval_between_runs}s")
                self._stop_event.wait(self.interval_between_runs)

        except Exception as e:
            self.logger.exception(f"Fatal error in {self.__class__.__name__}: {e}")
        finally:
            self.logger.info(f"{self.__class__.__name__} shutting down")

