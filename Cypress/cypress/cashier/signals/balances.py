import logging

from django.db.models.fields import return_None
import django.dispatch
from django.dispatch import receiver


log = logging.getLogger(__name__)


signal_balance_updated = django.dispatch.Signal()
signal_balance_deposit = django.dispatch.Signal()
signal_balance_withdrawal = django.dispatch.Signal()
signal_balance_wager_created = django.dispatch.Signal()
signal_balance_at_risk = django.dispatch.Signal()
signal_balance_wager_won = django.dispatch.Signal()
signal_deposit_confirmed = django.dispatch.Signal()  # For RAF: fired when pending deposit is confirmed

@receiver(signal_balance_wager_won)
def wager_won_handler(sender, **kwargs):
    log.debug("Wager Won Signal Handler called!")