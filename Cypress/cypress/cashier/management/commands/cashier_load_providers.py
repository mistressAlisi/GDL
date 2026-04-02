import importlib
import os

from django.core.management.base import BaseCommand

from cashier.models import PaymentProviders



class Command(BaseCommand):
    help = "Imports the Available Cashier Payment Providers into the Database."
    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING("Importing Available Cashier Payment Providers"))
        pdir = os.listdir(os.getcwd()+"/cashier/providers")
        for pt in pdir:
            fpt = os.getcwd()+"/cashier/providers/"+pt
            if os.path.isdir(fpt) and pt[0] != "_":
                self.stdout.write(self.style.MIGRATE_LABEL(f"Attempting Import; Provider: {pt}..."))
                modname = f"cashier.providers.{pt}"

                try:
                    config_module = importlib.import_module(f"{modname}.provider")
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Could not import provider f{modname}.provider: {e}"))
                    continue
                ppObj = PaymentProviders.objects.get_or_create(module_name=modname)[0]
                for key in ["name","is_fiat","is_crypto","icon_class","ordering_key","deposits","dep_min","dep_max","dep_fees","withdrawals","wdl_min","wdl_max","wdl_fees","description","default_crypto"]:
                    if key in config_module.PAYMENT_PROVIDER_INFO:

                        setattr(ppObj,key,config_module.PAYMENT_PROVIDER_INFO[key])
                ppObj.save()
                self.stdout.write(self.style.SUCCESS(f"Imported {ppObj.name}!"))


