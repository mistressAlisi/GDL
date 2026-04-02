from django.core.management.base import BaseCommand
from tablib import Dataset

from parameters.models import VHost, VHostMenuEntry


class Command(BaseCommand):
    help = 'Import a Menu items  file for the Agent Dashboard for the given VHost.'
    def add_arguments(self, parser):
        # Named (optional) arguments
        parser.add_argument("vhost",type=str,nargs="+")
        parser.add_argument("in_file", type=str, nargs="+")
    def handle(self, *args, **options):
        vHost = VHost.objects.get(pk=options["vhost"][0])
        with open(options["in_file"][0],"r") as fh:
            imported_data = Dataset().load(fh.read(),'json')
            for entry in imported_data.dict:
                vHObj,cc = VHostMenuEntry.objects.get_or_create(vhost=vHost,name=entry["name"])
                if cc:
                    vHObj.save()
                vHObj.on_click=entry["on_click"]
                vHObj.url=entry["url"]
                vHObj.ordering_key=entry["ordering_key"]
                vHObj.permission=entry["permission"]
                vHObj.font_awesome=entry["font_awesome"]
                vHObj.help_text=entry["help_text"]
                vHObj.active=entry["active"]
                vHObj.save()




