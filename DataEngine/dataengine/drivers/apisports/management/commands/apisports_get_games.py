import logging

from django.core.management.base import BaseCommand

from dataengine.drivers.apisports.driver.daemon.httpd import APISportsHTTPd
from parameters.models import VHost


class Command(BaseCommand):
    help = 'ApiSports: All Supported Sports: Get the Games.'
    def add_arguments(self, parser):
        # Named (optional) arguments
        parser.add_argument("vhost",type=str,nargs="+")
        parser.add_argument("-l", type=str, nargs="+")
        parser.add_argument("--start", type=str, nargs="+")
        parser.add_argument("--stop", type=str, nargs="+")
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Getting Games!'))
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
        apidaemon = APISportsHTTPd(vHost)
        if not options["start"]:
            apidaemon.get_games()
        else:
            apidaemon.fetch_period_games(options["start"][0],options["stop"][0])
        self.stdout.write(self.style.SUCCESS('Completed getting Games!'))

