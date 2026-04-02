from uuid import uuid4

from django.contrib import admin
from django.db import models

from cashier.models import CryptoCurrency
from toolkit import accounts


class ProviderTX(models.Model):
    STATUS_CHOICES = (('1','TX Created'),('2','Unpaid'),('3','Partial Payment'),('4','Payment Received'),('5','Invoice Complete'),('100','Cancelled'),('101','Refunded'),('102','Reverted'),('103','Expired w/o payment'))
    uuid = models.UUIDField(default=uuid4,primary_key=True)
    vhost = models.ForeignKey("parameters.VHost", on_delete=models.CASCADE)
    provider = models.TextField(verbose_name="Payment Provider Class Name ")
    status = models.CharField(verbose_name="Payment Status Code ", max_length=20,choices=STATUS_CHOICES)
    provider_tx = models.UUIDField(default=uuid4)
    idem_key = models.TextField(blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    cancelled_at = models.DateTimeField(blank=True, null=True)
    refunded_at = models.DateTimeField(blank=True, null=True)
    confirmed_at = models.DateTimeField(blank=True, null=True)
    deposited_at = models.DateTimeField(blank=True, null=True)
    is_fiat = models.BooleanField(default=False)
    cryp1 = models.ForeignKey(CryptoCurrency,on_delete=models.RESTRICT,null=True,blank=True)
    cryp2 = models.ForeignKey(CryptoCurrency, on_delete=models.RESTRICT, null=True, blank=True,related_name='+')
    hot_wallet = models.TextField(blank=True,null=True,verbose_name="Hot Wallet Address")
    url = models.TextField(blank=True,null=True)
    account = models.ForeignKey("account.Account", on_delete=models.CASCADE)
    domain = models.ForeignKey("parameters.VHostDomain", on_delete=models.CASCADE,null=True,blank=True)
    amount = models.DecimalField(max_digits=30, decimal_places=10)
    pending = models.DecimalField(max_digits=30, decimal_places=10)
    type = models.TextField(blank=True)
    fees = models.DecimalField(max_digits=30, decimal_places=10,default=0)
    provider_fees = models.DecimalField(max_digits=30, decimal_places=10,default=0)
    active = models.BooleanField(default=True)
    completed = models.BooleanField(default=False)
    provider_data = models.JSONField(default=dict)
    invoice_data = models.JSONField(default=dict)
    def __str__(self):
        return f"TX: {self.provider}:[{self.provider_tx}]- {self.vhost}/{self.account}: {self.type}: Amount: {self.amount} {self.cryp1.symbol}"


@admin.register(ProviderTX)
class ProviderTXAdmin(admin.ModelAdmin):
    list_filter = ["vhost","account","domain","type"]
