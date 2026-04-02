import logging
from decimal import Decimal

from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_GET

from cashier.engine import Cashier
from cashier.models import VDomainPaymentProviders, IonBlockChannel, IonBlockParameter
from cashier.providers.ionBlock.api import IonBlockAPIClient
from minerve.toolkit.errors import generic_json_error
from minerve.toolkit.responses import generic_json_success


logger = logging.getLogger(__name__)

@csrf_protect
@transaction.atomic
def start_deposit_handle(request):
    provider = request.POST.get('provider') or request.GET.get('provider')
    cashier = Cashier(account=request.account,vhost=request.vhost)
    if provider == "cashier.providers.ionBlock":
        amount = request.POST.get('amount') or request.GET.get('amount')
        currency_selected = request.POST.get('currency') or request.GET.get('currency')
        if amount:
            try:
                amount_decimal = Decimal(str(amount))
                logger.info(f"ionBlock: Creating deposit ticket for ${amount_decimal}")
                result = cashier.create_deposit_ticket(
                    request.vdomain,
                    provider,
                    amount_decimal,
                    currency=currency_selected
                )
                # Check if result is an error JsonResponse
                if isinstance(result, JsonResponse):
                    logger.error(f"ionBlock: Deposit failed, returning error response")
                    return result
                if result[0] == -2:
                    # Success - channel created, send payment details
                    channel_data = result[1]
                    # print("Channel Data::")
                    # print(channel_data, type(channel_data))
                    logger.info(f"ionBlock: Channel created successfully: {channel_data.get('channel_id', 'N/A')}")
                    result_data = {
                        "res":"ok",
                        "receiver_amount": f"{channel_data['receiver_amount']} USD",  # Accessing using key
                        "send_amount": float(channel_data['sender_amount']),  # Accessing using key
                        "send_currency": channel_data['sender_currency'],  # Accessing using key
                        "network": channel_data['network'],  # Accessing using key
                        "deposit_address": channel_data['address'],
                    }
                    logger.info(f"ionBlock: Result status code: {result[0]}")
                    return JsonResponse(result_data,safe=False)
                else:
                    logger.error(f"ionBlock: Unexpected result code: {result[0]}")
                    return generic_json_error("Provider Error", "Unable to create payment channel")
            except Exception as e:
                logger.error(f"ionBlock: Exception occurred: {str(e)}", exc_info=True)
                return generic_json_error("Cashier Error", str(e))


@csrf_protect
@transaction.atomic
def validate_deposit(request):
    if 'account_id' not in request.session:
        return redirect("/login")

    provider = request.POST["provider"]
    amount = Decimal(request.POST["amount"])
    cashier = Cashier(vhost=request.vhost,account=request.account)
    providers = cashier.get_available_deposit_providers(request.vdomain)
    try:
        chosen_provider = providers.get(payment_provider__module_name=provider).payment_provider
    except VDomainPaymentProviders.DoesNotExist:
        return generic_json_error("Cashier Providers", f"No such provider: {provider}")
    if amount < chosen_provider.dep_min:
        return generic_json_error("Beneath Minimums","Beneath Minimum Deposit for provider")
    if amount > chosen_provider.dep_max:
        return generic_json_error("Above Maximum","Deposit Exceeds Maximum for provider")
    kwargs = {}
    for key in request.POST:
        if key not in ["vdomain", "provider", "amount", "csrfmiddlewaretoken"]:
            kwargs[key] = request.POST[key]

    # results = cashier.create_deposit_ticket(vdomain, provider, amount, **kwargs)
    try:
        # print(request.POST)
        results = cashier.create_deposit_ticket(request.vdomain, provider, amount, **kwargs)
    except Exception as e:
        print(e)
        return generic_json_error("Cashier Error", str(e))
    if type(results) == JsonResponse:
        return results

    elif results[0] == True:
        # COMPLETE!!
        return JsonResponse({"res":"ok","avail_balance":round(cashier.get_available_balance(),2),"msg":f"Success! TXID: {results[1].uuid}"})
    elif results[0] == 0:
        # PEEEEEENDING!!!!
        return JsonResponse({"res": "ok","status":"pending", "title": f"Transaction is pending with the chosen external provider.","body_msg":f"You may follow it in pending transactions.<br/>Transaction ID: {results[1]}","msg":"Deposit Complete!"})
    elif results[0] == -1:
        # EXTERNAL VALIDATION NEEDED / OH EVER SO PENDING!
        return JsonResponse(
            {"res": "ok", "status": "external", "title": f"Transaction must be completed with the chosen external provider.",
             "msg": f"Please leave this tab/window open and visit your payment provider to finish the payment.",
            "body_msg":f"<br/> <a href='{results[2]}' target='_blank' class=\'btn btn-success'>Continue to Payment Provider</a>"})
    elif results[0] == -2:
        #  PAYMENT WILL BE HANDLED INTERNALLY USING CASHIER UI:
        return JsonResponse({
            "res": "ok",
            "hdr": "Ready to deposit!",
            "msg":f"Please Complete the payment to complete the transaction.",
            "further_steps":
                [{
                    "type":"capture_payment",
                    "data": results[1]
                }
                ]
        })

    # TODO: Gotta finish this handle-out
    return generic_json_error("I dont", "like you")


@require_GET
def check_ionblock_status(request):
    """
    Check ionBlock channel payment status

    Query params:
        channel_id: ionBlock channel ID (numeric ID from ionBlock API)

    Returns:
        {
            "status": "pending" | "confirmed" | "expired",
            "channel_status": 1 | 2 | 3,
            "txs": [...],
            "receiver_amount": "100.00",
            "sender_amount": "0.0479",
            ...
        }
    """
    if 'account_id' not in request.session:
        return JsonResponse({"error": "Not authenticated"}, status=401)

    channel_id = request.GET.get('channel_id')
    if not channel_id:
        return JsonResponse({"error": "Missing channel_id"}, status=400)

    try:
        # Find our internal channel record by ionBlock's channel_id
        channel = IonBlockChannel.objects.get(channel_id=channel_id)

        # Verify the channel belongs to the logged-in user
        if str(channel.account.uuid) != request.session.get('account_id'):
            return JsonResponse({"error": "Unauthorized"}, status=403)

        # Get ionBlock config for API access
        config = IonBlockParameter.objects.get(vhost=channel.vhost)

        # Query ionBlock API
        api_client = IonBlockAPIClient(
            api_key=config.api_key,
            api_secret=config.api_secret,
            base_url=config.api_endpoint
        )

        channel_data = api_client.get_channel_transactions(channel.channel_id)

        # Map status codes to strings
        status_map = {1: "pending", 2: "confirmed", 3: "expired"}
        status_code = channel_data.get('status', 1)
        status_str = status_map.get(status_code, "unknown")

        return JsonResponse({
            "res": "ok",
            "status": status_str,
            "channel_status": status_code,
            "txs": channel_data.get('txs', {}).get('data', []),
            "receiver_amount": str(channel_data.get('receiver_amount', 0)),
            "sender_amount": str(channel_data.get('sender_amount', 0)),
            "sender_currency": channel_data.get('sender_currency'),
            "address": channel_data.get('address'),
            "valid_until": channel_data.get('valid_until')
        })

    except IonBlockChannel.DoesNotExist:
        return JsonResponse({"error": "Channel not found"}, status=404)
    except IonBlockParameter.DoesNotExist:
        logger.error(f"ionBlock config not found for Parameter")
        return JsonResponse({"error": "Configuration error"}, status=500)
    except Exception as e:
        logger.exception(f"Error checking ionBlock status: {e}")
        return JsonResponse({"error": str(e)}, status=500)

