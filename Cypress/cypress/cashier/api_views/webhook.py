import base64
import hashlib,hmac
import importlib

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from account.models import Account
from cashier.engine import Cashier
from cashier.models import VDomainPaymentProviders
# from cryptocurrency.ipn.toolkit.hmac import create_ipn_hmac

from minerve.toolkit.errors import generic_json_error
from parameters.models import VHost, VHostCryptoParameters


@csrf_exempt
def webhook_handle(request,provider):
    # vhost, vdomain, apperance, context = default_dashboard_context(request, "player")
    print(provider)
    provObj = VDomainPaymentProviders.objects.get(active=True, vdomain=request.vdomain,payment_provider__withdrawals=True,payment_provider__name__icontains=provider)
    if provObj:
        modname = f"{provObj.payment_provider.module_name}.webhook"
        webhook_module = importlib.import_module(modname)
        return webhook_module.webhook_handle(request)
    else:
        return generic_json_error("Can't get shit in detroit!")
