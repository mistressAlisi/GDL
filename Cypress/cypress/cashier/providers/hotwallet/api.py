import json
import requests
from decimal import Decimal
from typing import Optional, Dict, Any, List

from parameters.models import VHostParameterRegistry


class EthereumNodeClient:
    """
    JSON-RPC client for communicating with an Ethereum node.
    Handles all ETH node interactions for the Hot Wallet payment provider.
    """

    rpc_endpoint = None
    vhost = None
    request_id = 0

    def __init__(self, vhost, **kwargs):
        """
        Initialize the Ethereum node client.

        Args:
            vhost: The virtual host object
            **kwargs: Additional configuration options
        """
        self.vhost = vhost
        self.rpc_endpoint = VHostParameterRegistry.objects.get_or_create(
            vhost=self.vhost,
            application="cashier.providers.hotwallet",
            name="rpc_endpoint"
        )[0].value_text

        if not self.rpc_endpoint:
            self.rpc_endpoint = "http://localhost:8545"  # Default fallback

    def _make_request(self, method: str, params: List[Any] = None) -> Dict[str, Any]:
        """
        Make a JSON-RPC request to the Ethereum node.

        Args:
            method: The RPC method name (e.g., 'eth_blockNumber')
            params: List of parameters for the method

        Returns:
            The result from the JSON-RPC response

        Raises:
            Exception: If the RPC call returns an error
        """
        if params is None:
            params = []

        self.request_id += 1

        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": self.request_id
        }

        headers = {
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(
                self.rpc_endpoint,
                data=json.dumps(payload),
                headers=headers,
                timeout=30
            )
            response.raise_for_status()

            result = response.json()

            if "error" in result:
                error_msg = result["error"].get("message", "Unknown error")
                error_code = result["error"].get("code", -1)
                raise Exception(f"RPC Error ({error_code}): {error_msg}")

            return result.get("result")

        except requests.RequestException as e:
            raise Exception(f"Failed to connect to Ethereum node: {str(e)}")

    # Block and Network Methods

    def eth_blockNumber(self) -> int:
        """
        Get the current block number.

        Returns:
            Current block number as integer
        """
        result = self._make_request("eth_blockNumber")
        return int(result, 16)

    def eth_getBlockByNumber(self, block_number: int, full_transactions: bool = False) -> Dict:
        """
        Get block information by block number.

        Args:
            block_number: Block number to fetch
            full_transactions: If True, returns full transaction objects

        Returns:
            Block information dictionary
        """
        block_hex = hex(block_number)
        return self._make_request("eth_getBlockByNumber", [block_hex, full_transactions])

    def eth_chainId(self) -> int:
        """
        Get the chain ID (1 for mainnet, 11155111 for Sepolia, etc.)

        Returns:
            Chain ID as integer
        """
        result = self._make_request("eth_chainId")
        return int(result, 16)

    # Balance Methods

    def eth_getBalance(self, address: str, block: str = "latest") -> Decimal:
        """
        Get the ETH balance of an address in Wei.

        Args:
            address: Ethereum address (0x prefixed)
            block: Block parameter (default: "latest")

        Returns:
            Balance in Wei as Decimal
        """
        if not address.startswith("0x"):
            address = "0x" + address

        result = self._make_request("eth_getBalance", [address, block])
        return Decimal(int(result, 16))

    def wei_to_eth(self, wei: Decimal) -> Decimal:
        """
        Convert Wei to ETH.

        Args:
            wei: Amount in Wei

        Returns:
            Amount in ETH
        """
        return wei / Decimal(10 ** 18)

    def eth_to_wei(self, eth: Decimal) -> Decimal:
        """
        Convert ETH to Wei.

        Args:
            eth: Amount in ETH

        Returns:
            Amount in Wei
        """
        return Decimal(eth) * Decimal(10 ** 18)

    # Transaction Methods

    def eth_getTransactionByHash(self, tx_hash: str) -> Optional[Dict]:
        """
        Get transaction details by transaction hash.

        Args:
            tx_hash: Transaction hash (0x prefixed)

        Returns:
            Transaction details dictionary or None if not found
        """
        if not tx_hash.startswith("0x"):
            tx_hash = "0x" + tx_hash

        return self._make_request("eth_getTransactionByHash", [tx_hash])

    def eth_getTransactionReceipt(self, tx_hash: str) -> Optional[Dict]:
        """
        Get transaction receipt (includes confirmation status, gas used, etc.)

        Args:
            tx_hash: Transaction hash (0x prefixed)

        Returns:
            Transaction receipt dictionary or None if not mined yet
        """
        if not tx_hash.startswith("0x"):
            tx_hash = "0x" + tx_hash

        return self._make_request("eth_getTransactionReceipt", [tx_hash])

    def eth_getTransactionCount(self, address: str, block: str = "latest") -> int:
        """
        Get the nonce (transaction count) for an address.
        Used when sending transactions.

        Args:
            address: Ethereum address (0x prefixed)
            block: Block parameter (default: "latest")

        Returns:
            Nonce as integer
        """
        if not address.startswith("0x"):
            address = "0x" + address

        result = self._make_request("eth_getTransactionCount", [address, block])
        return int(result, 16)

    def eth_sendRawTransaction(self, signed_tx: str) -> str:
        """
        Broadcast a signed transaction to the network.

        Args:
            signed_tx: Signed transaction hex (0x prefixed)

        Returns:
            Transaction hash
        """
        if not signed_tx.startswith("0x"):
            signed_tx = "0x" + signed_tx

        return self._make_request("eth_sendRawTransaction", [signed_tx])

    # Gas Methods

    def eth_gasPrice(self) -> int:
        """
        Get the current gas price in Wei.

        Returns:
            Gas price in Wei as integer
        """
        result = self._make_request("eth_gasPrice")
        return int(result, 16)

    def eth_estimateGas(self, transaction: Dict) -> int:
        """
        Estimate gas required for a transaction.

        Args:
            transaction: Transaction object with to, from, value, data, etc.

        Returns:
            Estimated gas as integer
        """
        return int(self._make_request("eth_estimateGas", [transaction]), 16)

    def eth_maxPriorityFeePerGas(self) -> int:
        """
        Get the current max priority fee per gas (EIP-1559).

        Returns:
            Max priority fee in Wei as integer
        """
        result = self._make_request("eth_maxPriorityFeePerGas")
        return int(result, 16)

    def eth_feeHistory(self, block_count: int, newest_block: str = "latest",
                       reward_percentiles: List[int] = None) -> Dict:
        """
        Get historical gas fee data (EIP-1559).

        Args:
            block_count: Number of blocks to fetch
            newest_block: Newest block (default: "latest")
            reward_percentiles: List of percentile values (0-100)

        Returns:
            Fee history data
        """
        if reward_percentiles is None:
            reward_percentiles = [25, 50, 75]

        return self._make_request("eth_feeHistory", [
            hex(block_count),
            newest_block,
            reward_percentiles
        ])

    # Utility Methods

    def eth_call(self, transaction: Dict, block: str = "latest") -> str:
        """
        Execute a read-only contract call (does not create a transaction).

        Args:
            transaction: Transaction object with to, data, etc.
            block: Block parameter (default: "latest")

        Returns:
            Result data as hex string
        """
        return self._make_request("eth_call", [transaction, block])

    def get_transaction_confirmations(self, tx_hash: str) -> Optional[int]:
        """
        Get the number of confirmations for a transaction.

        Args:
            tx_hash: Transaction hash

        Returns:
            Number of confirmations or None if not mined
        """
        receipt = self.eth_getTransactionReceipt(tx_hash)
        if not receipt or not receipt.get("blockNumber"):
            return None

        tx_block = int(receipt["blockNumber"], 16)
        current_block = self.eth_blockNumber()

        return current_block - tx_block + 1

    def is_transaction_successful(self, tx_hash: str) -> Optional[bool]:
        """
        Check if a transaction was successful.

        Args:
            tx_hash: Transaction hash

        Returns:
            True if successful, False if failed, None if not mined
        """
        receipt = self.eth_getTransactionReceipt(tx_hash)
        if not receipt:
            return None

        # Status: 0x1 = success, 0x0 = failure
        status = receipt.get("status")
        if status is None:
            return None

        return int(status, 16) == 1
