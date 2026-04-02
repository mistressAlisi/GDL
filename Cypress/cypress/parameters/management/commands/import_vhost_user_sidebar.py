from django.core.management.base import BaseCommand
from tablib import Dataset

from parameters.models import VHost, VHostMenuEntry, VHostUserSideBarEntry, VHostUserSideBarSubmenuEntry, Locales


class Command(BaseCommand):
    help = 'Import a Sidebar  items  file for the User Dashboard for the given VHost.'
    def add_arguments(self, parser):
        # Named (optional) arguments
        parser.add_argument("vhost",type=str,nargs="+")
        parser.add_argument("in_file", type=str, nargs="+")
    def handle(self, *args, **options):
        vHost = VHost.objects.get(pk=options["vhost"][0])
        with open(options["in_file"][0],"r") as fh:
            imported_data = Dataset().load(fh.read(),'json')
            for entry in imported_data.dict:
                vHObj,cc = VHostUserSideBarEntry.objects.get_or_create(vhost=vHost,name=entry["name"])
                if cc:
                    vHObj.save()
                vHObj.on_click=entry["on_click"]
                vHObj.url=entry["url"]
                vHObj.ordering_key=entry["ordering_key"]
                vHObj.permission=entry["permission"]
                vHObj.icon=entry["icon"]
                vHObj.help_text=entry["help_text"]
                vHObj.active=entry["active"]
                vHObj.ordering_key=entry["ordering_key"]
                vHObj.save()

                for submenu in entry["submenus"]:
                    locale,lcs = Locales.objects.get_or_create(id=submenu["locale"])
                    if lcs:
                        locale.save()
                    subMenuObj,_ = VHostUserSideBarSubmenuEntry.objects.get_or_create(name=submenu["name"],locale=locale,menu=vHObj)
                    subMenuObj.ordering_key=submenu["ordering_key"]
                    subMenuObj.permission=submenu["permission"]
                    subMenuObj.icon=submenu["icon"]
                    subMenuObj.help_text=submenu["help_text"]
                    subMenuObj.active=submenu["active"]
                    subMenuObj.url=submenu["url"]
                    subMenuObj.active=submenu["active"]
                    subMenuObj.save()


