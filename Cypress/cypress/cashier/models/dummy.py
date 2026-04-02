from uuid import uuid4

from django.db import models




class DummyProviderTXStub(models.Model):
    uuid = models.UUIDField(default=uuid4,primary_key=True)
    provider_tx = models.UUIDField(default=uuid4)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    account = models.ForeignKey("account.Account", on_delete=models.CASCADE)
    vdomain = models.ForeignKey("parameters.VHostDomain", on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    type = models.TextField(blank=True)
    fees = models.DecimalField(max_digits=10, decimal_places=2)
    provider_fees = models.DecimalField(max_digits=10, decimal_places=2)

