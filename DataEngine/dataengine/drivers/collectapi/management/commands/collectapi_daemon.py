import logging
from django.core.management import BaseCommand
from dataengine.drivers.collectapi.driver.daemons.collectapihttpd import CollectAPIHTTPd
from parameters.models import VHost


class Command(BaseCommand):
    help = 'Run CollectAPI daemon for continuous lottery updates (Process-based)'
    
    def add_arguments(self, parser):
        parser.add_argument('vhost', type=str, help='VHost UUID')
        parser.add_argument(
            '--interval',
            type=int,
            default=3600,
            help='Sync interval in seconds (default: 3600 = 1 hour)'
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
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        try:
            vhost = VHost.objects.get(pk=options['vhost'])
        except VHost.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f"VHost {options['vhost']} not found")
            )
            return
        
        self.stdout.write(
            self.style.MIGRATE_HEADING(
                f"Starting CollectAPI daemon for VHost: {vhost}"
            )
        )
        
        # Create and start the Process-based daemon
        daemon = CollectAPIHTTPd(
            vhost=vhost,
            interval_between_runs=options['interval']
        )
        
        self.stdout.write(
            self.style.SUCCESS(
                f"Daemon started. Syncing every {options['interval']} seconds..."
            )
        )
        
        try:
            daemon.run()
        except KeyboardInterrupt:
            self.stdout.write(
                self.style.WARNING("\nDaemon stopped by user")
            )
            daemon.stop()
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Daemon error: {e}")
            )
            raise
