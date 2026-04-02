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
from cashier.models.sepawithdrawrequest import SepaWithdrawRequest

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
        # Validate amount
        print("TEST 3")
        if amount <= 0:
            raise ValueError("Amount must be greater than 0")

        # Get vhost
        vhost = account.vhost

        # Get cryptocurrency and network
        # For ERC20 withdrawals: currency=USD, sender_currency=ETH, network=ERC20
        crypto_symbol = kwargs.get('currency', 'EUR')  # User receives ETH
        network = kwargs.get('network', 'SEPA')  # ERC20 network identifier

        wd_data = kwargs.get('wd_data')

        try:
            crypto_obj = CryptoCurrency.objects.get(
                vhost=vhost,
                symbol=crypto_symbol
            )
        except CryptoCurrency.DoesNotExist:
            raise ValueError(f"Cryptocurrency {crypto_symbol} not found for this vhost")
        print("TEST 4")
        # Create ProviderTX record (before calling ionBlock API)
        provider_tx = ProviderTX(
            vhost=vhost,
            domain=domain,
            account=account,
            provider="cashier.providers.sepa",
            status='1',  # TX Created
            type="WITHDRAWAL",
            amount=amount,
            pending=amount,
            fees=fees,
            provider_fees=Decimal('0'),  # ionBlock handles fees via exchange rate
            cryp1=crypto_obj,
            is_fiat=True,
            active=True,
            completed=False,
            provider_data={
                'network': network,
                'sender_currency': crypto_symbol,
                'receiver_currency': 'EUR',
            }
        )
        provider_tx.save()

        # Generate reference using ProviderTX UUID
        #reference = str(provider_tx.uuid)
        print("TEST 5")
        transaction_data = SepaWithdrawRequest(
            account=account,
            legal_name=wd_data["legalname"],
            iban_num=wd_data["iban"],
            amount=wd_data["amount"],
            vhost=vhost,
            domain=domain,
        )
        transaction_data.save()
        print('Creation TX UUID: ', transaction_data.uuid)
        # Update ProviderTX with transaction details
        provider_tx.status = '2'  # Unpaid (processing)
        provider_tx.provider_tx = transaction_data.uuid
        provider_tx.provider_data.update({
            'transaction_id': str(transaction_data.uuid),
            'receiver_amount': float(transaction_data.amount),
            'exchange_rate': float(kwargs.get('xchg')),
            'txid': str(transaction_data.uuid)
        })
        provider_tx.save()

        # Return status 0 (pending external payment)
        # The Cashier engine will:
        # 1. Deduct amount from user's available balance
        # 2. Create PENDING_WDL ledger entry
        # 3. Wait for confirmation (via webhook or polling)
        return 0, str(transaction_data.uuid)
