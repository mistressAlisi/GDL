from uuid import uuid4

from django.contrib import admin
from django.db import models


class EthereumWallet(models.Model):
    """
    Stores Ethereum hot wallet information.
    One wallet is generated per deposit transaction.
    """
    uuid = models.UUIDField(default=uuid4, primary_key=True)
    vhost = models.ForeignKey("parameters.VHost", on_delete=models.CASCADE)
    account = models.ForeignKey("account.Account", on_delete=models.CASCADE)

    # Wallet credentials
    address = models.CharField(
        max_length=42,
        unique=True,
        verbose_name="Ethereum Address",
        help_text="Checksummed Ethereum address (0x prefixed)"
    )
    encrypted_private_key = models.TextField(
        verbose_name="Encrypted Private Key",
        help_text="Fernet-encrypted private key for secure storage"
    )

    # Transaction tracking
    provider_tx = models.ForeignKey(
        "cashier.ProviderTX",
        on_delete=models.CASCADE,
        related_name="ethereum_wallets",
        help_text="Associated provider transaction for this deposit"
    )

    # Block tracking for deposit monitoring
    last_checked_block = models.BigIntegerField(
        default=0,
        verbose_name="Last Checked Block",
        help_text="Last block number checked for incoming transactions"
    )

    # Status tracking
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this wallet is actively monitoring for deposits"
    )
    deposit_received = models.BooleanField(
        default=False,
        help_text="Whether the expected deposit has been received"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    first_deposit_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Timestamp of first deposit received"
    )

    class Meta:
        verbose_name = "Ethereum Wallet"
        verbose_name_plural = "Ethereum Wallets"
        indexes = [
            models.Index(fields=['address']),
            models.Index(fields=['account', 'is_active']),
            models.Index(fields=['vhost', 'is_active']),
        ]

    def __str__(self):
        return f"ETH Wallet: {self.address} (Account: {self.account})"


@admin.register(EthereumWallet)
class EthereumWalletAdmin(admin.ModelAdmin):
    list_display = ['address', 'account', 'vhost', 'is_active', 'deposit_received', 'created_at']
    list_filter = ['vhost', 'is_active', 'deposit_received', 'created_at']
    search_fields = ['address', 'account__username']
    readonly_fields = ['uuid', 'created_at', 'updated_at', 'first_deposit_at']


class EthereumTransaction(models.Model):
    """
    Tracks individual Ethereum transactions detected on the blockchain.
    Multiple transactions can be associated with a single wallet.
    """
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('failed', 'Failed'),
    )

    uuid = models.UUIDField(default=uuid4, primary_key=True)
    vhost = models.ForeignKey("parameters.VHost", on_delete=models.CASCADE)

    # Transaction identifiers
    tx_hash = models.CharField(
        max_length=66,
        unique=True,
        verbose_name="Transaction Hash",
        help_text="Ethereum transaction hash (0x prefixed)"
    )

    # Transaction details
    from_address = models.CharField(
        max_length=42,
        verbose_name="From Address",
        help_text="Sender's Ethereum address"
    )
    to_address = models.CharField(
        max_length=42,
        verbose_name="To Address",
        help_text="Recipient's Ethereum address (our hot wallet)"
    )

    # Associated wallet (if this is an incoming deposit)
    wallet = models.ForeignKey(
        EthereumWallet,
        on_delete=models.CASCADE,
        related_name="transactions",
        null=True,
        blank=True,
        help_text="Associated hot wallet (for deposits)"
    )

    # Amount and fees
    amount_wei = models.DecimalField(
        max_digits=78,
        decimal_places=0,
        verbose_name="Amount in Wei",
        help_text="Transaction amount in Wei (1 ETH = 10^18 Wei)"
    )
    amount_eth = models.DecimalField(
        max_digits=30,
        decimal_places=18,
        verbose_name="Amount in ETH",
        help_text="Transaction amount in ETH"
    )
    gas_used = models.BigIntegerField(
        null=True,
        blank=True,
        verbose_name="Gas Used",
        help_text="Total gas used by the transaction"
    )
    gas_price = models.DecimalField(
        max_digits=78,
        decimal_places=0,
        null=True,
        blank=True,
        verbose_name="Gas Price in Wei",
        help_text="Gas price in Wei"
    )
    transaction_fee_wei = models.DecimalField(
        max_digits=78,
        decimal_places=0,
        null=True,
        blank=True,
        verbose_name="Transaction Fee in Wei",
        help_text="Total transaction fee (gas_used * gas_price)"
    )

    # Block information
    block_number = models.BigIntegerField(
        null=True,
        blank=True,
        verbose_name="Block Number",
        help_text="Block number where transaction was mined"
    )
    block_hash = models.CharField(
        max_length=66,
        null=True,
        blank=True,
        verbose_name="Block Hash"
    )
    confirmations = models.IntegerField(
        default=0,
        verbose_name="Confirmations",
        help_text="Number of block confirmations"
    )

    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="Transaction Status"
    )

    # Provider transaction link
    provider_tx = models.ForeignKey(
        "cashier.ProviderTX",
        on_delete=models.CASCADE,
        related_name="ethereum_transactions",
        null=True,
        blank=True,
        help_text="Associated provider transaction"
    )

    # Transaction metadata
    nonce = models.BigIntegerField(
        null=True,
        blank=True,
        verbose_name="Nonce",
        help_text="Transaction nonce"
    )
    transaction_index = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Transaction Index",
        help_text="Index of transaction in block"
    )
    input_data = models.TextField(
        blank=True,
        null=True,
        verbose_name="Input Data",
        help_text="Transaction input data (for contract calls)"
    )

    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="First Detected"
    )
    updated_at = models.DateTimeField(auto_now=True)
    confirmed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Confirmed At",
        help_text="When transaction reached required confirmations"
    )
    mined_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Mined At",
        help_text="Timestamp from the block"
    )

    class Meta:
        verbose_name = "Ethereum Transaction"
        verbose_name_plural = "Ethereum Transactions"
        indexes = [
            models.Index(fields=['tx_hash']),
            models.Index(fields=['to_address', 'status']),
            models.Index(fields=['wallet', 'status']),
            models.Index(fields=['block_number']),
            models.Index(fields=['status', 'confirmations']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"ETH TX: {self.tx_hash[:10]}... ({self.amount_eth} ETH) - {self.status}"

    def update_confirmations(self, current_block: int):
        """
        Update the number of confirmations based on current block.

        Args:
            current_block: Current blockchain block number
        """
        if self.block_number:
            self.confirmations = current_block - self.block_number + 1
            self.save(update_fields=['confirmations', 'updated_at'])


@admin.register(EthereumTransaction)
class EthereumTransactionAdmin(admin.ModelAdmin):
    list_display = [
        'tx_hash_short',
        'from_address_short',
        'to_address_short',
        'amount_eth',
        'status',
        'confirmations',
        'block_number',
        'created_at'
    ]
    list_filter = ['status', 'vhost', 'created_at']
    search_fields = ['tx_hash', 'from_address', 'to_address', 'wallet__address']
    readonly_fields = [
        'uuid',
        'created_at',
        'updated_at',
        'confirmed_at',
        'mined_at'
    ]

    def tx_hash_short(self, obj):
        return f"{obj.tx_hash[:10]}..." if obj.tx_hash else ""
    tx_hash_short.short_description = "TX Hash"

    def from_address_short(self, obj):
        return f"{obj.from_address[:10]}..." if obj.from_address else ""
    from_address_short.short_description = "From"

    def to_address_short(self, obj):
        return f"{obj.to_address[:10]}..." if obj.to_address else ""
    to_address_short.short_description = "To"


class EthereumNodeParameter(models.Model):
    """
    Stores Ethereum node configuration parameters per vhost.
    """
    uuid = models.UUIDField(default=uuid4, primary_key=True)
    vhost = models.OneToOneField(
        "parameters.VHost",
        on_delete=models.CASCADE,
        related_name="ethereum_config"
    )

    # Node configuration
    rpc_endpoint = models.URLField(
        max_length=500,
        verbose_name="RPC Endpoint",
        help_text="Ethereum node RPC endpoint URL"
    )
    chain_id = models.IntegerField(
        default=1,
        verbose_name="Chain ID",
        help_text="Ethereum network chain ID (1=mainnet, 11155111=sepolia)"
    )

    # Confirmation requirements
    required_confirmations = models.IntegerField(
        default=12,
        verbose_name="Required Confirmations",
        help_text="Number of block confirmations before accepting deposit"
    )

    # Monitoring configuration
    polling_interval_seconds = models.IntegerField(
        default=15,
        verbose_name="Polling Interval (seconds)",
        help_text="How often to check for new blocks/transactions"
    )

    # Gas configuration
    default_gas_limit = models.BigIntegerField(
        default=21000,
        verbose_name="Default Gas Limit",
        help_text="Default gas limit for ETH transfers"
    )
    gas_price_multiplier = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=1.1,
        verbose_name="Gas Price Multiplier",
        help_text="Multiplier for gas price (e.g., 1.1 = 10% above network rate)"
    )

    # Status
    is_active = models.BooleanField(
        default=True,
        verbose_name="Active",
        help_text="Whether Ethereum provider is active for this vhost"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Ethereum Node Configuration"
        verbose_name_plural = "Ethereum Node Configurations"

    def __str__(self):
        return f"ETH Config for {self.vhost} (Chain ID: {self.chain_id})"


@admin.register(EthereumNodeParameter)
class EthereumNodeParameterAdmin(admin.ModelAdmin):
    list_display = [
        'vhost',
        'chain_id',
        'required_confirmations',
        'is_active',
        'updated_at'
    ]
    list_filter = ['is_active', 'chain_id']
    readonly_fields = ['uuid', 'created_at', 'updated_at']
