from django.core.signals import request_finished
from django.dispatch import receiver

from grader.engine.core import GraderEngine
from wager.signals import signal_wager_qualified


@receiver(signal_wager_qualified)
def wager_signal_match_final_handler(sender, **kwargs):
    print(sender,kwargs)
    wager = kwargs['wagerObj']
    print(f"Qualified state change signal from Wager! {sender}, {kwargs} - Calling Grader!")
    grader = GraderEngine(wager.vhost)
    grader.execute_qualified_wager(wager)
