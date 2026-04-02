# ionBlock Payment Provider

Cryptocurrency payment gateway integration for handling ETH and other digital asset deposits and withdrawals.

## Overview

The ionBlock provider enables users to deposit and withdraw cryptocurrency through the ionBlock gateway service. It supports:

- **Deposits**: Create unique payment channels with deposit addresses
- **Withdrawals**: Send cryptocurrency to user-specified addresses
- **Webhooks**: Real-time payment confirmations
- **Multiple Networks**: ETH, BTC, and other supported blockchains

## Architecture

```
athena/cashier/providers/ionBlock/
├── __init__.py           # Package marker
├── provider.py           # Provider configuration (PAYMENT_PROVIDER_INFO)
├── api.py                # API client with HMAC-SHA512 authentication
├── deposit.py            # DepositProvider - creates payment channels
├── withdrawals.py        # WithdrawalProvider - creates payouts
├── webhook.py            # Webhook handler for payment confirmations
└── README.md             # This file
```

## Database Models

### IonBlockParameter
Configuration table storing API credentials per VHost.

**Fields:**
- `api_key`: X-Crypto-Key (hex-digit API access key)
- `api_secret`: 64-character Base62 API secret
- `default_network`: Default blockchain network (ETH, BTC, etc.)
- `default_sender_currency`: Default cryptocurrency
- `receiver_currency`: Currency we receive (usually USD)
- `is_active`: Enable/disable ionBlock

**Location:** `athena/cashier/models/ionblock.py:IonBlockParameter`

### IonBlockChannel
Tracks deposit channels (unique payment addresses).

**Fields:**
- `channel_id`: ionBlock's channel ID
- `address`: Deposit address for user
- `sender_currency`: Cryptocurrency user sends
- `sender_amount`: Amount user needs to send
- `receiver_amount`: Amount we receive
- `status`: 1=Pending, 2=Confirmed, 3=Expired

**Location:** `athena/cashier/models/ionblock.py:IonBlockChannel`

### IonBlockTransaction
Tracks both deposit and withdrawal transactions.

**Fields:**
- `transaction_id`: ionBlock's transaction ID
- `transaction_type`: IN (deposit) or OUT (withdrawal)
- `txid`: Blockchain transaction hash
- `status`: pending, confirmed, failed, expired

**Location:** `athena/cashier/models/ionblock.py:IonBlockTransaction`

## API Authentication

ionBlock uses HMAC-SHA512 signatures for authentication:

### Request Headers
```
X-Crypto-Key: <api_key>
X-Crypto-Nonce: <unique_incrementing_integer>
X-Crypto-Signature: <hmac_sha512_signature>
```

### Signature Calculation
```
msg = uri_path + str(nonce) + sha256(request_data).lower()
signature = hmac_sha512(api_secret, msg)
```

### Webhook Signature Verification
```
msg = callback_id + sha256(request_body).lower()
expected_signature = hmac_sha512(api_secret, msg)
```

**Implementation:** `athena/cashier/providers/ionBlock/api.py:IonBlockAPIClient`

## Deposit Flow

### 1. User Initiates Deposit

**API Endpoint:** `POST /api/v1/cashier/deposit/validate`

**Request:**
```json
{
  "provider": "cashier.providers.ionBlock",
  "amount": 100,
  "currency": "ETH"
}
```

### 2. Create ionBlock Channel

**Provider Method:** `DepositProvider.create_deposit()`

**ionBlock API Call:** `POST https://gateway.ionblock.io/v1/channels/`

**Parameters:**
- `sender_currency`: ETH
- `network`: ETH
- `receiver_currency`: USD
- `receiver_amount`: 100
- `reference`: <ProviderTX UUID>

**Response:**
```json
{
  "status": 1,
  "payload": {
    "channel_id": 13010,
    "address": "0x123...",
    "sender_amount": "0.05",
    "sender_currency": "ETH",
    "valid_until": 1655821347
  }
}
```

### 3. Display to User

The frontend receives payment details:
- Deposit address
- Amount to send in crypto
- QR code data
- Expiration time

### 4. User Sends Crypto

User sends the exact amount of cryptocurrency to the provided address.

### 5. ionBlock Webhook Confirmation

**Webhook URL:** `POST /api/v1/cashier/webhooks/ionBlock/`

**Payload:**
```json
{
  "channel_id": 13010,
  "status": 2,
  "receiver_reference": "<ProviderTX UUID>",
  "sender_amount": 0.05,
  "sender_currency": "ETH",
  "receiver_amount": 100,
  "receiver_currency": "USD"
}
```

### 6. Credit Account

When `status == 2` (confirmed), the webhook handler:
1. Verifies signature
2. Updates channel and transaction records
3. Calls `Cashier.confirm_pending_deposit()`
4. Credits user's account balance

**Implementation:** `athena/cashier/providers/ionBlock/webhook.py:process_deposit_webhook`

## Withdrawal Flow

### 1. User Requests Withdrawal

**API Endpoint:** `POST /api/v1/cashier/withdraw/validate`

**Request:**
```json
{
  "provider": "cashier.providers.ionBlock",
  "amount": 50,
  "currency": "ETH",
  "address": "0xUserAddress...",
  "network": "ETH"
}
```

### 2. Create ionBlock Payout

**Provider Method:** `WithdrawalProvider.create_withdrawal()`

**ionBlock API Call:** `POST https://gateway.ionblock.io/v1/send_money_async/`

**Parameters:**
- `currency`: USD
- `amount`: 50
- `address`: 0xUserAddress...
- `sender_currency`: ETH
- `network`: ETH
- `reference`: <ProviderTX UUID>

**Response:**
```json
{
  "status": 1,
  "payload": {
    "transaction_id": 72,
    "receiver_amount": 0.025,
    "receiver_currency": "ETH",
    "address": "0xUserAddress...",
    "txid": null
  }
}
```

### 3. Deduct from Account

The Cashier engine:
1. Deducts amount from available balance
2. Creates PENDING_WDL ledger entry
3. Waits for confirmation

### 4. ionBlock Processes Transaction

ionBlock broadcasts the transaction to the blockchain.

### 5. Confirmation (Optional)

If ionBlock sends withdrawal webhooks, the system updates the transaction status to completed.

**Implementation:** `athena/cashier/providers/ionBlock/withdrawals.py:WithdrawalProvider`

## Configuration

### 1. Run Migration

```bash
cd athena
python manage.py migrate cashier
```

### 2. Create ionBlock Configuration

**Django Admin** → **Cashier** → **IonBlock Parameters**

Create a new entry:
- **VHost**: Select your vhost
- **API Key**: Your ionBlock X-Crypto-Key
- **API Secret**: Your 64-character Base62 secret
- **Default Network**: ETH (or BTC, etc.)
- **Default Sender Currency**: ETH
- **Receiver Currency**: USD
- **Is Active**: ✓

### 3. Register Provider

**Django Admin** → **Cashier** → **Payment Providers**

Create entry:
- **Name**: ionBlock Payment Provider
- **Module Name**: cashier.providers.ionBlock
- **Is Crypto**: ✓
- **Deposits**: ✓
- **Withdrawals**: ✓
- **Deposit Min**: 0.001
- **Deposit Max**: 100
- **Withdrawal Min**: 0.001
- **Withdrawal Max**: 50

### 4. Link to Domain

**Django Admin** → **Cashier** → **VDomain Payment Providers**

Create entry:
- **Payment Provider**: ionBlock Payment Provider
- **VDomain**: Select your domain
- **Active**: ✓

### 5. Configure Webhook URL

In your ionBlock dashboard, set the webhook callback URL:
```
https://yourdomain.com/api/v1/cashier/webhooks/ionBlock/
```

## Testing

### Test Deposit (Manual)

1. Configure ionBlock with testnet settings
2. Create deposit via API
3. Send test ETH to the generated address
4. Verify webhook is received
5. Check account balance is credited

### Test Withdrawal (Manual)

1. Have sufficient balance in account
2. Request withdrawal via API
3. Verify transaction is created in ionBlock
4. Check blockchain for transaction
5. Verify account balance is deducted

### Test Webhook Signature Verification

```python
from cashier.providers.ionBlock.api import IonBlockAPIClient

client = IonBlockAPIClient(api_key="your_key", api_secret="your_secret")

# Verify webhook signature
is_valid = client.verify_webhook_signature(
    callback_id="123",
    request_body='{"channel_id": 5, ...}',
    received_signature="abcdef..."
)
```

## Webhook Endpoint

**URL:** `POST /api/v1/cashier/webhooks/ionBlock/`

**Headers:**
- `X-Crypto-Callback-Id`: Unique callback ID
- `X-Crypto-Signature`: HMAC-SHA512 signature

**Authentication:** Signature verification using API secret

**CSRF:** Exempt (external webhook)

## Error Handling

### Deposit Errors

- **Invalid amount**: Raises `ValueError`
- **Missing configuration**: Raises `ValueError`
- **ionBlock API error**: Marks ProviderTX as failed (status 103)
- **Webhook signature invalid**: Returns 403 Forbidden

### Withdrawal Errors

- **Missing destination address**: Raises `ValueError`
- **Insufficient balance**: Handled by Cashier engine
- **ionBlock API error**: Marks ProviderTX as failed

## Security Considerations

1. **API Secrets**: Store securely, never commit to version control
2. **Webhook Signatures**: Always verify before processing
3. **Nonce Management**: Ensure nonces always increment
4. **HTTPS Only**: All API calls and webhooks use HTTPS
5. **Atomic Transactions**: Use database transactions to prevent double-crediting

## Logging

All operations log to the `cashier.providers.ionBlock` logger:

```python
import logging
logger = logging.getLogger(__name__)
```

**Log Levels:**
- INFO: Successful operations
- WARNING: Non-critical issues (e.g., duplicate webhook)
- ERROR: Failed operations
- EXCEPTION: Unexpected errors with stack traces

## API Reference

### IonBlockAPIClient

**Methods:**
- `create_channel()`: Create deposit channel
- `send_money_async()`: Create withdrawal
- `verify_webhook_signature()`: Verify webhook authenticity

### DepositProvider

**Methods:**
- `create_deposit(domain, account, amount, fees, **kwargs)`: Returns `(-2, api_return_data, provider_tx)`

### WithdrawalProvider

**Methods:**
- `create_withdrawal(domain, account, amount, fees, **kwargs)`: Returns `(0, transaction_id)`

## Troubleshooting

### Deposits Not Confirming

1. Check webhook endpoint is accessible from internet
2. Verify webhook signature verification logic
3. Check ionBlock dashboard for webhook delivery logs
4. Verify API credentials are correct

### Withdrawals Failing

1. Check ionBlock balance/limits
2. Verify destination address is valid
3. Check network parameter matches currency
4. Review ionBlock transaction logs

### Invalid Signature Errors

1. Verify API secret is correct
2. Check nonce is incrementing
3. Ensure request data encoding matches (UTF-8)
4. Verify SHA256 hash is lowercase hex

## File Locations

| Component | Location |
|-----------|----------|
| Provider Config | `athena/cashier/providers/ionBlock/provider.py` |
| API Client | `athena/cashier/providers/ionBlock/api.py` |
| Deposit Handler | `athena/cashier/providers/ionBlock/deposit.py` |
| Withdrawal Handler | `athena/cashier/providers/ionBlock/withdrawals.py` |
| Webhook Handler | `athena/cashier/providers/ionBlock/webhook.py` |
| Models | `athena/cashier/models/ionblock.py` |
| Migration | `athena/cashier/migrations/0038_ionblock_provider.py` |

## Support

For issues related to:
- **ionBlock API**: Contact ionBlock support
- **Provider Implementation**: Check logs and this documentation
- **Athena Integration**: Review Cashier engine documentation

## Version History

- **v1.0** (2025-11-13): Initial implementation
  - Deposit flow via payment channels
  - Withdrawal flow via send_money_async
  - Webhook signature verification
  - Database models and migrations
