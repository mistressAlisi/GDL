from django.core.management.base import BaseCommand

from parameters.models import VHost


class Command(BaseCommand):
    help = 'List all VHosts in this cluster.'

    def handle(self, *args, **options):
        _vHost = VHost.objects.all()
        for vhost in _vHost:
            self.stdout.write(self.style.MIGRATE_HEADING(f'Virtual Host: {vhost.name} - UUID: {vhost.uuid}'))





