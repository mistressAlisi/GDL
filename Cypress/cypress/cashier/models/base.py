import uuid
from uuid import uuid4

from django.contrib import admin
from django.db import models
from django.db.models import CheckConstraint, Q

from cashier.models.parlays import ParlayPayoutRuleset
from parameters.models import VHost, VHostCryptoParameters, VHostDomain
from sports.models import Sport, Group


class AccountLevels(models.Model):
    class Meta:
        constraints = [
            CheckConstraint(
                condition=(
                    (Q(crypto_enabled=True) & Q(fiat_enabled=False)) |
                    (Q(crypto_enabled=False) & Q(fiat_enabled=True))
                ),
                name="crypto_xor_fiat_enabled"
            )
        ]
    uuid = models.UUIDField(primary_key=True,default=uuid4)
    vhost = models.ForeignKey(VHost, on_delete=models.CASCADE)
    vdomain = models.ForeignKey(VHostDomain, on_delete=models.CASCADE,null=True)
    agents = models.ManyToManyField('management.Manager', verbose_name="Managers this level applies to",help_text="No agent means Users WITHOUT agent!",blank=True)
    name = models.TextField(verbose_name="Account Level Name")
    active = models.BooleanField(verbose_name="Account Level Active", default=True)
    self_activation = models.BooleanField(verbose_name="Self Activation/Registration available/open for this level", default=False)
    initial_level = models.BooleanField(verbose_name="Initial Level assigned to new accounts", default=False)
    crypto_enabled = models.BooleanField(verbose_name="Crypto Enabled for Wagering and normal ops", default=True)
    fiat_enabled = models.BooleanField(verbose_name="Fiat Enabled for Wagering and normal ops", default=False)
    auto_assign = models.BooleanField(help_text="Assign level to accounts automatically during creation/kyc processes?", default=True)
    description = models.TextField(verbose_name="Account Level Description")
    user_description = models.TextField(verbose_name="Account Level Description: User Facing Title/Description")
    activation_data = models.JSONField(verbose_name="Account Level Activation/Registration Data",default=dict,blank=True,null=True)
    python_package = models.TextField(verbose_name="Account Level Python Package",null=True,blank=True)
    icon_class = models.TextField(verbose_name="Account Level Icon Class",null=True,blank=True)
    ordering_key = models.IntegerField(verbose_name="Ordering Key",default=0)
    juice_pct = models.IntegerField(verbose_name="Juice PCT",default=0)
    validate_mobile = models.BooleanField(verbose_name="Validate Mobile", default=False,help_text="Validate mobile number for non-kyc or pre-kyc validation")
    email_kyc = models.BooleanField(verbose_name="Account Level requires or is triggered by Email KYC", default=False)
    phone_kyc = models.BooleanField(verbose_name="Account Level requires or is triggered by Phone KYC", default=False)
    soft_kyc = models.BooleanField(verbose_name="Account Level requires or is triggered by Soft KYC", default=False)
    strict_kyc = models.BooleanField(verbose_name="Account Level requires or is triggered by Strict KYC", default=False)
    parlay_ruleset = models.ForeignKey(ParlayPayoutRuleset, on_delete=models.RESTRICT)
    max_deposit_fiat = models.IntegerField(verbose_name="Max Deposit (FIAT)",default=0)
    max_withdrawal_fiat = models.IntegerField(verbose_name="Max Withdrawal (FIAT)",default=0)
    deposit_fee_pct_fiat = models.IntegerField(verbose_name="Deposit Fee Percentage (FIAT)",default=0)
    withl_fee_pct_fiat = models.IntegerField(verbose_name="Withdrawal Fee Percentage (FIAT)",default=0)
    max_play_amount_fiat = models.DecimalField(verbose_name="Max Play Amount (FIAT)",default=0,max_digits=12,decimal_places=2)
    min_play_amount_fiat = models.DecimalField(verbose_name="Min Play Amount (FIAT)", default=0,max_digits=12,decimal_places=2)
    max_deposit_cryp = models.IntegerField(verbose_name="Max Deposit (Crypto)",default=0)
    max_withdrawal_cryp = models.IntegerField(verbose_name="Max Withdrawal (Crypto)",default=0)
    deposit_fee_pct_cryp = models.IntegerField(verbose_name="Deposit Fee Percentage (Crypto)",default=0)
    withl_fee_pct_cryp = models.IntegerField(verbose_name="Withdrawal Fee Percentage (Crypto)",default=0)
    max_play_amount_cryp = models.DecimalField(verbose_name="Max Play Amount (Crypto)",default=0,max_digits=12,decimal_places=2)
    min_play_amount_cryp = models.DecimalField(verbose_name="Min Play Amount (Crypto)", default=0,max_digits=12,decimal_places=2)
    daily_deposit_lim_cryp = models.DecimalField(verbose_name="Daily Deposit Limit (Crypto)",default=0,max_digits=12,decimal_places=2)
    weekly_deposit_lim_cryp = models.DecimalField(verbose_name="Weekly Deposit Limit (Crypto)",default=0,max_digits=12,decimal_places=2)
    monthly_deposit_lim_cryp = models.DecimalField(verbose_name="Monthly Deposit Limit (Crypto)",default=0,max_digits=12,decimal_places=2)
    yearly_deposit_lim_cryp = models.DecimalField(verbose_name="Yearly Deposit Limit (Crypto)",default=0,max_digits=12,decimal_places=2)
    daily_deposit_lim_fiat = models.DecimalField(verbose_name="Daily Deposit Limit (FIAT)",default=0,max_digits=12,decimal_places=2)
    weekly_deposit_lim_fiat = models.DecimalField(verbose_name="Weekly Deposit Limit (FIAT)",default=0,max_digits=12,decimal_places=2)
    monthly_deposit_lim_fiat = models.DecimalField(verbose_name="Monthly Deposit Limit (FIAT)",default=0,max_digits=12,decimal_places=2)
    yearly_deposit_lim_fiat = models.DecimalField(verbose_name="Yearly Deposit Limit (FIAT)",default=0,max_digits=12,decimal_places=2)
    daily_withdrawal_lim_cryp = models.DecimalField(verbose_name="Daily Withdrawal Limit (Crypto)",default=0,max_digits=12,decimal_places=2)
    weekly_withdrawal_lim_cryp = models.DecimalField(verbose_name="Weekly Withdrawal Limit (Crypto)",default=0,max_digits=12,decimal_places=2)
    monthly_withdrawal_lim_cryp = models.DecimalField(verbose_name="Monthly Withdrawal Limit (Crypto)",default=0,max_digits=12,decimal_places=2)
    yearly_withdrawal_lim_cryp = models.DecimalField(verbose_name="Yearly Withdrawal Limit (Crypto)",default=0,max_digits=12,decimal_places=2)
    daily_withdrawal_lim_fiat = models.DecimalField(verbose_name="Daily Withdrawal Limit (FIAT)",default=0,max_digits=12,decimal_places=2)
    weekly_withdrawal_lim_fiat = models.DecimalField(verbose_name="Weekly Withdrawal Limit (FIAT)",default=0,max_digits=12,decimal_places=2)
    monthly_withdrawal_lim_fiat = models.DecimalField(verbose_name="Monthly Withdrawal Limit (FIAT)",default=0,max_digits=12,decimal_places=2)
    yearly_withdrawal_lim_fiat = models.DecimalField(verbose_name="Yearly Withdrawal Limit (FIAT)",default=0,max_digits=12,decimal_places=2)
    # def has_next_level(self):
    #     return AccountLevels.objects.filter(vhost=self.vhost,active=True,vdomain=self.vdomain,self_activation=True,auto_assign=False,crypto_enabled=self.crypto_enabled,fiat_enabled=self.fiat_enabled,agents__in=self.agents.all(),ordering_key=self.ordering_key+1).exists()
    # def get_next_level(self):
    #     return AccountLevels.objects.filter(vhost=self.vhost, active=True, vdomain=self.vdomain, self_activation=True,
    #                                    auto_assign=False, crypto_enabled=self.crypto_enabled,
    #                                    fiat_enabled=self.fiat_enabled, agents__in=self.agents,
    #                                    ordering_key=self.ordering_key + 1).order_by("ordering_key").first()
    def get_base_crypto(self):
        vhc = VHostCryptoParameters.objects.get(vhost=self.vhost)
        return vhc.token_base_currency

    def get_base_rate(self):
        vhc = VHostCryptoParameters.objects.get(vhost=self.vhost)
        return vhc.token_base_currency_xrate

    def get_base_rate_and_crypto(self):
        vhc = VHostCryptoParameters.objects.get(vhost=self.vhost)
        return vhc.token_base_currency_xrate,vhc.token_base_currency

    def __str__(self):
        return f"Account Levels for {self.vhost}: '{self.name}': MD(f): {self.max_deposit_fiat}, MD(c): {self.max_deposit_cryp}, MP(f): {self.max_play_amount_fiat}, MP(c): {self.max_play_amount_cryp},  Juice: {self.juice_pct}%"

@admin.register(AccountLevels)
class AccountLevelsAdmin(admin.ModelAdmin):
    list_filter = ["vhost"]
    search_filter = ["vhost","name"]



class AccountLevelPaymentMethod(models.Model):
    uuid = models.UUIDField(primary_key=True,default=uuid4)
    name = models.TextField(verbose_name="Payment Method Name")
    description = models.TextField(verbose_name="Payment Method Description")
    max_deposit = models.IntegerField(verbose_name="Max Deposit",default=0)
    is_fiat = models.BooleanField(verbose_name="Is Fiat", default=False)
    is_crypto = models.BooleanField(verbose_name="Is Crypto", default=True)
    icon_class = models.TextField(verbose_name="Account Level Icon Class",null=True,blank=True)
    ordering_key = models.IntegerField(verbose_name="Ordering Key",default=0)
    active = models.BooleanField(verbose_name="Account Level Active", default=True)
    method_data = models.JSONField(verbose_name="Payment Method Data",default=dict)
    def __str__(self):
        return f"PaymentMethod: {self.name}/{self.description}"

@admin.register(AccountLevelPaymentMethod)
class AccountLevelPaymentMethodAdmin(admin.ModelAdmin):
    list_filter = ["is_fiat","is_crypto"]
    search_filter = ["name"]

class AccountLevelPaymentMethodMembers(models.Model):
    class Meta:
        unique_together = (('level','method'))
    uuid = models.UUIDField(primary_key=True,default=uuid4)
    level = models.ForeignKey(AccountLevels, on_delete=models.CASCADE)
    method = models.ForeignKey(AccountLevelPaymentMethod, on_delete=models.CASCADE)
    # def __str__(self):
    #     return f"Account Level Members for {self.level.name}: {self.method.name}"

@admin.register(AccountLevelPaymentMethodMembers)
class AccountLevelPaymentMethodMembersAdmin(admin.ModelAdmin):
        list_filter = ['level','method']


class PaymentProviders(models.Model):
    uuid = models.UUIDField(primary_key=True,default=uuid4)
    name = models.TextField(verbose_name="Payment Provider Name",unique=True)
    description = models.TextField(verbose_name="Payment Provider Description")
    is_fiat = models.BooleanField(verbose_name="Is Fiat", default=False)
    is_crypto = models.BooleanField(verbose_name="Is Crypto", default=True)
    icon_class = models.TextField(verbose_name="Payment Provider Icon Class",null=True,blank=True)
    ordering_key = models.IntegerField(verbose_name="Ordering Key",default=0)
    module_name = models.TextField(verbose_name="Payment Provider Module Name",unique=True)
    deposits = models.BooleanField(verbose_name="Deposits", default=True)
    dep_min = models.IntegerField(verbose_name="Minimum Payment Amount",default=0)
    dep_max = models.IntegerField(verbose_name="Maximum Payment Amount",default=0)
    dep_fees = models.DecimalField(verbose_name="Deposit Fees PCT",default=0,max_digits=4,decimal_places=2)
    withdrawals = models.BooleanField(verbose_name="Withdrawals", default=True)
    wdl_min = models.IntegerField(verbose_name="Withdrawals Payment Amount", default=0)
    wdl_max = models.IntegerField(verbose_name="Withdrawals Payment Amount", default=0)
    wdl_fees = models.DecimalField(verbose_name="Withdrawals Fees PCT", default=0, max_digits=4, decimal_places=2)
    default_crypto = models.CharField(verbose_name="Default Crypto Symbol", default=None,null=True)
    def __str__(self):
        return f"PaymentProvider: {self.name}"

@admin.register(PaymentProviders)
class PaymentProvidersAdmin(admin.ModelAdmin):
        list_filter = ['name','is_fiat','is_crypto']
        search_filter = ['name']

class VDomainPaymentProviders(models.Model):
    class Meta:
        unique_together = (('vdomain','payment_provider'))
    uuid = models.UUIDField(primary_key=True,default=uuid4)
    payment_provider = models.ForeignKey(PaymentProviders, on_delete=models.CASCADE)
    vdomain = models.ForeignKey('parameters.VHostDomain', on_delete=models.CASCADE)
    active = models.BooleanField(verbose_name="VDomain Active", default=True)
    def __str__(self):
        return f"VDomainPaymentProvider: {self.payment_provider.name} for Domain {self.vdomain.domain_fqdn}"


@admin.register(VDomainPaymentProviders)
class VDomainPaymentProvidersAdmin(admin.ModelAdmin):
        list_filter = ['payment_provider','vdomain']
        search_filter = ['payment_provider__name']



class FiatCurrencies(models.Model):
    uuid = models.UUIDField(primary_key=True,default=uuid4)
    vhost = models.ForeignKey(VHost, on_delete=models.CASCADE, verbose_name="Virtual Host")
    vdomain = models.ManyToManyField('parameters.VHostDomain', blank=True)
    symbol = models.CharField(verbose_name="Exchange Currency Code", max_length=20)
    name = models.CharField(verbose_name="Exchange Currency Name", max_length=200)
    active = models.BooleanField(verbose_name="Exchange Currency Active", default=True)
    def __str__(self):
        return f"{self.symbol}/{self.name}"


@admin.register(FiatCurrencies)
class FiatCurrenciesAdmin(admin.ModelAdmin):
    list_filter = ["vhost","symbol","vdomain"]

class FiatCurrencyProviderCode(models.Model):
    class Meta:
        unique_together = (('currency','provider'))
    uuid = models.UUIDField(primary_key=True,default=uuid4)
    currency = models.ForeignKey(FiatCurrencies, on_delete=models.CASCADE)
    provider = models.TextField(verbose_name="Fiat Currency Provider")
    code = models.TextField(verbose_name="Fiat Currency Code",null=True,blank=True)
    code_int = models.IntegerField(verbose_name="Fiat Currency Code Integer",null=True,blank=True)

class CashierVDomainParameters(models.Model):
    uuid = models.UUIDField(primary_key=True,default=uuid4)
    vhost = models.ForeignKey(VHost, on_delete=models.CASCADE, verbose_name="Virtual Host")
    vdomain = models.ManyToManyField('parameters.VHostDomain', blank=True)
    crypto_enabled = models.BooleanField(verbose_name="Crypto Enabled", default=True)
    base_crypto = models.ForeignKey('cashier.CryptoCurrency', on_delete=models.CASCADE, verbose_name="Base Crypto",blank=True,null=True)
    xchng_rate = models.DecimalField(verbose_name="Exchange Rate Crypto-to-Tokens",decimal_places=5,max_digits=20,default=1)
    fiat_enabled = models.BooleanField(verbose_name="Fiat Enabled", default=False)
    base_fiat = models.ForeignKey(FiatCurrencies, on_delete=models.CASCADE, verbose_name="Base Fiat",blank=True,null=True)
    fiat_xchng_rate = models.DecimalField(verbose_name="Exchange Rate Fiat-to-tokens",decimal_places=5,max_digits=20,default=1)
    majestic_iframe_base_url = models.TextField(verbose_name="Majestic Provider Iframe Base URL", blank=True, null=True, help_text="Base URL for Majestic payment provider iframe (e.g., https://example.com)")
    majestic_merchant_key = models.TextField(verbose_name="Majestic Provider Merchant Key", blank=True, null=True, help_text="Merchant key for Majestic payment provider")
    majestic_wallet_address = models.TextField(verbose_name="Majestic Provider Wallet Address", blank=True, null=True, help_text="Wallet address for Majestic payment provider")
    def __str__(self):
        return f"Parameters for {self.vhost}/{self.vdomain.all()}"


@admin.register(CashierVDomainParameters)
class CashierVDomainParametersAdmin(admin.ModelAdmin):
    list_filter = ["vhost","vdomain"]
