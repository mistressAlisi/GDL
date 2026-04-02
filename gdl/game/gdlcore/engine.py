import logging
from django.conf import settings
from django.utils import timezone

from .models import *
from .algos.core import GDLCore
from .tasks import gdl_algo_parallel_by_count

logger = logging.getLogger(__name__)

class GDLEngine(object):
    gdlcore = GDLCore()
    vhost = None
    domain = None
    sports = None
    teams = None
    cacheInxObj = False
    cacheObjs = False
    gdl_algo_defaults = {
        "min_payout":6000,
        "depth":7,
        "stake":6,
        "events_within":None,
        "sports_filters": []
    }
    def __init__(self, vhost, domain=None, sports=None, teams=None, defaults={}, **kwargs):
        self.vhost = vhost
        self.domain = domain
        self.gdl_algo_defaults.update(defaults)
        if sports:
            self.sports = sports
        if teams:
            self.teams = teams


    def get_gdl_tickets(self, count=32, gdl_settings=None,negative_limit=-150,juice=0.05):
        logger.debug(f"GDLEngine.get_gdl_tickets called with count={count}, gdl_settings={gdl_settings}")
        if not gdl_settings:
            gdl_settings = self.gdl_algo_defaults.copy()
        else:
            merged = self.gdl_algo_defaults.copy()
            merged.update(gdl_settings)
            gdl_settings = merged
        logger.debug(f"Merged gdl_settings: {gdl_settings}")

        # Build Cutoff filter:
        if settings.GDL_USE_GPU:
            logger.debug(f"Using GPU: GDL_USE_GPU={settings.GDL_USE_GPU}, GDL_USE_LOCAL_GPU={settings.GDL_USE_LOCAL_GPU}")
            if not settings.GDL_USE_LOCAL_GPU:
                logger.debug(f"Launching async task with params: min_payout={gdl_settings['min_payout']}, count={count}, depth={gdl_settings['depth']}, stake={gdl_settings['stake']}")
                res = gdl_algo_parallel_by_count.apply_async((gdl_settings["min_payout"], count, gdl_settings["depth"],
                                                 gdl_settings["stake"],negative_limit,juice,self.gdl_algo_defaults["events_within"],self.gdl_algo_defaults["sports_filters"],5,False),ignore_result=False)
                result = res.get()
                logger.debug(f"Async task returned {len(result)} tickets")
                return result
            else:
                # print("RS")
                res = gdl_algo_parallel_by_count(gdl_settings["min_payout"], count, gdl_settings["depth"],
                                                              gdl_settings["stake"], negative_limit, juice,self.gdl_algo_defaults["events_within"],self.gdl_algo_defaults["sports_filters"],5,False)
                # print(res)
                return res

        else:
            try:
                self.cacheInxObj = GDLTicketCacheIndex.objects.get(vhost=self.vhost, domain=self.domain, sports=self.sports, teams=self.teams, min_payout=gdl_settings["min_payout"], depth=gdl_settings["depth"], stake=gdl_settings["stake"])
                logger.debug(f"CacheIndex fetched: id={self.cacheInxObj.id}")
            except GDLTicketCacheIndex.DoesNotExist:
                self.cacheInxObj = GDLTicketCacheIndex(vhost=self.vhost, domain=self.domain,
                                                       min_payout=gdl_settings["min_payout"],
                                                       depth=gdl_settings["depth"], stake=gdl_settings["stake"])
                if self.sports:
                    self.cacheInxObj.sports.set(self.sports)
                if self.teams:
                    self.cacheInxObj.teams.set(self.teams)
                self.cacheInxObj.save()
                logger.debug(f"Created new CacheIndex id={self.cacheInxObj.id}")

            self.cacheInxObj.request_count += 1
            self.cacheInxObj.save()
            logger.debug(f"Incremented request_count to {self.cacheInxObj.request_count}")
            self.cacheObjs = GDLTicketCache.objects.filter(cache_index=self.cacheInxObj, expires__gte=timezone.now())

            result = []
            i = 0
            logger.debug(f"Starting ticket consumption loop, target count={count}")
            while (i < count):
                try:
                    result.append(self.cacheObjs[i].ticket_data)
                    logger.debug(f"Fetched ticket from cache at index {i}")
                    self.cacheObjs[i].delete()
                    i+=1
                except IndexError:
                    tc = count - i
                    logger.debug(f"Cache exhausted after {i} tickets; requesting {tc} more")
                    logger.debug(f"Calling gdl_algo_parallel_by_count for {tc} tickets")
                    res = gdl_algo_parallel_by_count(gdl_settings["min_payout"], tc, gdl_settings["depth"], gdl_settings["stake"])
                    res = res.get(timeout=50)
                    logger.debug(f"Algorithm returned {len(res)} tickets")
                    for r in res:
                        result.append(r)
                        i+=1
            logger.debug(f"Returning {len(result)} tickets to caller")
            return result
