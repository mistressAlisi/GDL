import tablib
from django.core.management.base import BaseCommand

from parameters.models import VHost, VHostMenuEntry, VHostSideBarEntry, VHostUserSideBarEntry


class Command(BaseCommand):
    help = 'Export all the Menu items for the User Sidebar Dashboard for the given VHost.'
    def add_arguments(self, parser):
        # Named (optional) arguments
        parser.add_argument("vhost",type=str,nargs="+")
        parser.add_argument("out_file", type=str, nargs="+")
    def handle(self, *args, **options):
        vHost = VHost.objects.get(pk=options["vhost"][0])
        data = tablib.Dataset(headers=["on_click","url","ordering_key","permission","icon","name","help_text","active","submenus"])
        for entry in VHostUserSideBarEntry.objects.filter(vhost=vHost):
            subentries = entry.get_submenus()
            sub_data = []
            for subentry in subentries:
                sub_data.append(
                    {
                     "url":subentry.url,
                     "ordering_key":subentry.ordering_key,
                     "permission":subentry.permission,
                     "icon":subentry.icon,
                     "on_click":subentry.on_click,
                     "locale":subentry.locale.id,
                     "name":subentry.name,
                     "help_text":subentry.help_text,
                     "active":subentry.active
                     }
                )

            data.append((entry.on_click,entry.url,entry.ordering_key,entry.permission,entry.icon,entry.name,entry.help_text,entry.active,sub_data))
        with open(options["out_file"][0],"w+") as f:
            f.write(data.export('json'))




