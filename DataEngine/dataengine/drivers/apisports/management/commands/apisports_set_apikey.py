import json
import logging
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from multiprocessing import cpu_count

from django.core.management import BaseCommand
from django.utils.timezone import now

from dataengine.drivers.kiblio.api.http import KiblHttpAPI
from dataengine.drivers.kiblio.models import Fixture
from dataengine.engine import DataEngine
from dataengine.models import DataEngineVHostConfig, MatchSyncStatus
from matches.models import Match
from parameters.models import VHost, VHostParameterRegistry


class Command(BaseCommand):
    help = "Set APISports API key for Driver."

    def add_arguments(self, parser):
        parser.add_argument("vhost", type=str, nargs="+")
        parser.add_argument("api_key", type=str, nargs="+")

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Setting APISports API key!'))
        vHost = VHost.objects.get(pk=options["vhost"][0])
        regappid = "dataengine.drivers.apisports"
        apiSettings,_ = VHostParameterRegistry.objects.get_or_create(vhost=vHost, application=regappid,name="api_key_str")
        apiSettings.value_text = options["api_key"][0]
        apiSettings.save()
