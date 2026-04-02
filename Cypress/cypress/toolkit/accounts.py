from datetime import timedelta

import uuid

from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.core.checks import database
from django.db import transaction
from django.db.models import Q, Func, CharField, F, Value
from django.utils.timezone import now

from account.models import Account, AccountActivationTokens
from agent.models import Agent
from cashier.engine import Cashier
from parameters.models import AccountParameters, Timezone


def account_email_in_use(vhost,email):
    accountObj = Account.objects.filter(Q(vhost=vhost) & Q(email1__iexact=email) | Q(
            email2__iexact=email))
    if len(accountObj) > 0:
        return True
    else:
        return False


def get_account_by_email(vhost,email):
    accountObj = Account.objects.filter(Q(vhost=vhost) & Q(email1__iexact=email) | Q(
            email2__iexact=email))
    if len(accountObj) > 0:
        return accountObj[0]
    else:
        return False

def account_mobile_in_use(vhost,mobile):
    accountObj = Account.objects.filter(Q(vhost=vhost) & Q(mobile=mobile))
    if len(accountObj) > 0:
        return True
    else:
        return False

def get_agent_accounts_options(user):
    if user.has_perm("user_view_all_accounts"):
        accounts = Account.objects.all()

    else:
        agentObj = Agent.objects.get(user=user)
        accounts = Account.objects.all(agent=agentObj)
    detail_view_options = []
    for account in accounts:
        detail_view_options.append({'value': account.uuid, 'label': f"#{account.acctnum} - ({account.holder})"})
    return detail_view_options


@transaction.atomic
def create_account(vhost,email1,password,**kwargs):
    # print(additional_param)

    if account_email_in_use(vhost,email1) or not vhost.reg_active:
        return False,False
    try:
        account_number = int(Account.objects.filter(vhost=vhost).annotate(
            acct_number=Func(
        F('acctnum'),
            Value(r'^([A-Za-z]+)([0-9]+)$'),
            Value(r'\2'),
            function='regexp_replace',
            output_field=CharField(),
    )).order_by('-acct_number')[0].acct_number)+1

    except IndexError:
        account_number = settings.DEFAULT_INITIAL_ACCOUNT_NUMBER

    pwsect = make_password(password)
    password=False
    aparameters,cc = AccountParameters.objects.get_or_create(vhost=vhost)
    # Get agent:
    manager = False
    if "manager" in kwargs:
        manager = kwargs["manager"]
    elif "domain" in kwargs:
        domain = kwargs["domain"]
        if domain.default_manager:
            manager = domain.default_manager
    if manager:
        account_number = f"{manager.acctnum_prefix}{account_number}"
    if cc:
        aparameters.save()
    tzObj = Timezone.objects.get(id=456)
    accountObj = Account(
        uuid=uuid.uuid4(),
        vhost=vhost,
        manager=manager,
        acctnum=account_number,
        email1=email1,
        credit_limit=aparameters.initial_credit,
        timezone=tzObj,

        secret=pwsect)
    if "account_active" not in kwargs:
        accountObj.active = False

    if "additional_param" in kwargs:
        additional_param = kwargs["additional_param"]
        for k, i in additional_param.items():
            setattr(accountObj,k,i)

    accountObj.save()
    # Activating the Promo codes:
    if "promo" in kwargs:
        promo = kwargs["promo"]
        cashier = Cashier(vhost=vhost,account=accountObj)
        cashier.account_activate_promocode(promo.promo_code)
    if "account_active" not in kwargs:
        aat = AccountActivationTokens(account=accountObj,expires=now()+timedelta(minutes=30))
        aat.save()
    else:
        aat = []
    return accountObj,aat



