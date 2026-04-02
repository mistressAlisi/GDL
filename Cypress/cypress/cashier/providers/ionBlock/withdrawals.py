"""
ionBlock Withdrawal Provider
Handles cryptocurrency payouts to user addresses
"""
import logging
from decimal import Decimal
from django.utils.timezone import now

from cashier.models import (
    ProviderTX,
    IonBlockParameter,
    IonBlockTransaction,
    CryptoCurrency
)
from .api import IonBlockAPIClient

logger = logging.getLogger(__name__)


class WithdrawalProvider:
    """
    Handles withdrawal/payout creation via ionBlock

    Flow:
    1. User requests withdrawal with destination address
    2. Create ionBlock payout transaction via send_money_async
    3. Create database records (ProviderTX, IonBlockTransaction)
    4. ionBlock processes and broadcasts transaction
    5. Update status when transaction is confirmed
    """

    def create_withdrawal(self, domain, account, amount, fees, **kwargs):
        """
        Create a withdrawal (payout) via ionBlock

        Args:
            domain: VHostDomain object
            account: Account object
            amount: Withdrawal amount in base currency (USD)
            fees: Fee amount
            **kwargs: Additional parameters (currency, address, network)

        Returns:
            Tuple of (status_code, further_value)
            - status_code: 0 (pending external payment)
            - further_value: Transaction ID/reference

        Raises:
            ValueError: If amount, address invalid or configuration missing
        """
        print("INIT LOG")
        # Validate amount
        if amount <= 0:
            raise ValueError("Amount must be greater than 0")

        # Get destination address from kwargs
        destination_address = kwargs.get('address')
        if not destination_address:
            raise ValueError("Destination address is required for withdrawals")

        # Get vhost
        vhost = account.vhost

        # Get ionBlock configuration
        try:
            config = IonBlockParameter.objects.get(vhost=vhost)
        except IonBlockParameter.DoesNotExist:
            print("TEST FAIL IONBLOCK DNE")
            raise ValueError(
                "ionBlock is not configured for this vhost. "
                "Please configure API credentials in admin panel."
            )

        if not config.is_active:
            print("TEST FAIL IONBLOCK Disabled")
            raise ValueError("ionBlock is currently disabled for this vhost")

        # Get cryptocurrency and network
        # For ERC20 withdrawals: currency=USD, sender_currency=ETH, network=ERC20
        crypto_symbol = kwargs.get('currency', 'ETH')  # User receives ETH
        network = kwargs.get('network', 'ERC20')  # ERC20 network identifier

        try:
            crypto_obj = CryptoCurrency.objects.get(
                vhost=vhost,
                symbol=crypto_symbol
            )
        except CryptoCurrency.DoesNotExist:
            raise ValueError(f"Cryptocurrency {crypto_symbol} not found for this vhost")

        # Initialize API client
        api_client = IonBlockAPIClient(
            api_key=config.api_key,
            api_secret=config.api_secret,
            base_url=config.api_endpoint,
        )

        # Create ProviderTX record (before calling ionBlock API)
        provider_tx = ProviderTX(
            vhost=vhost,
            domain=domain,
            account=account,
            provider="cashier.providers.ionBlock",
            status='1',  # TX Created
            type="WITHDRAWAL",
            amount=amount,
            pending=amount,
            fees=fees,
            provider_fees=Decimal('0'),  # ionBlock handles fees via exchange rate
            cryp1=crypto_obj,
            is_fiat=False,
            active=True,
            completed=False,
            hot_wallet=destination_address,  # Store destination address
            provider_data={
                'network': network,
                'sender_currency': crypto_symbol,
                'receiver_currency': config.receiver_currency,
                'destination_address': destination_address
            }
        )
        provider_tx.save()

        # Generate reference using ProviderTX UUID
        reference = str(provider_tx.uuid)

        try:
            # Create ionBlock payout transaction
            # amount is already the crypto amount (ETH) after USD->crypto conversion in engine
            transaction_data = api_client.send_money_async(
                currency=crypto_symbol,  # What we're sending (ETH)
                amount=float(amount),  # Crypto amount (e.g., 0.036 ETH)
                address=destination_address,
                sender_currency=crypto_symbol,  # Same as currency for withdrawals
                network=network,
                reference=reference
            )

            logger.info(
                f"Created ionBlock withdrawal {transaction_data['transaction_id']} "
                f"for account {account.uuid}: {amount} {crypto_symbol} "
                f"to address {destination_address}"
            )

        except Exception as e:
            print("FAILED TO MAKE WITHDRAWAL")
            logger.error(f"Failed to create ionBlock withdrawal: {e}")
            # Mark ProviderTX as failed
            provider_tx.status = '103'  # Expired w/o payment
            provider_tx.active = False
            provider_tx.save()
            raise ValueError(f"Failed to create withdrawal: {str(e)}")

        # Create IonBlockTransaction record
        ionblock_transaction = IonBlockTransaction(
            vhost=vhost,
            account=account,
            transaction_id=transaction_data['transaction_id'],
            transaction_type='OUT',
            status='pending',
            txid=transaction_data.get('txid'),  # May be None initially
            address=transaction_data['address'],
            network=network,
            sender_currency=transaction_data['sender_currency'],
            sender_amount=Decimal(str(transaction_data['sender_amount'])),
            receiver_currency=transaction_data['receiver_currency'],
            receiver_amount=Decimal(str(transaction_data['receiver_amount'])),
            rate=Decimal(str(transaction_data.get('rate', 0))),
            reference=reference,
            customer_reference=transaction_data.get('customer_reference'),
            provider_tx=provider_tx,
            is_blocked=transaction_data.get('is_blocked', False),
            ionblock_data=transaction_data
        )
        ionblock_transaction.save()

        # Update ProviderTX with transaction details
        provider_tx.status = '2'  # Unpaid (processing)
        provider_tx.provider_tx = transaction_data['transaction_id']
        provider_tx.provider_data.update({
            'transaction_id': transaction_data['transaction_id'],
            'receiver_amount': transaction_data['receiver_amount'],
            'exchange_rate': transaction_data.get('rate'),
            'txid': transaction_data.get('txid')
        })
        provider_tx.save()

        # Return status 0 (pending external payment)
        # The Cashier engine will:
        # 1. Deduct amount from user's available balance
        # 2. Create PENDING_WDL ledger entry
        # 3. Wait for confirmation (via webhook or polling)
        return 0, str(provider_tx.uuid)
