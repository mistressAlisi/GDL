from celery import shared_task
from celery.utils.log import get_task_logger

from account.models import Account

logger = get_task_logger(__name__)

@shared_task()
def account_mark_intro_seen(auuid):
    accountObj = Account.objects.get(uuid=auuid)
    if not accountObj.has_seen_intro_help:
        accountObj.has_seen_intro_help = True
        accountObj.save()