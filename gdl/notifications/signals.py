import logging

import django
from django.dispatch import receiver
from notifications.models import AccountNotifications

log = logging.getLogger(__name__)



signal_notifications_account_message = django.dispatch.Signal()
signal_notifications_agent_message = django.dispatch.Signal()

# We expect the ACCOUNT signal to at least contain account, vhost, title, text. It may also contain data, vdomain, and icon.
@receiver(signal_notifications_account_message)
def signal_notifications_account_message_receiver(sender, **kwargs):
    notObj = AccountNotifications(account=kwargs['account'],title=kwargs['title'],text=kwargs['text'],vhost=kwargs['vhost'])
    for key in ["vdomain","icon","data"]:
        if key in kwargs:
            setattr(notObj,key,kwargs[key])
    notObj.save()


# # We expect the AGENT signal to at least contain account, vhost, title, text. It may also contain data, vdomain, and icon.
# @receiver(signal_notifications_agent_message)
# def signal_notifications_agent_message_receiver(sender, **kwargs):
#     notObj = AgentNotifications(agent=kwargs['agent'], title=kwargs['title'], text=kwargs['text'],
#                                   vhost=kwargs['vhost'])
#     for key in ["vdomain", "icon", "data"]:
#         if key in kwargs:
#             setattr(notObj, key, kwargs[key])
#     notObj.save()
#
#
#
