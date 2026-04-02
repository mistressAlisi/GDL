from datetime import timezone, timedelta
from uuid import uuid4
from django.contrib import admin
from django.db import models

from account.models import Account
from cashier.models.base import AccountLevels
from licensemanager.models import AvailableApplication
from parameters.models import VHostDomain, VHost


class RAFConfiguration(models.Model):
    """
    RAF (Refer-A-Friend) Configuration per VHost/VDomain
    Configures reward percentages, caps, and rollover requirements
    """
    uuid = models.UUIDField(default=uuid4, primary_key=True)
    vhost = models.ForeignKey(VHost, on_delete=models.CASCADE)
    vdomain = models.ForeignKey(VHostDomain, on_delete=models.CASCADE, null=True, blank=True)

    # Reward settings
    reward_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, default=50,
        help_text="Percentage of referred player's first deposit to reward (e.g., 50 = 50%)"
    )
    max_reward_per_referral = models.DecimalField(
        max_digits=12, decimal_places=2, default=500,
        help_text="Maximum reward amount per single referral"
    )
    max_reward_per_month = models.DecimalField(
        max_digits=12, decimal_places=2, default=1000,
        help_text="Maximum total rewards a referrer can earn per month"
    )

    # Rollover requirements
    rollover_multiplier = models.IntegerField(
        default=1,
        help_text="Rollover multiplier for bonus (e.g., 3 = 3x rollover)"
    )

    # Expiration
    reward_expiry_days = models.IntegerField(
        default=14,
        help_text="Days until bonus expires"
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "RAF Configuration"
        verbose_name_plural = "RAF Configurations"
        unique_together = ['vhost', 'vdomain']

    def __str__(self):
        domain_str = f" ({self.vdomain.domain_fqdn})" if self.vdomain else ""
        return f"RAF Config: {self.vhost.name}{domain_str} - {self.reward_percentage}%"


class AccountReferralCodeTracker(models.Model):
    uuid = models.UUIDField(default=uuid4,primary_key=True)
    vhost = models.ForeignKey(VHost,on_delete=models.CASCADE)
    vdomain = models.ForeignKey(VHostDomain,on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    referrer = models.ForeignKey(Account, on_delete=models.CASCADE,related_name='referrer')
    new_player = models.ForeignKey(Account, on_delete=models.CASCADE,related_name='new_player')
    type = models.TextField(blank=True)

    # RAF tracking fields
    first_deposit_processed = models.BooleanField(default=False, help_text="Whether RAF reward has been processed for first deposit")
    first_deposit_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, help_text="Amount of the first deposit")
    reward_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, help_text="RAF reward amount credited to referrer")
    reward_paid_at = models.DateTimeField(null=True, blank=True, help_text="When the RAF reward was paid")


class RAFRewardTracker(models.Model):
    """
    Tracks individual RAF rewards for reporting and audit purposes
    """
    uuid = models.UUIDField(default=uuid4, primary_key=True)
    vhost = models.ForeignKey(VHost, on_delete=models.CASCADE)
    vdomain = models.ForeignKey(VHostDomain, on_delete=models.CASCADE, null=True, blank=True)

    # Participants
    referrer = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='raf_referrer')
    referred = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='raf_referred')
    referral_tracker = models.ForeignKey(AccountReferralCodeTracker, on_delete=models.CASCADE, null=True, blank=True)

    # Transaction details
    deposit_amount = models.DecimalField(max_digits=12, decimal_places=2, help_text="Referred player's deposit amount")
    reward_amount = models.DecimalField(max_digits=12, decimal_places=2, help_text="Reward credited to referrer")

    # Timing
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    # Status
    is_paid = models.BooleanField(default=False)
    paid_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "RAF Reward Tracker"
        verbose_name_plural = "RAF Reward Trackers"

    def __str__(self):
        return f"RAF: {self.referrer.acctname} <- {self.referred.acctname} (${self.reward_amount})"


@admin.register(RAFConfiguration)
class RAFConfigurationAdmin(admin.ModelAdmin):
    list_display = ['vhost', 'vdomain', 'reward_percentage', 'max_reward_per_referral', 'rollover_multiplier', 'is_active']
    list_filter = ['vhost', 'is_active']


@admin.register(AccountReferralCodeTracker)
class AccountReferralCodeTrackerAdmin(admin.ModelAdmin):
    list_display = ['referrer', 'new_player', 'first_deposit_processed', 'reward_amount', 'created_at']
    list_filter = ["vhost","vdomain","referrer","new_player", "first_deposit_processed"]


@admin.register(RAFRewardTracker)
class RAFRewardTrackerAdmin(admin.ModelAdmin):
    list_display = ['referrer', 'referred', 'deposit_amount', 'reward_amount', 'is_paid', 'created_at']
    list_filter = ['vhost', 'is_paid']
