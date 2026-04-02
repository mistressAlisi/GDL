from uuid import UUID

import uuid

from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand
from django.utils.crypto import get_random_string
from django.utils.timezone import now

from account.models import Account
from cashier.signals import signal_kyc_levelup
from parameters.models import VHost
from providers.apisports.admin import CoreTeamMapResource


class Command(BaseCommand):
    help = "Resets an Account Password."

    def add_arguments(self, parser):
        parser.add_argument("vhost",nargs='+', type=UUID,help="VHost to work on.")


    def handle(self, *args, **options):
        vhost = VHost.objects.get(uuid=options['vhost'][0])
        self.stdout.write(self.style.MIGRATE_HEADING(f"Creating Account at {vhost}..."))
        try:
            account_number = Account.objects.all().order_by('-acctnum')[0].acctnum + 1
        except IndexError:
            account_number = settings.DEFAULT_INITIAL_ACCOUNT_NUMBER
        pwsect = make_password(str(account_number))
        accountObj = Account(
            uuid=uuid.uuid4(),
            vhost=vhost,
            acctnum=account_number,
            active=True,
            credit_limit=0,
            secret=pwsect,
            activated=now(),
            )
        accountObj.save()
        signal_kyc_levelup.send(sender="account_created", mobile=True, email=True, account=accountObj)
        self.stdout.write(self.style.MIGRATE_HEADING(f"Account {accountObj.acctnum} created: Password is Acctnum."))

