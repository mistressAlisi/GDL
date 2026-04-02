import os
import secrets
from typing import Tuple, Dict, Any
from decimal import Decimal

from cryptography.fernet import Fernet
from eth_account import Account
from eth_account.signers.local import LocalAccount
from eth_utils import to_checksum_address

from parameters.models import VHostParameterRegistry


class WalletManager:
    """
    Manages Ethereum wallet operations including generation, encryption, and transaction signing.
    """

    def __init__(self, vhost):
        """
        Initialize the wallet manager.

        Args:
            vhost: The virtual host object
        """
        self.vhost = vhost
        self._encryption_key = None

    def _get_encryption_key(self) -> bytes:
        """
        Get or create the Fernet encryption key from VHostParameterRegistry.

        Returns:
            Encryption key as bytes
        """
        if self._encryption_key:
            return self._encryption_key

        key_param, created = VHostParameterRegistry.objects.get_or_create(
            vhost=self.vhost,
            application="cashier.providers.hotwallet",
            name="encryption_key"
        )

        if created or not key_param.value_text:
            # Generate new encryption key
            new_key = Fernet.generate_key()
            key_param.value_text = new_key.decode('utf-8')
            key_param.save()
            self._encryption_key = new_key
        else:
            self._encryption_key = key_param.value_text.encode('utf-8')

        return self._encryption_key

    def generate_wallet(self) -> Tuple[str, str]:
        """
        Generate a new Ethereum wallet (private key and address).

        Returns:
            Tuple of (address, private_key_hex)
            - address: Checksummed Ethereum address (0x prefixed)
            - private_key_hex: Private key as hex string (0x prefixed)
        """
        # Enable unaudited HD wallet features (needed for account creation)
        Account.enable_unaudited_hdwallet_features()

        # Generate a new account with cryptographically secure randomness
        account: LocalAccount = Account.create()

        address = account.address  # Already checksummed
        private_key_hex = account.key.hex()  # 0x prefixed

        return address, private_key_hex

    def encrypt_private_key(self, private_key: str) -> str:
        """
        Encrypt a private key for secure database storage.

        Args:
            private_key: Private key as hex string (with or without 0x prefix)

        Returns:
            Encrypted private key as base64 string
        """
        # Remove 0x prefix if present
        if private_key.startswith("0x"):
            private_key = private_key[2:]

        # Get encryption key
        key = self._get_encryption_key()
        fernet = Fernet(key)

        # Encrypt the private key
        encrypted = fernet.encrypt(private_key.encode('utf-8'))

        return encrypted.decode('utf-8')

    def decrypt_private_key(self, encrypted_private_key: str) -> str:
        """
        Decrypt a private key from database storage.

        Args:
            encrypted_private_key: Encrypted private key as base64 string

        Returns:
            Private key as hex string (0x prefixed)
        """
        # Get encryption key
        key = self._get_encryption_key()
        fernet = Fernet(key)

        # Decrypt the private key
        decrypted = fernet.decrypt(encrypted_private_key.encode('utf-8'))
        private_key = decrypted.decode('utf-8')

        # Ensure 0x prefix
        if not private_key.startswith("0x"):
            private_key = "0x" + private_key

        return private_key

    def get_account_from_private_key(self, private_key: str) -> LocalAccount:
        """
        Create an Account object from a private key.

        Args:
            private_key: Private key as hex string (with or without 0x prefix)

        Returns:
            LocalAccount object for signing transactions
        """
        if not private_key.startswith("0x"):
            private_key = "0x" + private_key

        return Account.from_key(private_key)

    def sign_transaction(self, transaction: Dict[str, Any], private_key: str) -> str:
        """
        Sign a transaction with a private key.

        Args:
            transaction: Transaction dictionary with the following fields:
                - nonce: Transaction nonce
                - gasPrice or maxFeePerGas/maxPriorityFeePerGas: Gas pricing
                - gas: Gas limit
                - to: Recipient address
                - value: Amount in Wei
                - data: Transaction data (default: '0x')
                - chainId: Chain ID (1 for mainnet)
            private_key: Private key to sign with (hex string)

        Returns:
            Signed transaction as hex string (0x prefixed)
        """
        account = self.get_account_from_private_key(private_key)

        # Sign the transaction
        signed_txn = account.sign_transaction(transaction)

        # Return raw transaction as hex
        return signed_txn.rawTransaction.hex()

    def build_eth_transfer_transaction(
        self,
        from_address: str,
        to_address: str,
        amount_wei: int,
        nonce: int,
        gas_price: int,
        gas_limit: int = 21000,
        chain_id: int = 1
    ) -> Dict[str, Any]:
        """
        Build a basic ETH transfer transaction.

        Args:
            from_address: Sender address
            to_address: Recipient address
            amount_wei: Amount to send in Wei
            nonce: Transaction nonce
            gas_price: Gas price in Wei
            gas_limit: Gas limit (default: 21000 for simple transfer)
            chain_id: Chain ID (default: 1 for mainnet)

        Returns:
            Transaction dictionary ready for signing
        """
        # Ensure addresses are checksummed
        from_address = to_checksum_address(from_address)
        to_address = to_checksum_address(to_address)

        transaction = {
            'nonce': nonce,
            'gasPrice': gas_price,
            'gas': gas_limit,
            'to': to_address,
            'value': amount_wei,
            'data': '0x',
            'chainId': chain_id
        }

        return transaction

    def build_eip1559_transaction(
        self,
        from_address: str,
        to_address: str,
        amount_wei: int,
        nonce: int,
        max_fee_per_gas: int,
        max_priority_fee_per_gas: int,
        gas_limit: int = 21000,
        chain_id: int = 1
    ) -> Dict[str, Any]:
        """
        Build an EIP-1559 transaction (post-London fork).

        Args:
            from_address: Sender address
            to_address: Recipient address
            amount_wei: Amount to send in Wei
            nonce: Transaction nonce
            max_fee_per_gas: Maximum total fee per gas in Wei
            max_priority_fee_per_gas: Maximum priority fee per gas in Wei
            gas_limit: Gas limit (default: 21000 for simple transfer)
            chain_id: Chain ID (default: 1 for mainnet)

        Returns:
            Transaction dictionary ready for signing
        """
        # Ensure addresses are checksummed
        from_address = to_checksum_address(from_address)
        to_address = to_checksum_address(to_address)

        transaction = {
            'nonce': nonce,
            'maxFeePerGas': max_fee_per_gas,
            'maxPriorityFeePerGas': max_priority_fee_per_gas,
            'gas': gas_limit,
            'to': to_address,
            'value': amount_wei,
            'data': '0x',
            'chainId': chain_id,
            'type': 2  # EIP-1559 transaction type
        }

        return transaction

    def validate_address(self, address: str) -> bool:
        """
        Validate an Ethereum address.

        Args:
            address: Address to validate

        Returns:
            True if valid, False otherwise
        """
        try:
            # This will raise an exception if invalid
            to_checksum_address(address)
            return True
        except (ValueError, TypeError):
            return False

    def get_address_from_private_key(self, private_key: str) -> str:
        """
        Derive the Ethereum address from a private key.

        Args:
            private_key: Private key as hex string

        Returns:
            Checksummed Ethereum address
        """
        account = self.get_account_from_private_key(private_key)
        return account.address


# Utility functions for external use

def generate_new_wallet(vhost) -> Dict[str, str]:
    """
    Generate a new wallet and return both address and encrypted private key.

    Args:
        vhost: The virtual host object

    Returns:
        Dictionary with 'address' and 'encrypted_private_key'
    """
    manager = WalletManager(vhost)
    address, private_key = manager.generate_wallet()
    encrypted_key = manager.encrypt_private_key(private_key)

    return {
        'address': address,
        'encrypted_private_key': encrypted_key
    }


def sign_and_send_transaction(
    vhost,
    encrypted_private_key: str,
    to_address: str,
    amount_eth: Decimal,
    rpc_client
) -> str:
    """
    Complete workflow: decrypt key, build transaction, sign, and broadcast.

    Args:
        vhost: The virtual host object
        encrypted_private_key: Encrypted private key from database
        to_address: Recipient address
        amount_eth: Amount in ETH
        rpc_client: EthereumNodeClient instance

    Returns:
        Transaction hash
    """
    manager = WalletManager(vhost)

    # Decrypt private key
    private_key = manager.decrypt_private_key(encrypted_private_key)

    # Get sender address
    from_address = manager.get_address_from_private_key(private_key)

    # Convert ETH to Wei
    amount_wei = int(rpc_client.eth_to_wei(amount_eth))

    # Get current nonce
    nonce = rpc_client.eth_getTransactionCount(from_address)

    # Get gas price
    gas_price = rpc_client.eth_gasPrice()

    # Get chain ID
    chain_id = rpc_client.eth_chainId()

    # Build transaction
    transaction = manager.build_eth_transfer_transaction(
        from_address=from_address,
        to_address=to_address,
        amount_wei=amount_wei,
        nonce=nonce,
        gas_price=gas_price,
        gas_limit=21000,
        chain_id=chain_id
    )

    # Sign transaction
    signed_tx = manager.sign_transaction(transaction, private_key)

    # Broadcast transaction
    tx_hash = rpc_client.eth_sendRawTransaction(signed_tx)

    return tx_hash


def sweep_hot_wallet_to_house(
    vhost,
    encrypted_private_key: str,
    hot_wallet_address: str,
    rpc_client
) -> Dict[str, Any]:
    """
    Sweep all ETH from hot wallet to house wallet.
    Transfers entire balance minus gas costs.

    Args:
        vhost: The virtual host object
        encrypted_private_key: Encrypted private key from database
        hot_wallet_address: Hot wallet address (for verification)
        rpc_client: EthereumNodeClient instance

    Returns:
        Dictionary with:
            - tx_hash: Transaction hash
            - amount_eth: Amount transferred in ETH
            - gas_cost_eth: Gas cost in ETH
            - house_wallet: Destination address
    """
    from parameters.models import VHostParameterRegistry

    manager = WalletManager(vhost)

    # Get house wallet address from parameters
    house_wallet_param = VHostParameterRegistry.objects.filter(
        vhost=vhost,
        application="cashier.providers.hotwallet",
        name="house_wallet_address"
    ).first()

    if not house_wallet_param or not house_wallet_param.value_text:
        raise ValueError("House wallet address not configured for this vhost")

    house_wallet_address = house_wallet_param.value_text

    # Decrypt private key
    private_key = manager.decrypt_private_key(encrypted_private_key)

    # Verify wallet address matches
    from_address = manager.get_address_from_private_key(private_key)
    if from_address.lower() != hot_wallet_address.lower():
        raise ValueError(f"Private key does not match wallet address: {hot_wallet_address}")

    # Get current balance
    balance_wei = rpc_client.eth_getBalance(from_address)
    balance_eth = rpc_client.wei_to_eth(balance_wei)

    if balance_wei == 0:
        raise ValueError(f"Hot wallet {from_address} has zero balance")

    # Get gas price and estimate costs
    gas_price = rpc_client.eth_gasPrice()
    gas_limit = 21000  # Standard ETH transfer
    gas_cost_wei = gas_price * gas_limit
    gas_cost_eth = rpc_client.wei_to_eth(Decimal(gas_cost_wei))

    # Calculate amount to send (balance - gas)
    amount_to_send_wei = int(balance_wei - gas_cost_wei)

    if amount_to_send_wei <= 0:
        raise ValueError(
            f"Insufficient balance to cover gas costs. "
            f"Balance: {balance_eth} ETH, Gas cost: {gas_cost_eth} ETH"
        )

    amount_to_send_eth = rpc_client.wei_to_eth(Decimal(amount_to_send_wei))

    # Get transaction parameters
    nonce = rpc_client.eth_getTransactionCount(from_address)
    chain_id = rpc_client.eth_chainId()

    # Build transaction
    transaction = manager.build_eth_transfer_transaction(
        from_address=from_address,
        to_address=house_wallet_address,
        amount_wei=amount_to_send_wei,
        nonce=nonce,
        gas_price=gas_price,
        gas_limit=gas_limit,
        chain_id=chain_id
    )

    # Sign transaction
    signed_tx = manager.sign_transaction(transaction, private_key)

    # Broadcast transaction
    tx_hash = rpc_client.eth_sendRawTransaction(signed_tx)

    return {
        'tx_hash': tx_hash,
        'amount_eth': float(amount_to_send_eth),
        'gas_cost_eth': float(gas_cost_eth),
        'house_wallet': house_wallet_address,
        'hot_wallet': from_address
    }
