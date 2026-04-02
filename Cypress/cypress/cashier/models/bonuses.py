from datetime import timezone, timedelta
from uuid import uuid4

from django.contrib import admin
from django.db import models


from cashier.models.base import AccountLevels
from parameters.models import VHostDomain, VHost
from sports.models import Sport, Group



class CommonBonusInfo(models.Model):
    class Meta:
        abstract = True
    ROLLOVER_TYPES = (('D','Deposits Only'),('B','Bonus Only'),('DB','Deposit and Bonus'))
    uuid = models.UUIDField(primary_key=True, default=uuid4)
    vhost = models.ForeignKey(VHost, on_delete=models.CASCADE,null=True)
    vdomains = models.ManyToManyField(VHostDomain,blank=True)
    name = models.TextField(verbose_name="Bonus Level Name")
    active = models.BooleanField(default=True)
    is_fiat = models.BooleanField(default=False, verbose_name="This is a FIAT BONUS Level")
    level = models.ForeignKey(AccountLevels, on_delete=models.CASCADE,blank=True,null=True)
    description = models.TextField(verbose_name="Bonus Level Description Description")
    min_deposit = models.IntegerField(default=0, verbose_name="Minimum Deposit to trigger Bonus")
    reward_deposit = models.IntegerField(default=0, verbose_name="Bonus Reward deposit")
    deposit_multiplier = models.DecimalField(default=1, verbose_name="Deposit Multiplier Default is (1x)",decimal_places=4,max_digits=12)
    bonus_deposit_stc = models.IntegerField(default=0, verbose_name="Bonus Deposit Static (ie, without multiplier) - instead of Deposit multiplier above.")
    max_reward_amount = models.IntegerField(default=500, verbose_name="Maximum Reward Amount Allowed per bonus type")
    max_deposit_count = models.IntegerField(default=1,verbose_name="Maximum Deposit Count per bonus type allowed (For Deposit bonus modules)")
    rollover = models.IntegerField(default=5, verbose_name="Rollover Deposit Multiplier (default is 5x)")
    rollover_type = models.CharField(max_length=2, choices=ROLLOVER_TYPES, verbose_name="Rollover Type",default="DB")
    time_limit = models.IntegerField(default=25200, verbose_name="Time Limit to fulfill bonus (in seconds) Default is 7 days")
    min_bet = models.IntegerField(verbose_name="Rollover Minimum Bet Qualifier (Default is 0)", default=0)
    groups = models.ManyToManyField(Group,verbose_name="Sports to apply this Rollover to (May be blank for all)",blank=True)
    sports = models.ManyToManyField(Sport, verbose_name="Leagues to apply this Rollover to (May be blank for all)", blank=True)

    def __str__(self):
        return f"Bonus: {self.name}"

class AccountLevelActivationBonus(CommonBonusInfo):
    ACTIVATION_TYPES = (('tel','Telegram'),('what','WhatsApp'),('sms','SMS/MMS'),('eml','E-Mail'))
    validate_mobile_type = models.TextField(verbose_name="Mobile Type Validation Level",choices=ACTIVATION_TYPES)

    def __str__(self):
        if self.is_fiat:
            return f"Account FIAT Level Activation Bonus: {self.level.name}: {self.name} - {self.description}"
        else:
            return f"Account Level Activation Bonus: {self.level.name}: {self.name} - {self.description}"

@admin.register(AccountLevelActivationBonus)
class AccountLevelActivationBonusAdmin(admin.ModelAdmin):
    list_filter = ["active","level__vhost","is_fiat"]
    search_filter = ["vhost","name"]


class AccountLoosingWagerBonus(CommonBonusInfo):
    wager_count = models.IntegerField(default=1, verbose_name="Wager Count (default is 1)")
    def __str__(self):
        if self.is_fiat:
            return f"Account Loosing Wager Bonus: {self.level.name}: {self.name} - {self.description}"
        else:
            return f"Account Loosing Wager Bonus: {self.level.name}: {self.name} - {self.description}"

@admin.register(AccountLoosingWagerBonus)
class AccountLoosingWagerBonusAdmin(admin.ModelAdmin):
    list_filter = ["active","level__vhost","is_fiat"]
    search_filter = ["vhost","name"]

class GenericInternalBonus(CommonBonusInfo):
    slug = models.SlugField(verbose_name="Bonus Slug",unique=True)
    def __str__(self):
        return f"Generic Internal Bonus: {self.slug} - {self.name}"


@admin.register(GenericInternalBonus)
class GenericInternalBonusAdmin(admin.ModelAdmin):
    list_filter = ["active","level__vhost","is_fiat"]
    search_filter = ["vhost","name"]



class AccountDepositBonus(CommonBonusInfo):
    second_deposit_multiplier = models.DecimalField(default=1, verbose_name="Deposit Multiplier Default is (1x) for SECOND DEPOSIT",
                                             decimal_places=4, max_digits=12)
    third_deposit_multiplier = models.DecimalField(default=1, verbose_name="Deposit Multiplier Default is (1x) for THIRD DEPOSIT",
                                             decimal_places=4, max_digits=12)
    def __str__(self):
        if self.is_fiat:
            return f"Account Deposit Bonus: {self.level.name}: {self.name} - {self.description}"
        else:
            return f"Account Deposit Bonus: {self.level.name}: {self.name} - {self.description}"

@admin.register(AccountDepositBonus)
class AccountDepositBonusAdmin(admin.ModelAdmin):
    list_filter = ["active","level__vhost","is_fiat"]
    search_filter = ["vhost","name"]



class AccountPromoCodeBonus(CommonBonusInfo):
    promo_code = models.TextField(verbose_name="Promotion Code",unique=True)
    max_uses = models.IntegerField(verbose_name="Max Uses",default=0)
    expires_on = models.DateTimeField(null=True,blank=True)
    level = models.ForeignKey(AccountLevels, on_delete=models.CASCADE,null=True,blank=True)
    set_to_manager = models.ForeignKey('management.Manager', on_delete=models.SET_NULL, related_name="promocode_set", null=True,
                                       help_text="When selected, this Promocode will set the account that uses it to this manager.",
                                       verbose_name="Promocode: Set to Manager", blank=True)
    def __str__(self):
        if self.is_fiat:
            return f"FIAT PromoCode  Bonus: {self.name} - {self.description}"
        else:
            return f"PromoCode Bonus: {self.name} - {self.description}"

@admin.register(AccountPromoCodeBonus)
class AccountPromoCodeBonusAdmin(admin.ModelAdmin):
    list_filter = ["active","is_fiat"]
    search_filter = ["vhost","name","promocode"]


class AccountBonusStateTracker(models.Model):
    class Meta:
        verbose_name_plural = "Account Bonus State Trackers"
    uuid = models.UUIDField(primary_key=True,default=uuid4)
    vhost = models.ForeignKey(VHost,on_delete=models.CASCADE,null=True,blank=True)
    account = models.ForeignKey('account.Account',on_delete=models.CASCADE)
    domain = models.ForeignKey('parameters.VHostDomain', on_delete=models.CASCADE, null=True)
    wager = models.ForeignKey('wager.Wager',on_delete=models.CASCADE,null=True,blank=True)
    bonus_obj_type = models.TextField(null=True,blank=True)
    bonus_obj_uuid = models.UUIDField(null=True,blank=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(null=True,blank=True)
    is_fiat = models.BooleanField(default=False, verbose_name="This is a FIAT BONUS Level")
    wagers_lost = models.IntegerField(verbose_name="Wager Count",default=0)
    current_deposit = models.DecimalField(verbose_name="Current Deposit",decimal_places=2,max_digits=12,default=0)
    min_deposit = models.IntegerField(default=0, verbose_name="Minimum Deposit to trigger Bonus")
    reward_deposit = models.IntegerField(default=0, verbose_name="Bonus Reward deposit")
    deposit_multiplier = models.IntegerField(default=1, verbose_name="Deposit Multiplier")
    second_deposit_multiplier = models.DecimalField(default=1, verbose_name="Deposit Multiplier Default is (1x) for SECOND DEPOSIT",
                                             decimal_places=4, max_digits=12)
    third_deposit_multiplier = models.DecimalField(default=1, verbose_name="Deposit Multiplier Default is (1x) for THIRD DEPOSIT",
                                             decimal_places=4, max_digits=12)
    deposit_count = models.IntegerField(default=0, verbose_name="Deposit Count")
    rollover = models.IntegerField(default=5, verbose_name="Rollover Deposit PCT (default is 5x)")
    rollover_type = models.CharField(max_length=2, choices=CommonBonusInfo.ROLLOVER_TYPES, verbose_name="Rollover Type",default="DB")
    rollover_amount = models.DecimalField(decimal_places=2, max_digits=10, verbose_name="Rollover Amount Total",default=0)
    rollover_completed = models.DecimalField(decimal_places=2, max_digits=10, verbose_name="Rollover Completed Amount",default=0)
    rollover_complete = models.BooleanField(default=False)
    time_limit = models.IntegerField(default=25200, verbose_name="Time Limit to fulfill bonus (in seconds) Default is 7 days")
    min_bet = models.IntegerField(verbose_name="Rollover Minimum Bet Qualifier (Default is 0)", default=0)
    groups = models.ManyToManyField(Group,verbose_name="Sports to apply this Rollover to (May be blank for all)",blank=True)
    sports = models.ManyToManyField(Sport, verbose_name="Leagues to apply this Rollover to (May be blank for all)", blank=True)
    def __str__(self):
        return f"Activation Bonus State Tracker: {self.account.acctnum} @ {self.vhost}: {self.bonus_obj_type}:{str(self.bonus_obj_uuid)}"

@admin.register(AccountBonusStateTracker)
class AccountBonusStateTrackerAdmin(admin.ModelAdmin):
    list_filter = ["active","vhost","account"]
    search_filter = ["vhost","name"]


class AccountBonusStateHistory(models.Model):
    class Meta:
        verbose_name_plural = "Account Bonus State Histories"
    uuid = models.UUIDField(primary_key=True,default=uuid4)
    parent = models.ForeignKey(AccountBonusStateTracker,on_delete=models.SET_NULL,null=True,blank=True)
    vhost = models.ForeignKey(VHost, on_delete=models.CASCADE, null=True, blank=True)
    account = models.ForeignKey('account.Account',on_delete=models.CASCADE)
    bonus_obj_type = models.TextField(null=True, blank=True)
    bonus_obj_uuid = models.UUIDField(null=True, blank=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(null=True,blank=True)
    finished_at = models.DateTimeField(null=True,blank=True)
    is_fiat = models.BooleanField(default=False, verbose_name="This is a FIAT BONUS Level")
    vhost = models.ForeignKey(VHost,on_delete=models.CASCADE,null=True)
    wagers_lost = models.IntegerField(verbose_name="Wager Count",default=0)
    current_deposit = models.DecimalField(verbose_name="Current Deposit", decimal_places=2, max_digits=12, default=0)

    max_wagers_lost = models.IntegerField(verbose_name="Maximum Lost Wager Count",default=1)
    min_deposit = models.IntegerField(default=0, verbose_name="Minimum Deposit to trigger Bonus")
    reward_deposit = models.IntegerField(default=0, verbose_name="Bonus Reward deposit")
    deposit_multiplier = models.IntegerField(default=1, verbose_name="Deposit Multiplier")
    rollover = models.IntegerField(default=5, verbose_name="Rollover Deposit PCT (default is 5x)")
    rollover_type = models.CharField(max_length=2, choices=CommonBonusInfo.ROLLOVER_TYPES, verbose_name="Rollover Type",default="DB")
    rollover_amount = models.DecimalField(decimal_places=2, max_digits=10, verbose_name="Rollover Amount Total",
                                          default=0)
    rollover_completed = models.DecimalField(decimal_places=2, max_digits=10, verbose_name="Rollover Completed Amount",
                                             default=0)
    rollover_complete = models.BooleanField(default=False)

    min_bet = models.IntegerField(verbose_name="Rollover Minimum Bet Qualifier (Default is 0)", default=0)
    groups = models.ManyToManyField(Group,verbose_name="Sports to apply this Rollover to (May be blank for all)",blank=True)
    sports = models.ManyToManyField(Sport, verbose_name="Leagues to apply this Rollover to (May be blank for all)", blank=True)
    def __str__(self):
        return f"Activation Bonus State History: {self.account.acctnum} @ {self.vhost}: {self.bonus_obj_type}:{str(self.bonus_obj_uuid)}"


@admin.register(AccountBonusStateHistory)
class AccountBonusStateHistoryAdmin(admin.ModelAdmin):
    list_filter = ["active","vhost","account"]
    search_filter = ["vhost","name"]

