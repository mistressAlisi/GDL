from datetime import timezone, timedelta
from uuid import uuid4
from django.contrib import admin
from django.db import models

from cashier.models import CryptoCurrency
from cashier.models.base import AccountLevels
from licensemanager.models import AvailableApplication
from parameters.models import VHostDomain

class AccountBalance(models.Model):
    uuid = models.UUIDField(primary_key=True,default=uuid4)
    account = models.OneToOneField('account.Account',on_delete=models.CASCADE,verbose_name="Account")
    vhost = models.ForeignKey('parameters.VHost', on_delete=models.CASCADE, null=True, blank=True)
    domain = models.ForeignKey('parameters.VHostDomain', on_delete=models.CASCADE, null=True, blank=True)
    available = models.DecimalField(verbose_name="Available Balance",decimal_places=5,max_digits=20,default=0,blank=True)
    deposits = models.DecimalField(verbose_name="Deposits",decimal_places=5,max_digits=20,default=0,blank=True)
    withdrawals = models.DecimalField(verbose_name="Withdrawals", decimal_places=5, max_digits=20, default=0, blank=True)
    fees = models.DecimalField(verbose_name="Fees",decimal_places=5,max_digits=20,default=0)
    bonus = models.DecimalField(verbose_name="Bonus",decimal_places=5,max_digits=20,default=0)
    bonus_points = models.DecimalField(verbose_name="Bonus",decimal_places=5,max_digits=20,default=0)
    pending_deposits = models.DecimalField(verbose_name="Deposits",decimal_places=5,max_digits=20,default=0,blank=True)
    pending_rollovers = models.DecimalField(verbose_name="Pending Rollovers",decimal_places=5,max_digits=20,default=0,blank=True)
    rollovers = models.DecimalField(verbose_name="Rollovers",decimal_places=5,max_digits=20,default=0,blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    pending_withdraw = models.DecimalField(verbose_name="Pending Withdrawable Balance", decimal_places=5, max_digits=20, default=0,blank=True)
    at_risk = models.DecimalField(verbose_name="At Risk Balance", decimal_places=5, max_digits=20, default=0,blank=True)
    def __str__(self):
        return f"Account Balance for Account {self.account.acctnum}"

class AccountDailyBalance(models.Model):

    uuid = models.UUIDField(primary_key=True,default=uuid4)
    account = models.OneToOneField('account.Account',on_delete=models.CASCADE,verbose_name="Account")
    date = models.DateField(verbose_name="Date",null=True,blank=True)
    vhost = models.ForeignKey('parameters.VHost', on_delete=models.CASCADE, null=True, blank=True)
    domain = models.ForeignKey('parameters.VHostDomain', on_delete=models.CASCADE, null=True, blank=True)
    available = models.DecimalField(verbose_name="Available Balance",decimal_places=5,max_digits=20,default=0,blank=True)
    deposits = models.DecimalField(verbose_name="Deposits",decimal_places=5,max_digits=20,default=0,blank=True)
    withdrawals = models.DecimalField(verbose_name="Withdrawals", decimal_places=5, max_digits=20, default=0, blank=True)
    fees = models.DecimalField(verbose_name="Fees",decimal_places=5,max_digits=20,default=0)
    bonus = models.DecimalField(verbose_name="Bonus",decimal_places=5,max_digits=20,default=0)
    bonus_points = models.DecimalField(verbose_name="Bonus",decimal_places=5,max_digits=20,default=0)
    pending_deposits = models.DecimalField(verbose_name="Deposits",decimal_places=5,max_digits=20,default=0,blank=True)
    pending_rollovers = models.DecimalField(verbose_name="Pending Rollovers",decimal_places=5,max_digits=20,default=0,blank=True)
    rollovers = models.DecimalField(verbose_name="Rollovers",decimal_places=5,max_digits=20,default=0,blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    pending_withdraw = models.DecimalField(verbose_name="Pending Withdrawable Balance", decimal_places=5, max_digits=20, default=0,blank=True)
    at_risk = models.DecimalField(verbose_name="At Risk Balance", decimal_places=5, max_digits=20, default=0,blank=True)
    def __str__(self):
        return f"Account Daily Balance for Account {self.account.acctnum}: {self.date}"


class AccountBalanceLedgerTX(models.Model):
    uuid = models.UUIDField(primary_key=True,default=uuid4)
    parent = models.ForeignKey(AccountBalance,on_delete=models.CASCADE,verbose_name="Parent")
    vhost = models.ForeignKey('parameters.VHost', on_delete=models.CASCADE, null=True, blank=True)
    domain = models.ForeignKey('parameters.VHostDomain', on_delete=models.CASCADE, null=True, blank=True)
    application = models.ForeignKey(AvailableApplication, on_delete=models.CASCADE, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    curr_ip = models.GenericIPAddressField(verbose_name="Current IP",null=True,blank=True)
    type = models.TextField(verbose_name="Tx Type")
    subtype = models.TextField(verbose_name="Subtype",blank=True,null=True)
    fees_change = models.DecimalField(verbose_name="Fees Change", decimal_places=5, max_digits=20, default=0)
    processor_fees = models.DecimalField(verbose_name="Processor Fees", decimal_places=5, max_digits=20, default=0)
    processor_txid = models.TextField(verbose_name="Processor Txid",null=True,blank=True)
    avail_change = models.DecimalField(verbose_name="Available Change",decimal_places=5,max_digits=20,default=0)
    bonus_change = models.DecimalField(verbose_name="Bonus Change", decimal_places=5, max_digits=20, default=0)
    adjustment_change = models.DecimalField(verbose_name="Adjustment Change", decimal_places=5, max_digits=20, default=0)
    win_change = models.DecimalField(verbose_name="Win Change", decimal_places=5, max_digits=20, default=0)
    deposit_change = models.DecimalField(verbose_name="Deposit Change",decimal_places=5,max_digits=20,default=0)
    rollover_change = models.DecimalField(verbose_name="Rollover Change", decimal_places=5, max_digits=20, default=0)
    withdrawable_change = models.DecimalField(verbose_name="Withdrawable Change", decimal_places=5, max_digits=20, default=0)
    pending_deposit_change = models.DecimalField(verbose_name="Pending Deposits Change",decimal_places=5,max_digits=20,default=0)
    pending_rollover_change = models.DecimalField(verbose_name="Pending Rollover Change", decimal_places=5, max_digits=20, default=0)
    pending_withdraw_change = models.DecimalField(verbose_name="Pending Withdrawable Change", decimal_places=5, max_digits=20, default=0)
    at_risk_change = models.DecimalField(verbose_name="At Risk Change", decimal_places=5, max_digits=20, default=0,blank=True)
    original_crypto = models.ForeignKey(CryptoCurrency, on_delete=models.SET_NULL, null=True, blank=True)
    xchg_rate = models.DecimalField(verbose_name="XChg Rate", decimal_places=5, max_digits=20, default=1)
    reference_data = models.JSONField(verbose_name="Reference Data",default=dict,blank=True,null=True)
    processor_provider = models.ForeignKey('cashier.PaymentProviders',on_delete=models.SET_NULL,null=True,blank=True)
    def __str__(self):
        return f"Account Balance Ledger TX - {self.uuid}:{self.parent}"

