"""
ionBlock Webhook Handler
Processes payment confirmation callbacks from ionBlock
"""
import json
import logging
from decimal import Decimal
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db import transaction as db_transaction
from django.utils.timezone import now

from cashier.models import (
    ProviderTX,
    IonBlockParameter,
    IonBlockChannel,
    IonBlockTransaction
)
from cashier.engine import Cashier
from .api import IonBlockAPIClient

logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(["POST"])
def webhook_handle(request):
    """
    Handle ionBlock webhook callbacks for deposit confirmations

    ionBlock POSTs to this endpoint when:
    - A deposit channel receives payment
    - A withdrawal is confirmed
    - Channel status changes

    Webhook payload:
    {
        "channel_id": 5,
        "status": 2,
        "receiver_reference": "uuid-here",
        "receiver_currency": "USD",
        "receiver_amount": 500,
        "address": "0x...",
        "sender_currency": "ETH",
        "sender_amount": 0.4792026,
        "sender_rate": 1043.4,
        "valid_until": 1490919030,
        "created_at": 1490918730
    }

    Headers:
    - X-Safebits-Callback-Id: Unique callback ID
    - X-Safebits-Signature: HMAC-SHA512 signature
    """
    try:
        # Get raw request body for signature verification
        raw_body = request.body.decode('utf-8')

        # Parse JSON payload
        try:
            payload = json.loads(raw_body)
        except json.JSONDecodeError:
            logger.error("Invalid JSON in webhook payload")
            return HttpResponseBadRequest("Invalid JSON")
        print(payload)
        # Get callback ID and signature from headers
        callback_id = request.headers.get('X-Safebits-Callback-Id')
        received_signature = request.headers.get('X-Safebits-Signature')

        if not callback_id or not received_signature:
            logger.error("Missing webhook headers")
            return HttpResponseBadRequest("Missing authentication headers")

        # Get receiver reference (our ProviderTX UUID)
        reference = payload.get('receiver_reference')
        if not reference:
            logger.error("Missing receiver_reference in webhook")
            return HttpResponseBadRequest("Missing receiver_reference")

        # Find the ProviderTX
        try:
            provider_tx = ProviderTX.objects.get(
                uuid=reference,
                provider='cashier.providers.ionBlock'
            )
        except ProviderTX.DoesNotExist:
            logger.error(f"ProviderTX not found: {reference}")
            return HttpResponseBadRequest("Transaction not found")

        # Get ionBlock configuration for signature verification
        try:
            config = IonBlockParameter.objects.get(vhost=provider_tx.vhost)
        except IonBlockParameter.DoesNotExist:
            logger.error(f"ionBlock config not found for vhost {provider_tx.vhost}")
            return HttpResponseForbidden("Configuration error")

        # Verify webhook signature
        api_client = IonBlockAPIClient(
            api_key=config.api_key,
            api_secret=config.api_secret
        )

        if not api_client.verify_webhook_signature(callback_id, raw_body, received_signature):
            logger.error(f"Invalid webhook signature for {reference}")
            return HttpResponseForbidden("Invalid signature")

        logger.info(f"Webhook signature verified for {reference}")

        # Process the webhook based on channel_id presence
        channel_id = payload.get('channel_id')
        status = payload.get('status', 1)

        if channel_id:
            # This is a deposit channel webhook
            result = process_deposit_webhook(provider_tx, payload, config)
        else:
            # This might be a withdrawal webhook or other notification
            logger.info(f"Received webhook without channel_id: {payload}")
            result = process_withdrawal_webhook(provider_tx, payload, config)

        return JsonResponse(result)

    except Exception as e:
        logger.exception(f"Error processing ionBlock webhook: {e}")
        return JsonResponse({"error": "Internal server error"}, status=500)


def process_deposit_webhook(provider_tx: ProviderTX, payload: dict, config: IonBlockParameter) -> dict:
    """
    Process deposit channel webhook

    Args:
        provider_tx: ProviderTX object
        payload: Webhook payload
        config: IonBlockParameter configuration

    Returns:
        Response dict
    """
    channel_id = payload['channel_id']
    status = payload.get('status', 1)

    logger.info(
        f"Processing deposit webhook for channel {channel_id}, "
        f"status={status}, reference={provider_tx.uuid}"
    )

    # Find the channel
    try:
        channel = IonBlockChannel.objects.get(
            channel_id=channel_id,
            receiver_reference=str(provider_tx.uuid)
        )
    except IonBlockChannel.DoesNotExist:
        logger.error(f"Channel not found: {channel_id}")
        return {"error": "Channel not found"}

    # Update channel with latest data
    channel.status = status
    channel.sender_amount = Decimal(str(payload.get('sender_amount', channel.sender_amount)))
    channel.sender_rate = Decimal(str(payload.get('sender_rate', channel.sender_rate or 0)))
    channel.ionblock_data = payload
    channel.save()

    # Check if payment is confirmed (status == 2)
    if status == 2:
        logger.info(f"Deposit confirmed for channel {channel_id}")

        # Use atomic transaction to prevent double-crediting
        with db_transaction.atomic():
            # Check if already processed
            if provider_tx.completed:
                logger.warning(f"Deposit already completed for {provider_tx.uuid}")
                return {"status": "already_processed"}

            # Update ProviderTX status
            provider_tx.status = '4'  # Payment Received
            provider_tx.confirmed_at = now()
            provider_tx.save()

            # Create/update IonBlockTransaction record
            ionblock_tx, created = IonBlockTransaction.objects.update_or_create(
                channel=channel,
                transaction_type='IN',
                defaults={
                    'vhost': provider_tx.vhost,
                    'account': provider_tx.account,
                    'status': 'confirmed',
                    'address': payload['address'],
                    'network': channel.network,
                    'sender_currency': payload['sender_currency'],
                    'sender_amount': Decimal(str(payload['sender_amount'])),
                    'receiver_currency': payload['receiver_currency'],
                    'receiver_amount': Decimal(str(payload['receiver_amount'])),
                    'rate': Decimal(str(payload.get('sender_rate', 0))),
                    'reference': str(provider_tx.uuid),
                    'provider_tx': provider_tx,
                    'confirmed_at': now(),
                    'ionblock_data': payload
                }
            )

            # Update channel confirmed timestamp
            if not channel.confirmed_at:
                channel.confirmed_at = now()
                channel.save()

            # Credit the account using Cashier engine
            cashier = Cashier(vhost=provider_tx.account.vhost,account=provider_tx.account)

            # Calculate final amount from actual transaction data in txs.data
            # (not the channel's expected sender_amount/sender_rate)
            final_amount = Decimal('0')
            txs_data = payload.get('txs', {}).get('data', [])
            for tx in txs_data:
                tx_sender_amount = Decimal(str(tx.get('sender_amount', 0)))
                tx_sender_rate = Decimal(str(tx.get('sender_rate', 0)))
                final_amount += tx_sender_amount * tx_sender_rate

            logger.info(f"Calculated final_amount from {len(txs_data)} transaction(s): {final_amount}")

            logger.info(
                f"Crediting account {provider_tx.account.uuid} with "
                f"{final_amount} {channel.receiver_currency}"
            )

            cashier.confirm_pending_deposit(provider_tx, final_amount)

            # Update ProviderTX to completed
            provider_tx.status = '5'  # Invoice Complete
            provider_tx.completed = True
            provider_tx.completed_at = now()
            provider_tx.save()

            logger.info(
                f"Deposit completed: {final_amount} {channel.receiver_currency} "
                f"for channel {channel_id}"
            )

            return {
                "status": "success",
                "credited": True,
                "amount": str(final_amount),
                "currency": channel.receiver_currency
            }

    elif status == 3:
        # Channel expired or failed
        logger.warning(f"Channel {channel_id} expired/failed")

        with db_transaction.atomic():
            if not provider_tx.completed:
                provider_tx.status = '103'  # Expired w/o payment
                provider_tx.cancelled_at = now()
                provider_tx.active = False
                provider_tx.save()

        return {"status": "expired"}

    else:
        # Status still pending (status == 1)
        logger.info(f"Channel {channel_id} still pending")
        return {"status": "pending"}


def process_withdrawal_webhook(provider_tx: ProviderTX, payload: dict, config: IonBlockParameter) -> dict:
    """
    Process withdrawal transaction webhook (if ionBlock sends them)

    Args:
        provider_tx: ProviderTX object
        payload: Webhook payload
        config: IonBlockParameter configuration

    Returns:
        Response dict

    Note: This is a placeholder. Implement based on actual ionBlock withdrawal webhook format.
    """
    transaction_id = payload.get('transaction_id')

    logger.info(f"Processing withdrawal webhook for transaction {transaction_id}")

    # Find the transaction
    try:
        ionblock_tx = IonBlockTransaction.objects.get(
            transaction_id=transaction_id,
            provider_tx=provider_tx
        )
    except IonBlockTransaction.DoesNotExist:
        logger.error(f"Transaction not found: {transaction_id}")
        return {"error": "Transaction not found"}

    # Update transaction
    ionblock_tx.status = 'confirmed'
    ionblock_tx.txid = payload.get('txid', ionblock_tx.txid)
    ionblock_tx.confirmed_at = now()
    ionblock_tx.ionblock_data = payload
    ionblock_tx.save()

    # Update ProviderTX
    with db_transaction.atomic():
        provider_tx.status = '5'  # Invoice Complete
        provider_tx.completed = True
        provider_tx.completed_at = now()
        provider_tx.save()

    logger.info(
        f"Debiting account {provider_tx.account.uuid} with "
        f"{provider_tx.amount} {ionblock_tx.receiver_currency}"
    )

    cashierObj = Cashier(vhost=provider_tx.account.vhost, account=provider_tx.account)
    cashierObj.confirm_pending_withdrawal(provider_tx, provider_tx.amount)

    logger.info(f"Withdrawal completed: {transaction_id}")

    return {"status": "success"}
