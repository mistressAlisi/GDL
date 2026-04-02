from decimal import Decimal
from django.utils.timezone import now

from cashier.models import (
    CashierVDomainParameters,
    ProviderTX,
    CryptoCurrency,
    EthereumWallet
)
from cashier.providers.hotwallet.api import EthereumNodeClient
from cashier.providers.hotwallet.wallets import WalletManager


class DepositProvider(object):
    """
    Handles ETH deposit creation by generating unique hot wallets per deposit.
    """

    def create_deposit(self, domain, account, amount, fees, **kwargs):
        """
        Create a new Ethereum deposit by generating a unique hot wallet.

        Args:
            domain: VHostDomain object
            account: Account object
            amount: Deposit amount in ETH
            fees: Calculated fees
            **kwargs: Additional parameters (currency, etc.)

        Returns:
            Tuple of (status_code, api_return_data, provider_tx_object)
            - status_code: -2 (pending internal deposit)
            - api_return_data: Dict with wallet address and deposit info
            - provider_tx_object: ProviderTX database object

        Raises:
            ValueError: If amount is invalid
        """
        # Validate amount
        if amount <= 0:
            raise ValueError("amount must be > 0")
        if amount > 100:  # Max from PAYMENT_PROVIDER_INFO
            raise ValueError("amount must be <= 100 ETH")

        # Get Ethereum currency object
        cryptoParams = CashierVDomainParameters.objects.get_or_create(
            vhost=account.vhost
        )[0]

        if "currency" in kwargs:
            currency_uuid = kwargs["currency"]
        else:
            # Default to ETH - need to ensure ETH exists in CryptoCurrencies
            currency_uuid = self._get_or_create_eth_currency(account.vhost)

        crypto_obj = CryptoCurrency.objects.get(uuid=currency_uuid)

        # Validate this is actually ETH
        if crypto_obj.symbol.upper() != "ETH":
            raise ValueError("Hot Wallet provider only supports ETH deposits")

        # Initialize wallet manager and generate new wallet
        wallet_manager = WalletManager(account.vhost)
        address, private_key = wallet_manager.generate_wallet()
        encrypted_private_key = wallet_manager.encrypt_private_key(private_key)

        # Create ProviderTX object
        provider_tx = ProviderTX(
            vhost=account.vhost,
            domain=domain,
            account=account,
            provider="cashier.providers.hotwallet",
            status='1',  # TX Created
            type="DEPOSIT",
            amount=amount,
            pending=amount,
            fees=fees,
            provider_fees=0,  # Gas fees paid by sender
            is_fiat=False,
            cryp1=crypto_obj,
            hot_wallet=address,
            url="",  # No external URL needed
            provider_data={
                "address": address,
                "amount_eth": str(amount),
                "amount_wei": str(int(Decimal(amount) * Decimal(10 ** 18))),
                "created_at": now().isoformat()
            },
            invoice_data={
                "client_id": str(account.uuid),
                "vhost_id": str(account.vhost.uuid),
                "amount": str(amount),
                "currency": str(currency_uuid),
            }
        )
        provider_tx.save()

        # Create EthereumWallet record
        eth_wallet = EthereumWallet(
            vhost=account.vhost,
            account=account,
            address=address,
            encrypted_private_key=encrypted_private_key,
            provider_tx=provider_tx,
            is_active=True,
            deposit_received=False
        )
        eth_wallet.save()

        # Initialize node client to get current block
        try:
            node_client = EthereumNodeClient(account.vhost)
            current_block = node_client.eth_blockNumber()
            eth_wallet.last_checked_block = current_block
            eth_wallet.save()
        except Exception as e:
            # If node is not available, we'll start from 0
            print(f"Warning: Could not connect to ETH node: {e}")

        # Build API return data for UI rendering
        api_return = {
            "uuid": str(provider_tx.uuid),
            "provider": str(provider_tx.provider),
            "currency": str(crypto_obj.uuid),
            "currency_symbol": crypto_obj.symbol,
            "currency_name": crypto_obj.name,
            "hot_wallet": address,
            "amount": str(amount),
            "amount_eth": str(amount),
            "amount_wei": str(int(Decimal(amount) * Decimal(10 ** 18))),
            "network": "Ethereum Mainnet",
            "chain_id": 1,
            "instructions": (
                f"Send exactly {amount} ETH to the address below. "
                "Your deposit will be credited after 12 block confirmations."
            ),
            "qr_data": address,  # For QR code generation
            "expires": None,  # ETH wallets don't expire
        }

        # Construct Majestic iframe URL if configured
        if cryptoParams.majestic_iframe_base_url and cryptoParams.majestic_merchant_key:
            # Determine payment method endpoint (can be overridden via kwargs)
            payment_method = kwargs.get('payment_method', 'pp')  # Default to PayPal
            endpoint_map = {
                'apl': '/ap/live.php',   # Apple Pay
                'pyl': '/pp/live.php',   # PayPal
                'crd': '/cc/live.php',   # Credit/Debit Cards
                'pp': '/pp/live.php'     # Default PayPal
            }
            endpoint = endpoint_map.get(payment_method, '/pp/live.php')

            majestic_url = f"{cryptoParams.majestic_iframe_base_url}{endpoint}"
            majestic_url += f"?wallet={address}"  # Use the generated wallet address
            majestic_url += f"&playerid={account.uuid}"
            majestic_url += f"&key={cryptoParams.majestic_merchant_key}"
            majestic_url += f"&txid={provider_tx.uuid}"  # Transaction ID for tracking
            api_return["majestic_url"] = majestic_url

        # Return -2 status code to trigger internal payment UI rendering
        # The UI will display the wallet address and QR code for the user
        return -2, api_return, provider_tx

    def _get_or_create_eth_currency(self, vhost):
        """
        Get or create the ETH cryptocurrency record.

        Args:
            vhost: VHost object

        Returns:
            UUID of ETH currency
        """
        eth_currency, created = CryptoCurrency.objects.get_or_create(
            vhost=vhost,
            symbol="ETH",
            defaults={
                "name": "Ethereum",
                "active": True
            }
        )
        return eth_currency.uuid
