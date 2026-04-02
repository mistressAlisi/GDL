from decimal import Decimal

from django.contrib.auth.hashers import check_password
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_protect

from cashier.engine import Cashier
from cashier.models import VDomainPaymentProviders, CryptoCurrency
from minerve.toolkit.errors import generic_json_error
from minerve.toolkit.responses import generic_json_success

@csrf_protect
@transaction.atomic
def validate_withdrawal(request):
    provider = request.POST.get('provider') or request.GET.get('provider')
    cashier = Cashier(account=request.account, vhost=request.vhost)
    if provider == "cashier.providers.ionBlock":
        amount = request.POST.get('amount') or request.GET.get('amount')
        currency = request.POST.get('currency') or request.GET.get('currency')
        exchange = CryptoCurrency.objects.get(vhost=request.vhost, symbol=currency)
        if currency == "USDT":
            exchange_rate = 1
        else:
            exchange_rate = float(exchange.current_usd_exr)
        crypto_amount = round(amount / exchange_rate, 5)
    pwd = request.POST.get("password")

    if not check_password(pwd,request.account.secret):
        return generic_json_error("Incorrect credentials!","Please check your password!")
    provider = request.POST.get('provider')
    cashier = Cashier(vhost=request.vhost,account=request.account)

    # Get and validate amount
    import logging
    logger = logging.getLogger(__name__)
    amount_str = request.POST.get("amount", "0")
    logger.info(f"Withdrawal amount from POST: '{amount_str}'")
    amount = Decimal(amount_str)
    logger.info(f"Withdrawal amount as Decimal: {amount}")
    providers = cashier.get_available_withdrawal_providers(request.vdomain,module=provider)
    # print(providers)
    # return generic_json_error("nope","nopecopter")
    try:
        chosen_provider = providers.get(payment_provider__module_name=provider).payment_provider
        if "symbol" in request.POST:
            crypto = request.POST.get("symbol")
        else:
            crypto = chosen_provider.default_crypto
        currency = request.POST.get('currency')
        # print(currency)
        try:
            cco = CryptoCurrency.objects.get(vhost=request.vhost,symbol=currency)
        except CryptoCurrency.DoesNotExist:
            return generic_json_error("Invalid Currency", f"Currency is not supported or enabled {currency}")
        network = cco.exchange_network
        # For ionBlock and hotwallet, we send USD directly (1 token = $1 USD)
        # TODO/NOTE: Not sure about this - doing default conversion by now using CCO cur exchange rate objs.
        # # The provider handles USD->crypto conversion
        # if provider in ["ionBlock", "hotwallet"]:
        #     xamount = amount  # Amount is already in USD (tokens)
        # else:
        #     # For other providers, convert using exchange rate
        xchng = cco.current_usd_exr
        if xchng == 0:
            return generic_json_error("Exchange Rate Error", "Exchange rate is not available")
        xamount = amount / xchng
    except VDomainPaymentProviders.DoesNotExist:
        return generic_json_error("Cashier Providers", f"No such provider: {provider}")
    if xamount < chosen_provider.wdl_min:
        return generic_json_error("Beneath Minimums","Beneath Minimum Withdraw for provider")
    if xamount > chosen_provider.wdl_max:
        return generic_json_error("Above Maximum","Withdraw Exceeds Maximum for provider")
    try:
        # Get additional parameters for crypto withdrawals (ionBlock, hotwallet)
        address = request.POST.get('deposit_address', '').strip()
        if crypto == "ETH":
            if not address.startswith('0x') or len(address) != 42:
                return generic_json_error(
                    "Invalid Address",
                    "Please enter a valid Ethereum address (0x...)"
                )
        # Pass address and network to withdrawal ticket creation
        results = cashier.create_withdrawal_ticket(
            request.vdomain,
            provider,
            crypto,
            amount,
            address=address,
            network=network,
            xchng=xchng
        )
    except Exception as e:
        logger.exception(f"Withdrawal error: {e}")
        return generic_json_error("Cashier Error", str(e))
    if type(results) == JsonResponse:
        return results

    elif results[0] == True:
        # COMPLETE!!
        return JsonResponse({"res":"ok","avail_balance":round(cashier.get_available_balance(),2),"msg":f"Success! TXID: {results[1].uuid}"})
    elif results[0] == 0:
        # PEEEEEENDING!!!!
        return JsonResponse({"res": "ok","status":"pending", "title": f"Transaction is pending with the chosen external provider.","body_msg":f"You may follow it in pending transactions.<br/>Transaction ID: {results[1]}","msg":"Withdrawal Pending!"})
    elif results[0] == -1:
        # EXTERNAL VALIDATION NEEDED / OH EVER SO PENDING!
        return JsonResponse(
            {"res": "ok", "status": "external", "title": f"Transaction must be completed with the chosen external provider.",
             "msg": f"Please leave this tab/window open and visit your payment provider to finish the payment.",
            "body_msg":f"<br/> <a href='{results[2]}' target='_blank' class=\'btn btn-success'>Continue to Payment Provider</a>"})
    # TODO: Gotta finish this handle-out
    return generic_json_error("I dont", "like you")

