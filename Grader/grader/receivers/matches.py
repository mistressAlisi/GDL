from django.core.signals import request_finished
from django.dispatch import receiver
from matches.signals import signal_match_final
from grader.engine.core import GraderEngine




def match_signal_match_final_handler(sender,**kwargs):
    # print(kwargs)
    # vhost = kwargs['vhost']
    if 'match' in kwargs:
        matches = [kwargs['match']]
    elif 'matches' in kwargs:
        matches = kwargs['matches']

    # print(f"Match state change signal from Cashier! {sender}, {kwargs} - Calling Grader!")
    grader = GraderEngine(matches[0].vhost)
    for match in matches:
        grader.qualify_match_wagers(match)
        # print(match)