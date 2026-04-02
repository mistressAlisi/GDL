from django.core.management.base import BaseCommand

from django.core.management.base import BaseCommand

from parameters.models import VHost, VHostMenuEntry, VHostDomain


class Command(BaseCommand):
    help = 'Add a Domain Listener for the specified VHost.'
    def add_arguments(self, parser):
        # Named (optional) arguments
        parser.add_argument("vhost",type=str,nargs="+")
        parser.add_argument("fqdn", type=str, nargs="+")
        parser.add_argument("addr", type=str, nargs="+")
    def handle(self, *args, **options):
        vHost = VHost.objects.get(pk=options["vhost"][0])
        try:
            domain = VHostDomain.objects.get(vhost=vHost,domain_fqdn=options["fqdn"][0])
        except VHostDomain.DoesNotExist:
            domain = VHostDomain(vhost=vHost, domain_fqdn=options["fqdn"][0])
            domain.domain_addr = options["addr"][0]
            domain.save()
            self.stdout.write(self.style.MIGRATE_LABEL(f'Virtual Host: {vHost.name} - Domain: {options["fqdn"][0]} - added'))
            return
        self.stdout.write(self.style.MIGRATE_LABEL(f'Virtual Host: {vHost.name} - Domain {options["fqdn"][0]} already registered. Doing nothing.'))
        return


