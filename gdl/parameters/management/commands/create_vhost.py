from django.core.management.base import BaseCommand

from django.core.management.base import BaseCommand

from parameters.models import VHost, VHostMenuEntry, VHostDomain


class Command(BaseCommand):
    help = 'Add a Domain/VHost.'
    def add_arguments(self, parser):
        # Named (optional) arguments
        parser.add_argument("vhost",type=str,nargs="+")


    def handle(self, *args, **options):
        vHost,cc = VHost.objects.get_or_create(name=options["vhost"][0])
        if cc:
            vHost.save()
            self.stdout.write(self.style.SUCCESS(f"Virtual Host {vHost.name} created."))
            return True
        else:
            self.stdout.write(self.style.WARNING(f'Virtual Host: {vHost.name} - already exists.'))
            return False


