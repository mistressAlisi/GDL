from django.db import models
from uuid import uuid4

from frontend.management.models import Manager


class SepaWithdrawRequest(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid4)
    account = models.ForeignKey('account.Account', on_delete=models.CASCADE, verbose_name="Requesting Account")
    vhost = models.ForeignKey('parameters.VHost', on_delete=models.CASCADE, null=True, blank=True)
    domain = models.ForeignKey('parameters.VHostDomain', on_delete=models.CASCADE, null=True, blank=True)
    amount = models.DecimalField(verbose_name="Requested Withdraw Amount", decimal_places=5, max_digits=20, default=0,blank=True)
    iban_num = models.BigIntegerField(verbose_name="IBAN Number", default=0)
    legal_name = models.CharField(verbose_name="Legal Name", max_length=100, default="")
    created_at =  models.DateTimeField(verbose_name="Withdrawal Created",auto_now_add=True)
    processed_at = models.DateTimeField(verbose_name="Withdrawal Processed",null=True,blank=True)
    processed_by = models.ForeignKey(Manager, on_delete=models.CASCADE, verbose_name="Account Manager Who processed",null=True,blank=True)
    sepa_data = models.JSONField(verbose_name="SEPA Data",null=True,blank=True)
    deposited_at = models.DateTimeField(verbose_name="Deposited Date",null=True,blank=True)
    completed = models.BooleanField(verbose_name="Completed", default=False)
    provider = "cashier.providers.sepa"

    def __str__(self):
        return f"SEPA Payout for Account {self.account}: Created at {self.created_at} For ${self.amount}"