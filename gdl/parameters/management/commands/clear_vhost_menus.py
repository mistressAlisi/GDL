from django.core.management.base import BaseCommand

from django.core.management.base import BaseCommand

from parameters.models import VHost, VHostMenuEntry


class Command(BaseCommand):
    help = 'Import a Menu items  file for the Agent Dashboard for the given VHost.'
    def add_arguments(self, parser):
        # Named (optional) arguments
        parser.add_argument("vhost",type=str,nargs="+")

    def handle(self, *args, **options):
        vHost = VHost.objects.get(pk=options["vhost"][0])
        VHostMenuEntry.objects.filter(vhost=vHost).delete()


