import logging
from django.core.management.base import BaseCommand
from dataengine.drivers.collectapi.driver.daemons.collectapihttpd import CollectAPIHTTPd
from parameters.models import VHost


class Command(BaseCommand):
    help = 'CollectAPI: Start the Lottery Updater Daemon'
    
    def add_arguments(self, parser):
        parser.add_argument('vhost', type=str, nargs='?', help='VHost UUID (optional for multi-vhost mode)')
        parser.add_argument(
            '--multi-vhost',
            action='store_true',
            help='Enable multi-VHost mode to sync all active VHosts'
        )
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
        
        # Get VHost if specified
        vhost = None
        if options['vhost']:
            try:
                vhost = VHost.objects.get(pk=options['vhost'])
                self.stdout.write(
                    self.style.SUCCESS(f'Starting daemon for VHost: {vhost}')
                )
            except VHost.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f"VHost {options['vhost']} not found")
                )
                return
        elif not options['multi_vhost']:
            # If no VHost specified and not in multi-vhost mode, use first active
            vhost = VHost.objects.filter(active=True).first()
            if not vhost:
                self.stdout.write(
                    self.style.ERROR("No active VHost found. Specify a VHost or use --multi-vhost")
                )
                return
            self.stdout.write(
                self.style.WARNING(f'No VHost specified, using: {vhost}')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('Starting daemon in multi-VHost mode')
            )
            
        # Create and start daemon
        daemon = CollectAPIHTTPd(
            vhost=vhost,
            interval_between_runs=options['interval'],
            enable_multi_vhost=options['multi_vhost']
        )
        
        self.stdout.write(
            self.style.SUCCESS(
                f"CollectAPI daemon starting. Syncing every {options['interval']} seconds..."
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