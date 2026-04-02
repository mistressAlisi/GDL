import asyncio
import logging

from django.core.management.base import BaseCommand

from dataengine.drivers.apitennis.driver.daemons.apitennisasyncdaemon import APITennisAsyncDaemon
from parameters.models import VHost



class Command(BaseCommand):
    help = 'APITennis: Start the Async Updater Daemon'
    def add_arguments(self, parser):
        # Named (optional) arguments
        parser.add_argument("vhost",type=str,nargs="+")
        parser.add_argument("-l", type=str, nargs="+")
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Getting Fixtures!'))
        vHost = VHost.objects.get(pk=options["vhost"][0])
        if options["l"]:
            if options["l"][0] == "INFO":
                logging.basicConfig(level=logging.INFO,force=True)
            elif options["l"][0] == "DEBUG":
                logging.basicConfig(level=logging.DEBUG,force=True)
            elif options["l"][0] == "WARNING":
                logging.basicConfig(level=logging.WARNING,force=True)
            elif options["l"][0] == "ERROR":
                logging.basicConfig(level=logging.ERROR,force=True)
        apidaemon = APITennisAsyncDaemon(vhost=vHost, logger=logging.getLogger())
        asyncio.run(apidaemon.start())


