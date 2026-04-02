
import logging
import time
from abc import ABC
from logging import getLogger
from threading import Thread
from multiprocessing import Process, Queue, Event
# Iterating-over-a-first-Obj type Worker thread base for Participants,Fixtures,Markets, etc.
import copy
import concurrent.futures



# Non-Iterating Worker thread base for most Data API Resources:
class KIBLWorkerThreadBase(Thread,ABC):
    vhost = False
    verbose = False
    api_hook = False
    api_hook_name = ""
    api = False
    logger = False
    kwargs = []
    def __init__(self, vhost, **kwargs):
        self.kwargs = copy.deepcopy(kwargs)
        # print(self.kwargs)
        if "verbose" in kwargs:
            self.verbose = kwargs["verbose"]
        for key in ["verbose", "api_hook", "api_hook_name", "api","league","participant","api","fixture"]:
            if key in kwargs:
                del kwargs[key]
        self.vhost = vhost
        if "api" in self.kwargs:
            self.api = self.kwargs["api"]
        else:
            from ...api.http import KiblHttpAPI
            self.api = KiblHttpAPI(self.vhost)
        self.api_hook = getattr(self.api, self.api_hook_name)
        Thread.__init__(self,**kwargs)
        self.logger = getLogger(f"dataengine.drivers.kiblio.daemons.kiblhttpd.{self.__class__.__name__}")
    def run(self):
        # self.logger.info(f"Starting Run for Thread of class {self.__class__.__name__}")
        #print(self.kwargs)
        if self.verbose:
            print(self.api_hook(**self.kwargs))
        else:
            self.api_hook(**self.kwargs)
# Setup the Httpd Data Setup Worker threads for later use:
KIBLIO_HTTPD_SETUP_THREAD_MAP = {
    "KIBLSportsWorkerThread":"fetch_sports",
    "KIBLRegionWorkerThread":"fetch_regions",
    "KIBLLeaguesWorkerThread":"fetch_leagues",
    "KIBLBetTypesWorkerThread":"fetch_betting_types",
    "KIBLMarketTypesWorkerThread":"fetch_market_types",
    "KIBLMarketStatusWorkerThread":"fetch_market_statuses",
    "KIBLSegmentWorkerThread":"fetch_segments",
    "KIBLSeasonsWorkerThread":"fetch_seasons",
    "KIBLStatesWorkerThread":"fetch_states",
    "KIBLSidesWorkerThread":"fetch_sides",
    "KIBLLocationsWorkerThread":"fetch_locations",
    "KIBLFixtureTypeWorkerThread":"fetch_fixture_types",
    "KIBLSportsbookWorkerThread":"fetch_sportsbooks",
}
KIBLIO_HTTPD_SETUP_THREADS = []
for class_name,function_name in KIBLIO_HTTPD_SETUP_THREAD_MAP.items():
    classInst = type(class_name, (KIBLWorkerThreadBase,),{'api_hook_name':function_name})
    # print(func,classInst)
    KIBLIO_HTTPD_SETUP_THREADS.append(classInst)




class KIBLIteratingWorkerThreadBase(KIBLWorkerThreadBase):
    iter_api_hook = False
    iter_api_hook_name = ""
    iter_obj_arg_name = ""
    kwargs = {}

    def __init__(self, vhost, **kwargs):
        self.kwargs = kwargs
        self.workers = kwargs.get("workers", 10)  # default max threads
        super().__init__(vhost=vhost, **kwargs)
        self.iter_api_hook = getattr(self.api, self.iter_api_hook_name)

    def run(self):
        self.logger.info(
            f"Starting Iterating Run for {self.__class__.__name__} with max {self.workers} workers"
        )
        iter_objs = self.iter_api_hook(**self.kwargs)

        # Dynamically build the worker class
        iter_class = type(
            f"{self.__class__.__name__}:worker",
            (KIBLWorkerThreadBase,),
            {"api_hook_name": self.api_hook_name},
        )

        def worker_task(iobj):
            local_kwargs = copy.deepcopy(self.kwargs)
            local_kwargs.update({self.iter_obj_arg_name: iobj})
            thread_worker = iter_class(self.vhost, **local_kwargs)
            thread_worker.start()
            thread_worker.join()
            return thread_worker

        results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.workers) as executor:
            future_to_obj = {
                executor.submit(worker_task, iobj): iobj for iobj in iter_objs
            }
            for future in concurrent.futures.as_completed(future_to_obj):
                iobj = future_to_obj[future]
                try:
                    results.append(future.result())
                except Exception as e:
                    self.logger.error(f"Error in worker for {iobj}: {e}")

        return results


# Setup HTTPD  data setup iterating worker:
classInst = type('KIBLLeagueParticipantsWorkerThread', (KIBLIteratingWorkerThreadBase,),{"iter_api_hook_name":"fetch_leagues_in_season","api_hook_name":"fetch_league_participants","iter_obj_arg_name":"league"})
KIBLIO_HTTPD_SETUP_THREADS.append(classInst)


# Setup the HTTPD Iterating Main Run() function Workers:
KIBLIO_ITERATING_HTTP_SETUP_THREAD_MAP = {
    "KIBLLeagueFixturesWorkerThread":{"iter_api_hook_name":"fetch_leagues_in_season","api_hook_name":"_fetch_league_fixtures","iter_obj_arg_name":"league"},
    "KIBLFixtureMarketWorkerThread":{"iter_api_hook_name":"fetch_leagues_in_season","api_hook_name":"fetch_fixture_markets","iter_obj_arg_name":"league"},
    "KIBLFixtureOutcomesWorkerThread":{"iter_api_hook_name":"fetch_leagues_in_season","api_hook_name":"fetch_fixture_outcomes","iter_obj_arg_name":"league"},
}
KIBLIO_ITERATING_HTTP_THREADS = []
for class_name,attr in KIBLIO_ITERATING_HTTP_SETUP_THREAD_MAP.items():
    classInst = type(class_name, (KIBLIteratingWorkerThreadBase,),attr)
    # print(func,classInst)
    KIBLIO_ITERATING_HTTP_THREADS.append(classInst)



# Upcoming

class KIBLHTTPd(Process):
    setup_threads = []
    data_threads = []

    def __init__(self, vhost, verbose=False, interval_between_runs=300, **kwargs):
        Process.__init__(self,**kwargs)
        self.vhost = vhost
        self.verbose = verbose
        self.vhost = vhost
        self.verbose = verbose
        self.interval_between_runs = interval_between_runs
        from ...api.http import KiblHttpAPI
        self.api = KiblHttpAPI(self.vhost)
        self.api.get_token()
        self.logger = logging.getLogger(f"dataengine.drivers.kiblio.daemons.{self.__class__.__name__}")
        # exit signal for clean shutdown
        self._stop_event = Event()

    def stop(self):
        """Signal the process to stop on next loop."""
        self._stop_event.set()




    def data_setup_run(self):
        self.logger.info(f"Starting Data Setup Run for Process of class {self.__class__.__name__}")
        for thread in KIBLIO_HTTPD_SETUP_THREADS:
            threadInst = thread(self.vhost,verbose=self.verbose,api=self.api)
            self.setup_threads.append(threadInst)
            threadInst.start()

        root_thread = self.setup_threads[0]
        root_thread.join()

    def data_run(self):
        self.data_threads = []
        self.logger.info(f"Starting Run for Process of class {self.__class__.__name__}")
        for thread in KIBLIO_ITERATING_HTTP_THREADS:
            threadinst = thread(self.vhost,verbose=self.verbose,api=self.api)
            threadinst.start()
            self.data_threads.append(threadinst)
        root_thread = self.data_threads[0]
        root_thread.join()

    def run(self):
        self.data_setup_run()
        while not self._stop_event.is_set():
            try:
                self.logger.info("Updating KIBL Data....")
                self.data_run()
            except Exception as e:
                    self.logger.exception(f"Update Data run failed: {e}")
            self.logger.info("Data Run Success.")
            self.logger.info(f"Data Run Complete, sleeping for {self.interval_between_runs} seconds")
            time.sleep(self.interval_between_runs)
