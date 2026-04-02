"""
ionBlock Payment Provider Models
Tracks channels, transactions, and configuration for ionBlock integration
"""
from django.db import models
from django.contrib import admin
from uuid import uuid4
from decimal import Decimal


class IonBlockParameter(models.Model):
    """
    ionBlock API configuration per VHost
    Stores API credentials and settings
    """
    class Meta:
        db_table = 'cashier_ionblock_parameter'

    uuid = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    vhost = models.OneToOneField(
        "parameters.VHost",
        on_delete=models.CASCADE,
        related_name="ionblock_config"
    )

    # API Credentials
    api_key = models.TextField(
        help_text="X-Crypto-Key: Hex-digit API access key"
    )
    api_secret = models.TextField(
        help_text="64-character Base62 API secret (stored securely)"
    )
    api_endpoint = models.URLField(
        max_length=255,
        default='https://gateway.ionblock.io',
        help_text="ionBlock API endpoint URL"
    )

    # Configuration
    default_network = models.CharField(
        max_length=20,
        default='ETH',
        help_text="Default blockchain network (ETH, BTC, etc.)"
    )
    default_sender_currency = models.CharField(
        max_length=10,
        default='ETH',
        help_text="Default cryptocurrency for deposits/withdrawals"
    )
    receiver_currency = models.CharField(
        max_length=10,
        default='USD',
        help_text="Currency we receive (usually USD)"
    )

    # Settings
    channel_expiry_minutes = models.IntegerField(
        default=15,
        help_text="Minutes until deposit channel expires"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Enable/disable ionBlock for this vhost"
    )
    testnet = models.BooleanField(
        default=False,
        help_text="Use testnet for testing"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"ionBlock Config: {self.vhost}"


@admin.register(IonBlockParameter)
class IonBlockParameterAdmin(admin.ModelAdmin):
    """Django admin interface for ionBlock configuration"""
    list_display = ['vhost', 'default_network', 'default_sender_currency', 'receiver_currency', 'is_active', 'testnet', 'updated_at']
    list_filter = ['is_active', 'testnet', 'default_network']
    search_fields = ['vhost__name', 'api_key']
    readonly_fields = ['uuid', 'created_at', 'updated_at']
    fieldsets = (
        ('VHost', {
            'fields': ('vhost', 'is_active', 'testnet')
        }),
        ('API Configuration', {
            'fields': ('api_key', 'api_secret', 'api_endpoint')
        }),
        ('Currency & Network Settings', {
            'fields': ('default_network', 'default_sender_currency', 'receiver_currency', 'channel_expiry_minutes')
        }),
        ('Metadata', {
            'fields': ('uuid', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


class IonBlockChannel(models.Model):
    """
    Deposit channels (payment addresses) created via ionBlock
    Each channel is a unique deposit address for a user
    """
    class Meta:
        db_table = 'cashier_ionblock_channel'
        indexes = [
            models.Index(fields=['channel_id']),
            models.Index(fields=['address']),
            models.Index(fields=['status']),
        ]

    STATUS_CHOICES = (
        (1, 'Pending/Active'),
        (2, 'Confirmed/Completed'),
        (3, 'Expired/Failed'),
    )

    uuid = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    vhost = models.ForeignKey(
        "parameters.VHost",
        on_delete=models.CASCADE,
        related_name="ionblock_channels"
    )
    account = models.ForeignKey(
        "account.Account",
        on_delete=models.CASCADE,
        related_name="ionblock_channels"
    )

    # ionBlock channel data
    channel_id = models.BigIntegerField(
        unique=True,
        help_text="ionBlock's channel ID"
    )
    channel_type = models.CharField(
        max_length=10,
        default='IN',
        help_text="IN for deposits, OUT for withdrawals"
    )
    status = models.IntegerField(
        choices=STATUS_CHOICES,
        default=1,
        help_text="Channel status"
    )

    # Payment details
    address = models.CharField(
        max_length=255,
        db_index=True,
        help_text="Deposit address for user to send crypto"
    )
    sender_currency = models.CharField(
        max_length=10,
        help_text="Cryptocurrency user sends (ETH, BTC, etc.)"
    )
    sender_amount = models.DecimalField(
        max_digits=30,
        decimal_places=18,
        help_text="Amount user needs to send in crypto"
    )
    network = models.CharField(
        max_length=20,
        help_text="Blockchain network (ETH, BTC, etc.)"
    )

    # Receiver details (what we get)
    receiver_currency = models.CharField(
        max_length=10,
        help_text="Currency we receive (USD)"
    )
    receiver_amount = models.DecimalField(
        max_digits=30,
        decimal_places=10,
        help_text="Amount we receive"
    )
    receiver_reference = models.CharField(
        max_length=255,
        db_index=True,
        help_text="Our internal reference/ProviderTX UUID"
    )

    # Exchange rate
    sender_rate = models.DecimalField(
        max_digits=30,
        decimal_places=10,
        null=True,
        blank=True,
        help_text="Exchange rate at time of channel creation"
    )

    # Timestamps
    valid_until = models.BigIntegerField(
        null=True,
        blank=True,
        help_text="UNIX timestamp when channel expires"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)

    # Link to ProviderTX
    provider_tx = models.ForeignKey(
        "cashier.ProviderTX",
        on_delete=models.CASCADE,
        related_name="ionblock_channels",
        null=True,
        blank=True
    )

    # Additional data
    is_blocked = models.BooleanField(default=False)
    customer_reference = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Customer reference if provided"
    )
    ionblock_data = models.JSONField(
        default=dict,
        help_text="Raw data from ionBlock API"
    )

    def __str__(self):
        return f"Channel {self.channel_id}: {self.sender_amount} {self.sender_currency}"


class IonBlockTransaction(models.Model):
    """
    Tracks ionBlock transactions (both deposits and withdrawals)
    """
    class Meta:
        db_table = 'cashier_ionblock_transaction'
        indexes = [
            models.Index(fields=['transaction_id']),
            models.Index(fields=['txid']),
            models.Index(fields=['transaction_type']),
        ]

    TRANSACTION_TYPE_CHOICES = (
        ('IN', 'Deposit'),
        ('OUT', 'Withdrawal'),
    )

    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('failed', 'Failed'),
        ('expired', 'Expired'),
    )

    uuid = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    vhost = models.ForeignKey(
        "parameters.VHost",
        on_delete=models.CASCADE,
        related_name="ionblock_transactions"
    )
    account = models.ForeignKey(
        "account.Account",
        on_delete=models.CASCADE,
        related_name="ionblock_transactions"
    )

    # ionBlock transaction data
    transaction_id = models.BigIntegerField(
        null=True,
        blank=True,
        db_index=True,
        help_text="ionBlock's transaction ID (for withdrawals)"
    )
    transaction_type = models.CharField(
        max_length=3,
        choices=TRANSACTION_TYPE_CHOICES,
        help_text="IN for deposits, OUT for withdrawals"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    # Blockchain data
    txid = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        db_index=True,
        help_text="Blockchain transaction hash"
    )
    address = models.CharField(
        max_length=255,
        help_text="Crypto address (deposit address or withdrawal destination)"
    )
    network = models.CharField(
        max_length=20,
        help_text="Blockchain network"
    )

    # Amount details
    sender_currency = models.CharField(max_length=10)
    sender_amount = models.DecimalField(max_digits=30, decimal_places=18)
    receiver_currency = models.CharField(max_length=10)
    receiver_amount = models.DecimalField(max_digits=30, decimal_places=18)
    rate = models.DecimalField(
        max_digits=30,
        decimal_places=10,
        null=True,
        blank=True,
        help_text="Exchange rate"
    )

    # References
    reference = models.CharField(
        max_length=255,
        db_index=True,
        help_text="Our internal reference"
    )
    customer_reference = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )

    # Links
    channel = models.ForeignKey(
        IonBlockChannel,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="transactions",
        help_text="Associated channel (for deposits)"
    )
    provider_tx = models.ForeignKey(
        "cashier.ProviderTX",
        on_delete=models.CASCADE,
        related_name="ionblock_transactions",
        null=True,
        blank=True
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)

    # Flags
    is_blocked = models.BooleanField(default=False)

    # Raw data from ionBlock
    ionblock_data = models.JSONField(
        default=dict,
        help_text="Raw data from ionBlock API"
    )

    def __str__(self):
        return f"{self.transaction_type} Transaction {self.transaction_id}: {self.sender_amount} {self.sender_currency}"
