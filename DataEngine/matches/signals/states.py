import logging

from django.db.models.fields import return_None
import django.dispatch
from django.dispatch import receiver


log = logging.getLogger(__name__)

signal_match_state_changed = django.dispatch.Signal()
signal_match_started = django.dispatch.Signal()
signal_match_halftime = django.dispatch.Signal()
signal_match_secondhalf = django.dispatch.Signal()
signal_match_final = django.dispatch.Signal()
signal_match_wagers_paid = django.dispatch.Signal()

# @receiver(signal_match_state_changed)
# def check_for_match_states(sender, **kwargs):
#         print(f"signal_match_state_changed Called! Sender: {sender} Kwargs: {kwargs}")