from datetime import date, datetime, timedelta

from dateutil.relativedelta import relativedelta
from django.contrib.auth.hashers import make_password, check_password
from django.http import JsonResponse
from django.template.defaulttags import csrf_token
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_protect

from cashier.models import AccountApplicationLimits, AccountLossesLimits, AccountLockouts
# from frontend.mycashier.forms import ApplicationLimitForm, AccountLossesLimitsForm
from minerve.toolkit.responses import generic_json_success
from toolkit.contexts import default_account_dashboard_context
from toolkit.decorators import account_login
from django.utils.translation import gettext_lazy as _

LIMITS_UPDATED_STR = _("Limits Updated!")
FORM_ERRORS_STR = _("Form Errors")
PERIOD_SPEC_STR = _("Period must be specified")
LOCKOUT_SPEC_STR = _("Lockout Until Date must be specified")
INV_LOCKOUT_SPEC_STR = _("Invalid Lockout until Date specified.")
CONFIRM_ACT_TOGGLE_STR = _("Please confirm the action by toggling the switch.")
INVALID_PASSWORD_STR = _("Invalid Password.")
LOCKOUT_SUCCESS_STR = _("Locked out Successfully.")

@account_login
@csrf_protect
def set_application_limit(request):
    vhost, vdomain, apperance, account, context = default_account_dashboard_context(request,"player")
    instance = AccountApplicationLimits.objects.get(uuid=request.POST["uuid"])
    modal_form = ApplicationLimitForm(request.POST,instance=instance)
    if modal_form.is_valid():
        modal_form.save()
        return generic_json_success(LIMITS_UPDATED_STR)
    else:
        return JsonResponse({"res": "err", "err": FORM_ERRORS_STR, "data": {"e": modal_form.errors}})

@csrf_protect
@account_login
def set_loss_limit(request):
    vhost, vdomain, apperance, account, context = default_account_dashboard_context(request,"player")
    instance = AccountLossesLimits.objects.get(uuid=request.POST["uuid"])
    modal_form = AccountLossesLimitsForm(request.POST,instance=instance)
    if modal_form.is_valid():
        modal_form.save()
        return generic_json_success(LIMITS_UPDATED_STR)
    else:
        return JsonResponse({"res": "err", "err": FORM_ERRORS_STR, "data": {"e": modal_form.errors}})

@csrf_protect
@account_login
def set_account_lockout(request):
    vhost, vdomain, apperance, account, context = default_account_dashboard_context(request,"player")
    # print(request.POST)
    if "period" not in request.POST:
        return JsonResponse({"res": "err", "err": PERIOD_SPEC_STR})
    period = request.POST["period"]
    if period == "c":
        if "custom" not in request.POST:
            return JsonResponse({"res": "err", "err": LOCKOUT_SPEC_STR})
        if not datetime.strptime(request.POST["custom"],"%Y-%m-%dT%H:%M"):
            return JsonResponse({"res": "err", "err": INV_LOCKOUT_SPEC_STR})
        expires_at = datetime.strptime(request.POST["custom"],"%Y-%m-%dT%H:%M")
    else:
        expires_at = datetime.now() + timedelta(seconds=int(request.POST["period"]))

    if "confirmSwitch" not in request.POST:
        return JsonResponse({"res": "err", "err": CONFIRM_ACT_TOGGLE_STR})

    if not check_password(request.POST["password"],account.secret):
        return JsonResponse({"res": "err", "err": INVALID_PASSWORD_STR})
    accountLockOutObj = AccountLockouts(account=account, lockout_period_start=now(),lockout_period_end=expires_at,vhost=vhost,active=True,confirmed=True)
    accountLockOutObj.save()
    return JsonResponse({"res": "ok","msg":LOCKOUT_SUCCESS_STR})

