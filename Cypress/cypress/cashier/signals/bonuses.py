import logging

from django.db.models.fields import return_None
import django.dispatch
from django.dispatch import receiver


log = logging.getLogger(__name__)


signal_bonus_created = django.dispatch.Signal()
signal_bonus_paid = django.dispatch.Signal()
signal_bonus_rollover_met = django.dispatch.Signal()