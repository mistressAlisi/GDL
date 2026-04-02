from datetime import timezone, timedelta
from uuid import uuid4
from django.contrib import admin
from django.db import models
from cashier.models.base import AccountLevels
from licensemanager.models import AvailableApplication
from parameters.models import VHostDomain, VHost


class CryptoCurrency(models.Model):
    class Meta:
        unique_together = (('vhost','symbol'))
    uuid = models.UUIDField(primary_key=True,default=uuid4)
    coinlore_id = models.TextField(verbose_name="CoinLoreID for this Currency", null=True, blank=True)
    vhost = models.ForeignKey(VHost, on_delete=models.CASCADE)
    vdomain = models.ManyToManyField(VHostDomain, blank=True)
    symbol = models.TextField(verbose_name="Symbol/Token for this Currency", null=True, blank=True)
    name = models.TextField(verbose_name="Token Name",help_text="i.e.: Bitcoin, Ethereum")
    current_usd_exr = models.DecimalField(verbose_name="Current Exchange Rate to USD",decimal_places=10,max_digits=20,default=0)
    current_eur_exr = models.DecimalField(verbose_name="Current Exchange Rate to EUR", decimal_places=10,max_digits=20, default=0)
    current_btc_exr = models.DecimalField(verbose_name="Current Exchange Rate to BTC", decimal_places=10, max_digits=20,
                                          default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)
    exchange_network = models.TextField(verbose_name="Exchange Network for Crypto", null=True, blank=True)
    def __str__(self):
        return f"CryptoCurrency - {self.symbol}/{self.name} on {self.vhost}"

@admin.register(CryptoCurrency)
class CryptoCurrencyAdmin(admin.ModelAdmin):
    pass

class CryptoCurrencyFXHistory(models.Model):
    uuid = models.UUIDField(primary_key=True,default=uuid4)
    vhost = models.ForeignKey(VHost, on_delete=models.CASCADE)
    crypto = models.ForeignKey(CryptoCurrency, on_delete=models.CASCADE)
    current_usd_exr = models.DecimalField(verbose_name="Current Exchange Rate to USD",decimal_places=10,max_digits=20,default=0)
    current_eur_exr = models.DecimalField(verbose_name="Current Exchange Rate to EUR", decimal_places=10,max_digits=20, default=0)
    current_btc_exr = models.DecimalField(verbose_name="Current Exchange Rate to BTC", decimal_places=10, max_digits=20,
                                          default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    source_url = models.TextField()
    def __str__(self):
        return f"Crypto Currency - {self.crypto.symbol}: Update from {self.created_at}"

@admin.register(CryptoCurrencyFXHistory)
class CryptoCurrencyFXHistoryAdmin(admin.ModelAdmin):
    pass

class CryptoWalletAddress(models.Model):
    uuid = models.UUIDField(primary_key=True,default=uuid4)
    vhost = models.ForeignKey(VHost, on_delete=models.CASCADE)
    vdomain = models.ForeignKey(VHostDomain, on_delete=models.CASCADE)
    crypto = models.ForeignKey(CryptoCurrency, on_delete=models.CASCADE)
    type = models.TextField(verbose_name="Wallet Type")
    network = models.TextField(verbose_name="Wallet Network")
    name = models.TextField(verbose_name="Wallet Name")
    addr = models.TextField(verbose_name="Wallet Address")
    active = models.BooleanField(default=True)
    default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"Crypto Currency Wallet - {self.crypto.symbol}: {self.addr}"

@admin.register(CryptoWalletAddress)
class CryptoWalletAddress(admin.ModelAdmin):
    pass