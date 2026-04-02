import logging
from django.core.management import BaseCommand
from parameters.models import VHost
from dataengine.drivers.collectapi.driver import CollectAPIDriver


class Command(BaseCommand):
    help = 'Sync lottery results from CollectAPI'
    
    def add_arguments(self, parser):
        parser.add_argument('vhost', type=str, help='VHost UUID')
        parser.add_argument(
            '--lottery',
            type=str,
            choices=['powerball', 'megamillions', 'all'],
            default='all',
            help='Which lottery to sync (default: all)'
        )
        parser.add_argument(
            '-l', '--log-level',
            type=str,
            choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
            default='INFO',
            help='Logging level'
        )
    
    def handle(self, *args, **options):
        # Setup logging
        log_level = getattr(logging, options['log_level'])
        logging.basicConfig(level=log_level)
        logger = logging.getLogger(__name__)
        
        try:
            vhost = VHost.objects.get(pk=options['vhost'])
        except VHost.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f"VHost {options['vhost']} not found")
            )
            return
        
        self.stdout.write(
            self.style.MIGRATE_HEADING(
                f"Syncing lottery results for VHost: {vhost}"
            )
        )
        
        # Initialize driver
        driver = CollectAPIDriver(vhost, logger)
        
        # Perform sync based on option
        lottery_option = options['lottery'].lower()
        
        if lottery_option == 'all':
            self.stdout.write("Syncing all lotteries...")
            results = driver.sync_all()
            
            for lottery, success in results.items():
                if success:
                    self.stdout.write(
                        self.style.SUCCESS(f"✓ {lottery} synced successfully")
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR(f"✗ {lottery} sync failed")
                    )
                    
        elif lottery_option == 'powerball':
            self.stdout.write("Syncing Powerball...")
            draw, match = driver.sync_powerball()
            if draw and match:
                self.stdout.write(
                    self.style.SUCCESS("✓ Powerball synced successfully")
                )
            else:
                self.stdout.write(
                    self.style.ERROR("✗ Powerball sync failed")
                )
                
        elif lottery_option == 'megamillions':
            self.stdout.write("Syncing Mega Millions...")
            draw, match = driver.sync_megamillions()
            if draw and match:
                self.stdout.write(
                    self.style.SUCCESS("✓ Mega Millions synced successfully")
                )
            else:
                self.stdout.write(
                    self.style.ERROR("✗ Mega Millions sync failed")
                )
        
        self.stdout.write(
            self.style.SUCCESS("\nSync operation complete")
        )

