import base64
from  datetime import datetime
import hashlib,hmac
import json
from decimal import Decimal

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from account.models import Account
from cashier.engine import Cashier
from cashier.models import ProviderTX
from cashier.providers.coinpayments.api import CoinPaymentsAPI
from cryptocurrency.ipn.toolkit.hmac import create_ipn_hmac
from ledger.models import VHostCryptoTransactionLedger
from parameters.models import VHost, VHostCryptoParameters
from toolkit import contexts
from toolkit.contexts import default_account_dashboard_context, default_dashboard_context
from toolkit.vhosts import get_vhost_and_apperance
from toolkit.wagers.ledger_tools import deposit_to_acct

from cashier.providers.coinpayments import api


@csrf_exempt
def webhook_handle(request):
    vhost, vdomain, apperance, context = default_dashboard_context(request)
    cpApi = CoinPaymentsAPI(vhost)
    if (cpApi.validate_request('POST',request)):
        data = json.loads(request.body)
        try:
            pTxObj = ProviderTX.objects.get(provider_tx=data["invoice"]["id"])
        except:
            return JsonResponse({"res": "ok","msg":"TX not created yet."})
        txType = data["type"]
        custom_data = data["invoice"]["customData"]
        # print(pTxObj)
        # print(txType)
        # print(custom_data)
        # print("-----------")
        # print(request.body)
        if txType == "InvoicePending":
            pTxObj.status = '2'
            pTxObj.save()
        elif txType == "InvoicePaid":
            pTxObj.status = '4'
            pTxObj.invoice_paid = True
            pTxObj.confirmed_at = datetime.fromtimestamp(data["invoice"]["confirmedAt"])
            pTxObj.save()
        elif txType == "InvoiceCompleted":
            pTxObj.status = '5'
            pTxObj.completed_at = datetime.fromtimestamp(data["invoice"]["completedAt"])
            final_amount = Decimal(data["invoice"]["payments"][0]["payout"]["payoutAmountToMerchantInNativeCurrency"]/100)
            cashier = Cashier(pTxObj.account,vhost=vhost)
            # print(final_amount,pTxObj.amount)
            cashier.confirm_pending_deposit(pTxObj,final_amount)
            print(f"CaChing goes the Cashier! {final_amount}")
            pTxObj.save()
        return JsonResponse({"res": "ok"})
    else:
        return JsonResponse({"res": "err","msg":"Cryptographic Error"},status=500)

# def webhook_handle(request):
#     vhost, vdomain, apperance, account, context = default_account_dashboard_context(request)
#     cryptoParams = VHostCryptoParameters.objects.get(vhost=vhost)
#     if cryptoParams.crypto_enabled != True:
#         return JsonResponse({'status': 'error', 'message': 'crypto is disabled'})
#     if 'HTTP_HMAC' not in request.META or request.META['HTTP_HMAC'] == "":
#         return JsonResponse({"res":"err","err":"No HMAC signature!"})
#     if 'merchant' not in request.POST or request.POST['merchant'] != cryptoParams.cpay_merchantid:
#         return JsonResponse({"res":"err","err":"Invalid merchant ID"})
#     signature = create_ipn_hmac(request, cryptoParams.cpay_ipn)
#     if signature != request.META['HTTP_HMAC']:
#         return JsonResponse({"res":"err","err":"Invalid HMAC Signature!!!"})
#     if "ipn_mode" not in request.POST or request.POST["ipn_mode"] != "hmac":
#         return JsonResponse({"res":"err","err":"Invalid ipn mode"})
#     # print(request.POST["invoice"])
#     auuid,amount = request.POST["invoice"].split(":::")
#     try:
#         accountObj = Account.objects.get(uuid=auuid)
#     except Account.DoesNotExist:
#         return JsonResponse({"res":"err","err":"Account not found"})
#     txn = request.POST["txn_id"]
#     transaction,created = VHostCryptoTransactionLedger.objects.get_or_create(vhost=vhost,account=accountObj,txn_id=txn)
#     if created:
#         transaction.deposit_id = request.POST["ipn_id"]
#         transaction.amount1 = float(request.POST["amount1"])
#         transaction.amount2 = float(request.POST["amount2"])
#         transaction.currency1 = request.POST["currency1"]
#         transaction.currency2 = request.POST["currency2"]
#         transaction.fee = float(request.POST["fee"])
#         transaction.tax = float(request.POST["tax"])
#         if 'net' in request.POST:
#             transaction.net = float(request.POST["net"])
#         if request.POST['ipn_type'] == "button":
#             transaction.type = 'd'
#     new_status = int(request.POST["status"])
#     received = float(request.POST["received_amount"])
#     if not transaction.deposited and (new_status >= 100 or new_status == 2):
#             # Transaction completed, deposit the funds!
#             amount_bought = cryptoParams.token_base_currency_xrate * transaction.amount1
#             deposit_to_acct(accountObj,,f"Coinpayments Transaction: {transaction.txn_id}")
#             transaction.deposited = True
#             # print("Deposited",transaction)
#     transaction.received = received
#     transaction.status = new_status
#     transaction.status_text = request.POST["status_text"]
#     transaction.save()
#     # print("=====Trusted:====")
#     # print(request.POST["status_text"])
#     # print(request.POST["received_amount"])
#     # print("=========")
#     # print("*********")
#     return JsonResponse({"res":"ok"})