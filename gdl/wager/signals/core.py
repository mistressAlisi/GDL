import logging
import django.dispatch

log = logging.getLogger(__name__)


signal_wager_created = django.dispatch.Signal()
signal_wager_lost = django.dispatch.Signal()
signal_wager_won = django.dispatch.Signal()
signal_wager_draw = django.dispatch.Signal()
signal_wager_qualified = django.dispatch.Signal()
signal_wager_closed = django.dispatch.Signal()
signal_wager_executed = django.dispatch.Signal()

