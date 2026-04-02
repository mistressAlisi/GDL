"""
ionBlock API Client
Handles authentication and API requests to ionBlock gateway
"""
import hashlib
import hmac
import time
import json
import requests
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class IonBlockAPIClient:
    """
    Client for interacting with ionBlock API

    Authentication uses HMAC-SHA512 signatures with:
    - X-Crypto-Key: API access key
    - X-Crypto-Nonce: Unique, incrementing 64-bit integer
    - X-Crypto-Signature: HMAC-SHA512(secret, uri_path + nonce + SHA256(request_data))
    """

    BASE_URL = "https://gateway.ionblock.io"

    def __init__(self, api_key: str, api_secret: str, base_url: str = None):
        """
        Initialize the ionBlock API client

        Args:
            api_key: X-Crypto-Key (hex-digit string)
            api_secret: 64-character Base62 secret
            base_url: Optional custom API endpoint URL (defaults to production)
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = base_url or self.BASE_URL
        self.session = requests.Session()

    def _generate_nonce(self) -> int:
        """
        Generate a unique nonce using microsecond-precision UNIX timestamp

        Returns:
            64-bit unsigned integer
        """
        # Use microseconds for uniqueness
        return int(time.time() * 1_000_000)

    def _calculate_signature(self, uri_path: str, nonce: str, request_params: Dict) -> str:
        """
        Calculate HMAC-SHA512 signature for API request

        Following ionBlock's specification:
        1. Convert params to JSON string (or "[]" if empty)
        2. Calculate SHA256 hash of JSON bytes
        3. Create message: uri_path + nonce + hash
        4. Calculate HMAC-SHA512 of message

        Args:
            uri_path: API endpoint path (e.g., "/v1/channels")
            nonce: Request nonce as string
            request_params: Request parameters dict

        Returns:
            Hex-encoded signature string
        """
        # Convert params to JSON (following ionBlock's exact format)
        if len(request_params) > 0:
            request_json = json.dumps(request_params, separators=(',', ':'))
        else:
            request_json = "[]"

        # Calculate SHA256 hash of JSON bytes
        request_hash = hashlib.sha256(request_json.encode('utf-8')).hexdigest()

        # Construct message: uri_path + nonce + hash
        message = uri_path.encode('utf-8') + nonce.encode('utf-8') + request_hash.encode('utf-8')

        # Calculate HMAC-SHA512
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            message,
            hashlib.sha512
        ).hexdigest()

        return signature

    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None
    ) -> Dict:
        """
        Make authenticated request to ionBlock API

        Args:
            method: HTTP method (GET, POST)
            endpoint: API endpoint (e.g., "/v1/channels/")
            params: Request parameters

        Returns:
            Response JSON as dict

        Raises:
            requests.HTTPError: On API error
        """
        url = f"{self.base_url}{endpoint}"
        nonce = str(self._generate_nonce())

        # Prepare request params
        if params is None:
            params = {}

        # Calculate signature (using params dict, not encoded string)
        signature = self._calculate_signature(endpoint, nonce, params)

        # Prepare headers
        headers = {
            'Accept': 'application/json',
            'X-Crypto-Key': self.api_key,
            'X-Crypto-Nonce': nonce,
            'X-Crypto-Signature': signature
        }

        # Make request
        try:
            timeout = 30  # 30 second timeout

            # Convert params to JSON for request body
            request_json = json.dumps(params, separators=(',', ':')) if params else "[]"

            if method.upper() == 'POST':
                # For POST, send JSON data
                headers['Content-Type'] = 'application/json'
                response = self.session.post(url, headers=headers, data=request_json, timeout=timeout)
            elif method.upper() == 'GET':
                response = self.session.get(url, headers=headers, params=params, timeout=timeout)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            response.raise_for_status()
            result = response.json()

            logger.info(f"ionBlock API {method} {endpoint}: {result.get('message', 'Success')}")
            return result

        except requests.exceptions.Timeout:
            logger.error(f"ionBlock API timeout after {timeout}s: {method} {endpoint}")
            raise ValueError(f"ionBlock API request timed out. Please try again.")
        except requests.exceptions.RequestException as e:
            logger.error(f"ionBlock API error: {e}")
            logger.error(f"URL: {url}")
            logger.error(f"Method: {method}")
            logger.error(f"Request JSON: {request_json}")
            logger.error(f"Nonce: {nonce}")
            logger.error(f"Signature: {signature}")
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    logger.error(f"Error details: {error_data}")
                except:
                    logger.error(f"Error response: {e.response.text}")
            raise

    def create_channel(
        self,
        sender_currency: str,
        network: str,
        receiver_currency: str,
        receiver_amount: float,
        reference: str,
        customer_reference: str
    ) -> Dict:
        """
        Create a deposit channel (payment address)

        Args:
            sender_currency: Cryptocurrency user will send (e.g., "ETH", "BTC")
            network: Blockchain network (e.g., "ETH", "BTC")
            receiver_currency: Currency we receive (e.g., "USD")
            receiver_amount: Amount we expect to receive
            customer_reference: Our internal reference ID - will also be sent as reference.

        Returns:
            Channel data including deposit address
            {
                "channel_id": 13010,
                "address": "0x...",
                "sender_amount": "0.123",
                "valid_until": 1655821347,
                ...
            }
        """
        # All params must be strings as per ionBlock specification
        params = {
            'receiver_currency': receiver_currency,
            'customer_reference': customer_reference,
            'reference':reference,
            'sender_currency': sender_currency,
            'network': network,
            'receiver_amount': str(receiver_amount)  # Convert to string
        }

        response = self._make_request('POST', '/v1/channels', params)

        if response.get('status') != 1:
            raise Exception(f"Failed to create channel: {response.get('message')}")

        return response.get('payload', {})

    def send_money_async(
        self,
        currency: str,
        amount: float,
        address: str,
        sender_currency: str,
        network: str,
        reference: str
    ) -> Dict:
        """
        Create an async withdrawal/payout transaction

        Args:
            currency: Currency we're sending from (e.g., "USD")
            amount: Amount in sender currency
            address: Destination crypto address
            sender_currency: Cryptocurrency to send (e.g., "ETH", "BTC")
            network: Blockchain network (e.g., "ETH", "BTC")
            reference: Our internal reference ID

        Returns:
            Transaction data
            {
                "transaction_id": 72,
                "receiver_amount": 0.00068823,
                "address": "0x...",
                "txid": null,  # Populated when broadcast
                ...
            }
        """
        # All params must be strings as per ionBlock specification
        params = {
            'currency': currency,
            'amount': str(amount),  # Convert to string
            'address': address,
            'sender_currency': sender_currency,
            'network': network,
            'reference': reference
        }

        response = self._make_request('POST', '/v1/send_money_async', params)

        if response.get('status') != 1:
            raise Exception(f"Failed to create withdrawal: {response.get('message')}")

        return response.get('payload', {})

    def get_channel_transactions(self, channel_id: int) -> Dict:
        """
        Get channel details and transactions

        Args:
            channel_id: ionBlock channel ID

        Returns:
            Channel data with transactions
            {
                "channel_id": 67,
                "type": "IN",
                "status": 1,  # 1=Pending, 2=Confirmed, 3=Expired
                "receiver_reference": "ABC994",
                "receiver_currency": "USD",
                "receiver_amount": 100,
                "address": "0x...",
                "sender_currency": "ETH",
                "sender_amount": "0.0479",
                "network": "ETH",
                "sender_rate": 2086.5,
                "valid_until": 1575988400,
                "is_blocked": false,
                "created_at": 1575987500,
                "txs": {
                    "data": []
                }
            }
        """
        response = self._make_request('GET', f'/v1/channels/{channel_id}/txs')

        if response.get('status') != 1:
            raise Exception(f"Failed to get channel: {response.get('message')}")

        return response.get('payload', {})

    def verify_webhook_signature(
        self,
        callback_id: str,
        request_body: str,
        received_signature: str
    ) -> bool:
        """
        Verify webhook signature from ionBlock

        Formula: HMAC-SHA512(secret, callback_id + SHA256(request_body))

        Args:
            callback_id: X-Crypto-Callback-Id from webhook headers
            request_body: Raw JSON request body
            received_signature: X-Crypto-Signature from webhook headers

        Returns:
            True if signature is valid
        """
        # Calculate SHA256 of request body
        request_hash = hashlib.sha256(request_body.encode('utf-8')).hexdigest().lower()

        # Construct message: callback_id + SHA256(request_body)
        message = f"{callback_id}{request_hash}"

        # Calculate expected signature
        expected_signature = hmac.new(
            self.api_secret.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha512
        ).hexdigest()

        # Constant-time comparison
        return hmac.compare_digest(expected_signature, received_signature)
