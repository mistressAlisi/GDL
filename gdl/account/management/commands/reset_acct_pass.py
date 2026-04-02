from uuid import UUID

from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand
from django.utils.crypto import get_random_string

from account.models import Account
from parameters.models import VHost


class Command(BaseCommand):
    help = "Resets an Account Password."

    def add_arguments(self, parser):
        parser.add_argument("vhost",nargs='+', type=UUID,help="VHost to work on.")
        parser.add_argument("account",nargs='+', type=int,help="Account Number to work on.")

    def handle(self, *args, **options):
        vhost = VHost.objects.get(uuid=options['vhost'][0])
        account = Account.objects.get(acctnum=options['account'][0])
        self.stdout.write(self.style.MIGRATE_HEADING(f"Resetting Account Password for {account.acctnum} at {vhost}..."))
        password = get_random_string(8)
        account.secret = make_password(password)
        account.save()
        self.stdout.write(self.style.MIGRATE_HEADING(f"Account Password for {account.acctnum} is now {password}."))

