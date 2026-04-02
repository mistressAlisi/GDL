import logging

from django.core.management.base import BaseCommand

from dataengine.drivers.apitennis.driver.daemons.apitennishttpd import APITennisHTTPd
from parameters.models import VHost

from dataengine.drivers.apisports.driver.daemons.apisporthttpd import APISportsHTTPd

class Command(BaseCommand):
    help = 'APITennis: Get All Fixtures'
    def add_arguments(self, parser):
        # Named (optional) arguments
        parser.add_argument("vhost",type=str,nargs="+")
        parser.add_argument("-l", type=str, nargs="+")
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Getting Livescores!'))
        vHost = VHost.objects.get(pk=options["vhost"][0])
        if options["l"]:
            if options["l"][0] == "INFO":
                logging.basicConfig(level=logging.INFO)
            elif options["l"][0] == "DEBUG":
                logging.basicConfig(level=logging.DEBUG)
            elif options["l"][0] == "WARNING":
                logging.basicConfig(level=logging.WARNING)
            elif options["l"][0] == "ERROR":
                logging.basicConfig(level=logging.ERROR)
        apidaemon = APITennisHTTPd(vhost=vHost)
        apidaemon.get_livescores()
        self.stdout.write(self.style.SUCCESS('Completed getting Livescores!'))

