import tablib
from django.core.management.base import BaseCommand

from parameters.models import VHost, VHostMenuEntry


class Command(BaseCommand):
    help = 'Export all the Menu items for the Agent Dashboard for the given VHost.'
    def add_arguments(self, parser):
        # Named (optional) arguments
        parser.add_argument("vhost",type=str,nargs="+")
        parser.add_argument("out_file", type=str, nargs="+")
    def handle(self, *args, **options):
        vHost = VHost.objects.get(pk=options["vhost"][0])
        data = tablib.Dataset(headers=["on_click","url","ordering_key","permission","font_awesome","name","help_text","active"])
        for entry in VHostMenuEntry.objects.filter(vhost=vHost):
            data.append((entry.on_click,entry.url,entry.ordering_key,entry.permission,entry.font_awesome,entry.name,entry.help_text,entry.active))
        with open(options["out_file"][0],"w+") as f:
            f.write(data.export('json'))




