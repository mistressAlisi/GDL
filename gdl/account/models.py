import uuid

from django.contrib import admin
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import UniqueConstraint, Q

# from cashier.models import AccountLevels
from parameters.models import Timezone, VHost, Locales, VHostDomain
from toolkit.string import random_string
from django.utils.translation import gettext_lazy as _



# Create your models here.
class   Account(models.Model):
    class Meta:
        permissions = [('view_all_accounts','Can view accounts from all users/agents'),('bulk_deposit_operations','Can use the Bulk Deposit/Withdraw Operations Tool')]
        unique_together = (('acctname','vhost'),('vhost','mobile'))
        constraints = [
            # email1 must be unique per vhost
            UniqueConstraint(
                fields=['vhost', 'email1'],
                condition=Q(email1__isnull=False),
                name='unique_email1_per_vhost'
            ),
            # email2 must be unique per vhost
            UniqueConstraint(
                fields=['vhost', 'email2'],
                condition=Q(email2__isnull=False),
                name='unique_email2_per_vhost'
            ),
            # Also keep your existing unique_together
            UniqueConstraint(fields=['acctname', 'vhost'], name='unique_acctname_per_vhost')
        ]

    def clean(self):
        super().clean()

        # Skip check if no vhost or both emails are empty
        if not self.vhost or not self.email1 and not self.email2:
            return ValidationError({"email1":"Primary Email is required.","email2":"Secondary Email is recommended"})

        # Build Q filters for other accounts in same vhost
        xor_filter = Q()
        if self.email1:
            xor_filter |= Q(email1=self.email1) | Q(email2=self.email1)
        if self.email2:
            xor_filter |= Q(email1=self.email2) | Q(email2=self.email2)

        # Exclude self if updating
        if self.pk:
            xor_filter &= ~Q(pk=self.pk)

        # Apply vhost constraint
        xor_filter &= Q(vhost=self.vhost)

        if Account.objects.filter(xor_filter).exists():
            raise ValidationError({"email1":"Either email1 or email2 already exists in another account in this service.","email2":"Either email1 or email2 already exists in another account in this service."})

    def save(self, *args, **kwargs):
        self.full_clean()  # enforce `clean()` before saving
        super().save(*args, **kwargs)


    uuid = models.UUIDField(primary_key=True,default=uuid.uuid4)
    acctnum = models.TextField(verbose_name="Account Number",default="100100",unique=True)
    acctname = models.CharField(verbose_name=_("Your Name"),max_length=100,blank=True,null=True)
    holder = models.TextField(verbose_name="Account Holder",blank=True,null=True,help_text="Optional, Account holder name.")
    pronouns = models.TextField(verbose_name=_("Your Pronouns"),blank=True,null=True)
    fday = models.DateField(verbose_name="Account Holder's Favourite Day",blank=True,null=True)
    avatar = models.ImageField(verbose_name="Avatar Image:",blank=True,null=True,upload_to="accounts/avatars/")
    secret = models.CharField(max_length=128,editable=False)
    secret_reminder = models.TextField(verbose_name="Secret Reminder Question",blank=True,null=True)
    secret_answer = models.TextField(verbose_name="Secret Answer Question",blank=True,null=True)
    phone_wager_pin = models.TextField(verbose_name="Phone Wager Pin",blank=True,null=True)
    created = models.DateTimeField(verbose_name="Account Created",auto_now_add=True)
    updated = models.DateTimeField(verbose_name="Account Updated",auto_now=True)
    activated = models.DateTimeField(verbose_name="Account Activated At",null=True,blank=True)
    vhost = models.ForeignKey(VHost, on_delete=models.CASCADE, verbose_name="Virtual Host", null=True, blank=True)
    domain = models.ForeignKey(VHostDomain, on_delete=models.CASCADE, verbose_name="Virtual Host Domain", null=True, blank=True)
    email1 = models.EmailField(verbose_name=_("Email 1"),blank=True,null=True,help_text=_("Your account is identified by your email."))
    email2 = models.EmailField(verbose_name=_("Email 2"),blank=True,null=True,help_text=_("Providing a secondary e-mail address is recommended for account recovery purposes! (Optional)"))
    credit_limit = models.DecimalField(verbose_name="Current Account Credit Limit", decimal_places=5, max_digits=20, default=0, blank=True)
    low_balance_alert = models.DecimalField(verbose_name="The balance at which an alert is sent to the account", max_digits=20, decimal_places=5, default=1000)
    min_wager = models.DecimalField(verbose_name="Min Wager Amount",help_text="All wagers must be equal or greater than this value.",default=100,decimal_places=5,max_digits=20)
    max_wager = models.DecimalField(verbose_name="Max Wager Amount",help_text="All wagers must be equal or less than this value.",default=1000,decimal_places=5,max_digits=20)
    wager_limit = models.DecimalField(verbose_name="Wager Limit",help_text="Maximum amount account can wager.",default=10000,decimal_places=5,max_digits=20)
    mobile = models.TextField(verbose_name=_("SMS/Mobile Number"), help_text=_("Your Mobile Number!"), blank=True, null=True)
    settle = models.DecimalField(verbose_name="Settle Balance at", decimal_places=5, max_digits=20, default=0, blank=True)
    active = models.BooleanField(default=False,help_text="Is this Account active? (Global enable) - FALSE by default for self-registration validation.")
    frozen = models.BooleanField(default=False,help_text="Is this Account Frozen/held?")
    can_place_wagers = models.BooleanField(default=True,help_text="Can this account place online wagers?",verbose_name="Enable/Disable All Wagering")
    can_place_phone_wagers = models.BooleanField(default=True,help_text="Can this account place phone wagers?",verbose_name="Enable Phone Wagers")
    can_use_sportsbook = models.BooleanField(default=True,help_text="Enable Sportsbook for Acct",verbose_name="Enable Sportsbook")
    timezone = models.ForeignKey(Timezone,verbose_name=_("Timezone"),on_delete=models.SET_NULL,null=True,blank=True)
    must_change_pw = models.BooleanField(default=True)
    use_rolling_balance = models.BooleanField(default=True,verbose_name="Use Rolling Balance",help_text="If enabled, the player balance will be rolled forward; without using the Settled balance amount.")
    must_set_tz = models.BooleanField(default=True)
    has_seen_intro_help = models.BooleanField(default=False)
    agent_transfer_blocked = models.BooleanField(default=False,verbose_name="Restrict Agent Transfer for this Account")
    available_invites = models.IntegerField(verbose_name="Available Invites",default=0)
    rules_package = models.UUIDField(verbose_name="Rules Package UUID",null=True,blank=True)
    locale = models.ForeignKey(Locales,verbose_name=_("Language"),on_delete=models.SET_NULL,null=True,blank=True)
    account_level = models.ForeignKey('cashier.AccountLevels',verbose_name="Account Level",on_delete=models.RESTRICT,null=True,blank=True)
    parlay_rules = models.ForeignKey('cashier.ParlayPayoutRuleset', verbose_name="Parlay Rules", on_delete=models.RESTRICT,
                                     null=True, blank=True)
    system_theme = models.ForeignKey('parameters.Theme',verbose_name="Game Skin",null=True,blank=True,on_delete=models.SET_NULL)
    sms_validated = models.BooleanField(default=False)
    telegram_validated = models.BooleanField(default=False)
    email_notifications = models.BooleanField(default=True)

    def current_balance(self):
        return self.available-self.at_risk

    def __str__(self):
        return f"Account: {self.acctnum}"

@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    pass

# class AccountLevelHistory(models.Model):
#     class Meta:
#         unique_together = (('account', 'level'),)
#     account = models.ForeignKey(Account,verbose_name="Account Level",on_delete=models.RESTRICT)
#     level = models.ForeignKey(AccountLevels,verbose_name="Account Level",on_delete=models.RESTRICT,null=True,blank=True)
#     activated_at = models.DateTimeField(verbose_name="Activated Date",auto_now=True)
#
#     def __str__(self):
#         return f"Account: {self.account.acctnum}, Level: {self.level.name}, Activated at: {self.activated_at}"
#
#
# @admin.register(AccountLevelHistory)
# class AccountLevelHistory(admin.ModelAdmin):
#     list_filter = ["account","level"]



class AccountEmailChanges(models.Model):
    class Meta:
        unique_together = ["account", "email1","email2"]
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    account = models.ForeignKey(Account,on_delete=models.CASCADE)
    email1 = models.EmailField(max_length=254,null=True,blank=True)
    email2 = models.EmailField(max_length=254,null=True,blank=True)
    created = models.DateTimeField(auto_now_add=True,verbose_name="Token Created at")
    expires = models.DateTimeField(verbose_name="Token Expires at")
    key = models.TextField(verbose_name="Activation Token Key")
    def __str__(self):
        return f"Email change request for {self.account.acctnum}"

@admin.register(AccountEmailChanges)
class AccountEmailChangesAdmin(admin.ModelAdmin):
    pass




class AccountActivationTokens(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    account = models.ForeignKey(Account,on_delete=models.CASCADE,verbose_name="Account")
    created =models.DateTimeField(auto_now_add=True,verbose_name="Token Created at")
    expires = models.DateTimeField(verbose_name="Token Expires at")
    key = models.TextField(verbose_name="Activation Token Key")
    def __str__(self):
        return f"Activation Token for Account {self.account.acctnum}: Created at {self.created}: Expires at: {self.expires}"

@admin.register(AccountActivationTokens)
class AccountActivationTokensAdmin(admin.ModelAdmin):
    list_filter = ["account","account__vhost"]


class AccountLockouts(models.Model):
    uuid = models.UUIDField(primary_key=True)
    account = models.ForeignKey(Account,on_delete=models.CASCADE,verbose_name="Account",related_name="account_lockouts")
    active = models.BooleanField(default=False,verbose_name="Lockout Active")
    created_at = models.DateTimeField(auto_now_add=True,verbose_name="Created at")
    expires = models.DateTimeField(verbose_name="Token Expires at",null=True,blank=True)
    system = models.BooleanField(default=False,verbose_name="System Lockout")
    self_lockout = models.BooleanField(default=False,verbose_name="Self Lockout")
    notes = models.TextField(verbose_name="Lockout Notes",default="")
    def __str__(self):
        return f"Account Lockout for Account {self.account.acctnum} in {self.account.vhost}"

@admin.register(AccountLockouts)
class AccountLockoutsAdmin(admin.ModelAdmin):
    list_filter = ["account", "account__vhost"]


