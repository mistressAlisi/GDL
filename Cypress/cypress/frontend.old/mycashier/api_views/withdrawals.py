from decimal import Decimal
from math import floor

from django.contrib.auth.hashers import check_password
from django.http import JsonResponse

from cashier.engine import Cashier
from minerve.toolkit.errors import generic_json_error
from minerve.toolkit.responses import generic_json_success
from toolkit.contexts import default_account_dashboard_context
from toolkit.decorators import account_login
from django.utils.translation import gettext_lazy as _

INCORRECT_CREDS_STR = _("Incorrect credentials!")
WITHDRAWAL_REQ_CREATED_STR = _("Withdrawal Request Created!")
WITHDRAWAL_PROCESSING_MSG_STR = _("Your Withdrawal will be processed as soon as possible.")

@account_login
def create_gift_card_withdrawal(request):
    vhost, vdomain, apperance, account, context = default_account_dashboard_context(request,"player")
    amount = int(request.POST.get("withdrawal_amount"))*1000
    pwd = request.POST.get("acct_passwd")
    symbol = request.POST.get("symbol")
    cashier = Cashier(vhost,account)
    balance = cashier.get_balance_obj()
    avail = cashier.get_available_balance() - balance.at_risk
    wd_avail = floor(avail/100)
    if not check_password(pwd,account.secret):
        return JsonResponse({"res":"err","error":INCORRECT_CREDS_STR})
    if amount > wd_avail:
        avail_amount_exceeded_str = _("Desired amount {amount} exceeds available amount {wd_avail}").format(amount = amount, wd_avail = wd_avail)
        return generic_json_error(avail_amount_exceeded_str)
    stat,tx = cashier.create_withdrawal_ticket(vdomain,"giftcards",symbol,amount)
    if stat == 0:
        return generic_json_success(WITHDRAWAL_REQ_CREATED_STR,WITHDRAWAL_PROCESSING_MSG_STR)