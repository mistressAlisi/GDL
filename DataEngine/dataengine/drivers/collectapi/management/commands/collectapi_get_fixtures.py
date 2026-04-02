import logging
from django.core.management.base import BaseCommand
from dataengine.drivers.collectapi.driver.daemons.collectapihttpd import CollectAPIHTTPd
from parameters.models import VHost


class Command(BaseCommand):
    help = 'CollectAPI: Get All Lottery Fixtures (Draws)'
    
    def add_arguments(self, parser):
        parser.add_argument("vhost", type=str, help="VHost UUID")
        parser.add_argument(
            "-l", "--log-level",
            type=str,
            choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
            default='INFO',
            help='Logging level'
        )
        
    def handle(self, *args, **options):
        # Setup logging
        log_level = getattr(logging, options['log_level'])
        logging.basicConfig(level=log_level)
        
        self.stdout.write(self.style.SUCCESS('Getting Lottery Fixtures!'))
        
        try:
            vhost = VHost.objects.get(pk=options["vhost"])
        except VHost.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f"VHost {options['vhost']} not found")
            )
            return
            
        # Create daemon instance and get fixtures
        daemon = CollectAPIHTTPd(vhost=vhost)
        results = daemon.get_fixtures()
        
        if results:
            self.stdout.write(
                self.style.SUCCESS('Completed getting lottery fixtures!')
            )
            
            # Display results
            if 'powerball' in results:
                self.stdout.write(f"Powerball: {results['powerball']}")
            if 'megamillions' in results:
                self.stdout.write(f"Mega Millions: {results['megamillions']}")
        else:
            self.stdout.write(
                self.style.WARNING('No fixtures retrieved')
            )