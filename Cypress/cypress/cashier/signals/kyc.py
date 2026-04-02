import logging
import django.dispatch
from django.dispatch import receiver

from cashier.engine import Cashier
from cashier.models import AccountLevels

log = logging.getLogger(__name__)



signal_kyc_levelup = django.dispatch.Signal()

# print("Setting up signals")
@receiver(signal_kyc_levelup)
def check_for_kyc_levelups(sender, **kwargs):

    log.debug("Check KYC Signal called!")
    if "account" not in kwargs:
        log.debug("No account specified for KYC Levelup Signal")
        return
    account = kwargs["account"]
    if account.account_level:
        alvl = account.account_level.ordering_key + 1
    else:
        alvl = 0
    if "email" in kwargs and "mobile" in kwargs:
        next_level = AccountLevels.objects.filter(vhost=account.vhost, active=True, self_activation=True,
                                                  phone_kyc=True,email_kyc=True, ordering_key__gte=alvl)
    elif "email" not in kwargs:
        next_level = AccountLevels.objects.filter(vhost=account.vhost,active=True,self_activation=True,phone_kyc=True,email_kyc=False,ordering_key=alvl)
    else:
        next_level = AccountLevels.objects.filter(vhost=account.vhost, active=True, self_activation=True,
                                                  email_kyc=True, phone_kyc=False,ordering_key__gte=alvl)
    # print(next_level)
    if len(next_level) > 0:
        # print("KYC Level Up Signal")
        # print(next_level[0])
        log.debug("KYC Level Up Signal: Found Next Level! Processing...")
        log.debug(f"KYC Level Up Signal Applying Level {next_level[0]}")
        cashier = Cashier(account=account,vhost=account.vhost)
        try:
            cashier.set_account_level(next_level[0])
        except Exception as e:
            log.error(e)
            raise e

    else:
        return
