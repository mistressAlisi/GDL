"""
ionBlock Deposit Provider
Handles creation of deposit channels for cryptocurrency payments
"""
import logging
from decimal import Decimal
from django.utils.timezone import now
from datetime import timedelta

from cashier.models import (
    ProviderTX,
    IonBlockParameter,
    IonBlockChannel,
    IonBlockTransaction,
    CryptoCurrency
)
from .api import IonBlockAPIClient

logger = logging.getLogger(__name__)


class DepositProvider:
    """
    Handles deposit creation via ionBlock payment channels

    Flow:
    1. Create ionBlock channel (generates unique deposit address)
    2. Create database records (ProviderTX, IonBlockChannel)
    3. Return payment details to user (address, QR code, amount)
    4. User sends crypto to address
    5. Webhook confirms payment and credits account
    """

    def create_deposit(self, domain, account, amount, fees, **kwargs):
        """
        Create a deposit channel via ionBlock

        Args:
            domain: VHostDomain object
            account: Account object
            amount: Deposit amount in base currency (USD)
            fees: Fee amount
            **kwargs: Additional parameters (currency, etc.)

        Returns:
            Tuple of (status_code, api_return_data, provider_tx)
            - status_code: -2 (internal pending - requires UI rendering)
            - api_return_data: Dict with channel details for UI
            - provider_tx: ProviderTX object

        Raises:
            ValueError: If amount is invalid or configuration missing
        """
        # Validate amount
        if amount <= 0:
            raise ValueError("Amount must be greater than 0")

        # Get vhost
        vhost = account.vhost

        # Get ionBlock configuration
        try:
            config = IonBlockParameter.objects.get(vhost=vhost)
        except IonBlockParameter.DoesNotExist:
            raise ValueError(
                "ionBlock is not configured for this vhost. "
                "Please configure API credentials in admin panel."
            )

        if not config.is_active:
            raise ValueError("ionBlock is currently disabled for this vhost")

        # Get cryptocurrency (default to ETH if not specified)
        crypto_symbol = kwargs.get('currency', config.default_sender_currency)
        try:
            crypto_obj = CryptoCurrency.objects.get(
                vhost=vhost,
                symbol=crypto_symbol
            )
        except CryptoCurrency.DoesNotExist:
            raise ValueError(f"Cryptocurrency {crypto_symbol} not found for this vhost")
        network = False
        if crypto_obj.exchange_network:
                network = crypto_obj.exchange_network
        if not network:
            network = config.default_network
        # Initialize API client
        api_client = IonBlockAPIClient(
            api_key=config.api_key,
            api_secret=config.api_secret,
            base_url=config.api_endpoint
        )

        # Create ProviderTX record (before calling ionBlock API)
        provider_tx = ProviderTX(
            vhost=vhost,
            domain=domain,
            account=account,
            provider="cashier.providers.ionBlock",
            status='1',  # TX Created
            type="DEPOSIT",
            amount=amount,
            pending=amount,
            fees=fees,
            provider_fees=Decimal('0'),  # ionBlock handles fees via exchange rate
            cryp1=crypto_obj,
            is_fiat=False,
            active=True,
            completed=False,
            provider_data={
                'network': network,
                'sender_currency': crypto_symbol,
                'receiver_currency': config.receiver_currency
            }
        )
        provider_tx.save()

        # Generate reference using ProviderTX UUID
        reference = str(provider_tx.uuid)
        customer_reference = str(account.uuid)
        try:
            # Create ionBlock channel
            channel_data = api_client.create_channel(
                sender_currency=crypto_symbol,
                network=network,
                receiver_currency=config.receiver_currency,
                receiver_amount=float(amount),
                customer_reference=customer_reference,
                reference=reference,
            )

            logger.info(
                f"Created ionBlock channel {channel_data['channel_id']} "
                f"for account {account.uuid}: {amount} {config.receiver_currency}"
            )

        except Exception as e:
            logger.error(f"Failed to create ionBlock channel: {e}")
            # Mark ProviderTX as failed
            provider_tx.status = '103'  # Expired w/o payment
            provider_tx.active = False
            provider_tx.save()
            raise ValueError(f"Failed to create payment channel: {str(e)}")

        # Create IonBlockChannel record
        ionblock_channel = IonBlockChannel(
            vhost=vhost,
            account=account,
            channel_id=channel_data['channel_id'],
            channel_type='IN',
            status=channel_data.get('status', 1),
            address=channel_data['address'],
            sender_currency=channel_data['sender_currency'],
            sender_amount=Decimal(str(channel_data['sender_amount'])),
            network=network,
            receiver_currency=channel_data['receiver_currency'],
            receiver_amount=Decimal(str(channel_data['receiver_amount'])),
            receiver_reference=reference,
            sender_rate=Decimal(str(channel_data.get('sender_rate', 0))),
            valid_until=channel_data.get('valid_until'),
            provider_tx=provider_tx,
            is_blocked=channel_data.get('is_blocked', False),
            customer_reference=channel_data.get('customer_reference'),
            ionblock_data=channel_data
        )
        ionblock_channel.save()

        # Update ProviderTX with channel details
        provider_tx.status = '2'  # Unpaid
        provider_tx.hot_wallet = channel_data['address']
        provider_tx.provider_data.update({
            'channel_id': channel_data['channel_id'],
            'sender_amount': channel_data['sender_amount'],
            'sender_rate': channel_data.get('sender_rate'),
            'valid_until': channel_data.get('valid_until')
        })
        provider_tx.save()

        # Calculate expiry time
        expiry_timestamp = channel_data.get('valid_until')
        expiry_datetime = None
        if expiry_timestamp:
            from datetime import datetime
            expiry_datetime = datetime.fromtimestamp(expiry_timestamp)

        # Calculate proper exchange rate (USD per ETH)
        # receiver_amount is USD tokens, sender_amount is ETH
        # So rate = USD / ETH = how many USD per 1 ETH
        sender_amount_float = float(channel_data['sender_amount'])
        receiver_amount_float = float(channel_data['receiver_amount'])

        if sender_amount_float > 0:
            calculated_rate = receiver_amount_float / sender_amount_float
        else:
            calculated_rate = 0

        # Format amounts for display
        # USD amounts: 2 decimal places
        # Crypto amounts: keep full precision from ionBlock
        receiver_amount_formatted = f"{receiver_amount_float:.2f}"

        # Build API return data for UI rendering
        api_return = {
            "uuid": str(provider_tx.uuid),
            "provider": "cashier.providers.ionBlock",
            "channel_id": channel_data['channel_id'],
            "address": channel_data['address'],
            "sender_currency": channel_data['sender_currency'],
            "sender_amount": str(channel_data['sender_amount']),  # Keep ionBlock's precision
            "network": network,
            "receiver_currency": channel_data['receiver_currency'],
            "receiver_amount": receiver_amount_formatted,  # Format USD to 2 decimals
            "exchange_rate": f"{calculated_rate:.2f}",  # Format exchange rate to 2 decimals
            "valid_until": expiry_timestamp,
            "expires_at": expiry_datetime.isoformat() if expiry_datetime else None,
            # "qr_code_data": f"{crypto_symbol.lower()}:{channel_data['address']}?amount={channel_data['sender_amount']}",
            "qr_code_data":channel_data['address'],
            "instructions": (
                f"Send exactly {channel_data['sender_amount']} {channel_data['sender_currency']} "
                f"to the address below. Your account will be credited with "
                f"{channel_data['receiver_amount']} {channel_data['receiver_currency']} "
                "once the transaction is confirmed."
            )
        }

        # Return status -2 (internal pending - requires UI rendering)
        # The Cashier engine will create a INTERNAL_PENDING_DEP ledger entry
        # and return this data to the frontend for display
        return -2, api_return, provider_tx
