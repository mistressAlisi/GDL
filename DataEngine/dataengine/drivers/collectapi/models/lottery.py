import uuid
from django.contrib import admin
from django.db import models
from parameters.models import VHost


class LotteryType(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    vhost = models.ForeignKey(VHost, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    api_endpoint = models.CharField(max_length=200)
    checker_endpoint = models.CharField(max_length=200, null=True, blank=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('vhost', 'slug')
        
    def __str__(self):
        return f"{self.name} - {self.vhost}"


@admin.register(LotteryType)
class LotteryTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'vhost', 'active']
    list_filter = ['vhost', 'active']


class LotteryDraw(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    lottery_type = models.ForeignKey(LotteryType, on_delete=models.CASCADE, related_name='draws')
    draw_date = models.DateField()
    draw_datetime = models.DateTimeField(null=True, blank=True)
    draw_number = models.CharField(max_length=50, null=True, blank=True)
    
    # Winning numbers
    main_numbers = models.JSONField(default=list)  # Regular numbers
    bonus_numbers = models.JSONField(default=list)  # Powerball/Megaball
    multiplier = models.IntegerField(null=True, blank=True)  # Power Play/Megaplier
    
    # Jackpot info
    jackpot_amount = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    jackpot_currency = models.CharField(max_length=10, default='USD')
    next_jackpot = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    next_draw_date = models.DateField(null=True, blank=True)
    
    # Raw API response
    raw_response = models.JSONField(default=dict)
    
    # Metadata
    synced_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('lottery_type', 'draw_date')
        ordering = ['-draw_date']
        
    def __str__(self):
        return f"{self.lottery_type.name} - {self.draw_date}"


@admin.register(LotteryDraw)
class LotteryDrawAdmin(admin.ModelAdmin):
    list_display = ['lottery_type', 'draw_date', 'jackpot_amount', 'synced_at']
    list_filter = ['lottery_type', 'draw_date']
    search_fields = ['draw_number']


class LotteryTicketCheck(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    lottery_draw = models.ForeignKey(LotteryDraw, on_delete=models.CASCADE, related_name='ticket_checks')
    account = models.ForeignKey('account.Account', on_delete=models.CASCADE, null=True, blank=True)
    
    # User's ticket numbers
    user_main_numbers = models.JSONField(default=list)
    user_bonus_number = models.IntegerField(null=True, blank=True)
    user_multiplier = models.BooleanField(default=False)
    
    # Match results
    main_matches = models.IntegerField(default=0)
    bonus_match = models.BooleanField(default=False)
    prize_tier = models.CharField(max_length=50, null=True, blank=True)
    prize_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    is_winner = models.BooleanField(default=False)
    
    # Metadata
    checked_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    def __str__(self):
        return f"Ticket Check - {self.lottery_draw} - {'Winner' if self.is_winner else 'No Win'}"


@admin.register(LotteryTicketCheck)
class LotteryTicketCheckAdmin(admin.ModelAdmin):
    list_display = ['lottery_draw', 'account', 'is_winner', 'prize_amount', 'checked_at']
    list_filter = ['is_winner', 'lottery_draw__lottery_type']


class LotterySyncStatus(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    lottery_type = models.ForeignKey(LotteryType, on_delete=models.CASCADE)
    last_sync = models.DateTimeField()
    last_draw_date = models.DateField(null=True, blank=True)
    success = models.BooleanField(default=True)
    error_message = models.TextField(null=True, blank=True)
    sync_count = models.IntegerField(default=0)
    
    class Meta:
        unique_together = ('lottery_type',)
        
    def __str__(self):
        return f"Sync Status - {self.lottery_type.name} - {self.last_sync}"


@admin.register(LotterySyncStatus)
class LotterySyncStatusAdmin(admin.ModelAdmin):
    list_display = ['lottery_type', 'last_sync', 'last_draw_date', 'success', 'sync_count']
    list_filter = ['success', 'lottery_type']


class LotteryPayoutConfig(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    vhost = models.ForeignKey(VHost, on_delete=models.CASCADE)
    lottery_type = models.ForeignKey(LotteryType, on_delete=models.CASCADE)
    multiplier = models.IntegerField(default=10000, help_text="Payout multiplier for exact match (e.g., 10000 = 10,000x)")
    max_payout = models.DecimalField(max_digits=10, decimal_places=2, default=100000, help_text="Maximum payout amount")
    min_wager = models.DecimalField(max_digits=10, decimal_places=2, default=1, help_text="Minimum wager amount")
    max_wager = models.DecimalField(max_digits=10, decimal_places=2, default=100, help_text="Maximum wager amount")
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('vhost', 'lottery_type')
        
    def __str__(self):
        return f"Payout Config - {self.lottery_type.name} - {self.vhost}"


@admin.register(LotteryPayoutConfig)
class LotteryPayoutConfigAdmin(admin.ModelAdmin):
    list_display = ['lottery_type', 'vhost', 'multiplier', 'max_payout', 'active']
    list_filter = ['vhost', 'active', 'lottery_type']
