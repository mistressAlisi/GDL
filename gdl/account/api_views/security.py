import json

from django.contrib.auth.hashers import check_password
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.translation import gettext_lazy as _
from account.models import Account

from cashier.engine import Cashier

ACCT_NOT_FOUND_STR = _("Account not found")
INCORRECT_CREDS_STR = _("Incorrect credentials!")
WELCOME_BACK_STR = _("Welcome back!")

@csrf_exempt
def account_login_handle(request):
    payload = json.loads(request.body)
    # print(payload)
    actname = payload["username"]
    password = payload["password"]
    acctObj = False
    acctnum = actname.upper()
    # print(acctnum,actname,request.vhost.uuid)
    try:
        acctObj = Account.objects.get(acctnum__iexact=acctnum,vhost=request.vhost,active=True)
        # print("DNE")
    except Account.DoesNotExist:
        try:
            acctObj = Account.objects.get(Q(email1__iexact=acctnum) | Q(acctname__iexact=actname), vhost=request.vhost,active=True)
        except Account.DoesNotExist:
            return JsonResponse({"res":"err","err":ACCT_NOT_FOUND_STR})
    if not acctObj: return False
    if not check_password(password,acctObj.secret):
        return JsonResponse({"res":"err","err":INCORRECT_CREDS_STR})
    request.session["account_id"] = str(acctObj.uuid)
    request.session.modified = True
    request.session.set_expiry(0)
    # tObjs = GDLTicketCartCache.objects.filter(vhost=vhost, domain=vdomain, account=acctObj)
    # for t in tObjs:
    #     t.delete()
    cashier = Cashier(vhost=request.vhost,account=acctObj)
    # print(cashier)
    balances = {
    "latest_balance": cashier.get_balance(),
    "latest_bonus": cashier.get_available_bonus(),
    "pending": cashier.get_at_risk_balance(),
    "available":cashier.get_available_balance()+cashier.get_available_bonus()
    }
    data = {
        "uuid":acctObj.uuid,
        "acctnum": acctObj.acctnum,
        "acctname": acctObj.acctname,
        "pronouns": acctObj.pronouns,
        "balances": balances,
        "email":acctObj.email1
    }
    if acctObj.avatar:
        data["avatar"] = acctObj.avatar.url
    else:
        data["avatar"] = None

    return JsonResponse({"res":"ok","msg":WELCOME_BACK_STR,"data":data},safe=False)