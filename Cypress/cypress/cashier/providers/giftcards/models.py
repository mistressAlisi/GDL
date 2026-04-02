from uuid import uuid4

from django.contrib import admin
from django.db import models

from account.models import Account
from frontend.management.models import Manager
from parameters.models import VHost, VHostDomain


class GiftCardWithdrawal(models.Model):
    uuid = models.UUIDField(primary_key=True,default=uuid4)
    vhost = models.ForeignKey(VHost, on_delete=models.CASCADE, verbose_name="Virtual Host")
    domain = models.ForeignKey(VHostDomain, on_delete=models.CASCADE, verbose_name="Virtual Host Domain", null=True,blank=True)
    account = models.ForeignKey(Account, on_delete=models.CASCADE, verbose_name="Account Name")
    amount = models.DecimalField(verbose_name="Withdrawal Amount", default=100,decimal_places=5, max_digits=20)
    created_at =  models.DateTimeField(verbose_name="Withdrawal Created",auto_now_add=True)
    processed_at = models.DateTimeField(verbose_name="Withdrawal Processed",null=True,blank=True)
    processed_by = models.ForeignKey(Manager, on_delete=models.CASCADE, verbose_name="Account Manager Who processed",null=True,blank=True)
    gift_card_id = models.CharField(verbose_name="Gift Card ID",max_length=100,null=True,blank=True)
    gift_card_data = models.JSONField(verbose_name="Gift Card Data",null=True,blank=True)
    deposited_at = models.DateTimeField(verbose_name="Deposited Date",null=True,blank=True)
    completed = models.BooleanField(verbose_name="Completed", default=False)
    provider = "cashier.providers.giftcards"

    def __str__(self):
        return f"Gift Card Payout for Account {self.account}: Created at {self.created_at} For ${self.amount}"

@admin.register(GiftCardWithdrawal)
class GiftCardWithdrawalAdmin(admin.ModelAdmin):
    pass