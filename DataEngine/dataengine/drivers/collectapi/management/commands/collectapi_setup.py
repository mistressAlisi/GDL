from django.core.management import BaseCommand
from parameters.models import VHost, VHostParameterRegistry
from dataengine.drivers.collectapi.driver import CollectAPIDriver


class Command(BaseCommand):
    help = 'Setup CollectAPI lottery types and configuration'
    
    def add_arguments(self, parser):
        parser.add_argument('vhost', type=str, help='VHost UUID')
        parser.add_argument(
            '--api-key',
            type=str,
            help='CollectAPI API key (will prompt if not provided)'
        )
    
    def handle(self, *args, **options):
        try:
            vhost = VHost.objects.get(pk=options['vhost'])
        except VHost.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f"VHost {options['vhost']} not found")
            )
            return
        
        self.stdout.write(
            self.style.MIGRATE_HEADING(
                f"Setting up CollectAPI for VHost: {vhost}"
            )
        )
        
        # Setup API key if provided
        if options['api_key']:
            param, created = VHostParameterRegistry.objects.update_or_create(
                vhost=vhost,
                application="dataengine.drivers.collectapi",
                name="api_key",
                defaults={
                    "value_text": options['api_key']
                }
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS("✓ API key configured")
                )
            else:
                self.stdout.write(
                    self.style.WARNING("✓ API key updated")
                )
        else:
            # Check if API key exists
            try:
                VHostParameterRegistry.objects.get(
                    vhost=vhost,
                    application="dataengine.drivers.collectapi",
                    name="api_key"
                )
                self.stdout.write(
                    self.style.SUCCESS("✓ API key already configured")
                )
            except VHostParameterRegistry.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(
                        "✗ API key not configured. Use --api-key option or configure manually."
                    )
                )
                return
        
        # Initialize driver and setup lottery types
        driver = CollectAPIDriver(vhost)
        lottery_types = driver.setup_lottery_types()
        
        self.stdout.write(
            self.style.SUCCESS(
                f"✓ Setup complete. Created {lottery_types.count()} lottery types:"
            )
        )
        
        for lottery_type in lottery_types:
            self.stdout.write(f"  - {lottery_type.name} ({lottery_type.slug})")
        
        self.stdout.write(
            self.style.SUCCESS(
                "\nYou can now run 'collectapi_sync' to fetch lottery results"
            )
        )
