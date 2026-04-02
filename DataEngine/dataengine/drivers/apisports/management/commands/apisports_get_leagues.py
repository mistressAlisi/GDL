import logging

from django.core.management.base import BaseCommand

from parameters.models import VHost

from dataengine.drivers.apisports.driver.daemons.apisporthttpd import APISportsHTTPd

class Command(BaseCommand):
    help = 'ApiSports: All Supported Sports: Get the Leagues.'
    def add_arguments(self, parser):
        # Named (optional) arguments
        parser.add_argument("vhost",type=str,nargs="+")
        parser.add_argument("-l", type=str, nargs="+")
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Getting Leagues!'))
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
        apidaemon.get_leagues()
        self.stdout.write(self.style.SUCCESS('Completed getting leagues!'))

