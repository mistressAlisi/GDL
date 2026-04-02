from uuid import uuid4

from django.contrib import admin
from django.db import models

from account.models import Account
from licensemanager.models import AvailableApplication
from parameters.models import VHost
from django.utils.translation import gettext_lazy as _

class AccountApplicationLimits(models.Model):
    uuid = models.UUIDField(primary_key=True,default=uuid4)
    application = models.ForeignKey(AvailableApplication,on_delete=models.CASCADE)
    vhost = models.ForeignKey(VHost,on_delete=models.CASCADE)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    daily_limit = models.DecimalField(verbose_name=_("Daily Wagering Limit for this Application"),default=0,max_digits=12,decimal_places=2)
    daily_wagers = models.IntegerField(verbose_name=_("Daily Wager count limit for this Application"),default=0)
    weekly_limit = models.DecimalField(verbose_name=_("Weekly Wagering Limit for this Application"), default=0,
                                      max_digits=12, decimal_places=2)
    weekly_wagers = models.IntegerField(verbose_name=_("Weekly Wager count limit for this Application"), default=0)
    monthly_limit = models.DecimalField(verbose_name=_("Monthly Wagering Limit for this Application"), default=0,
                                      max_digits=12, decimal_places=2)
    monthly_wagers = models.IntegerField(verbose_name=_("Monthly Wager count limit for this Application"), default=0)
    active = models.BooleanField(default=False,verbose_name=_("Enable Application Limit"))



@admin.register(AccountApplicationLimits)
class AccountApplicationLimitsAdmin(admin.ModelAdmin):
    pass


class AccountLockouts(models.Model):
    uuid = models.UUIDField(primary_key=True, editable=False,default=uuid4)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    vhost = models.ForeignKey(VHost, on_delete=models.CASCADE)
    lockout_period_start = models.DateField()
    lockout_period_end = models.DateField()
    active = models.BooleanField(default=True)
    confirmed = models.BooleanField(default=False)


@admin.register(AccountLockouts)
class AccountLockoutsAdmin(admin.ModelAdmin):
    pass


class AccountLossesLimits(models.Model):
    uuid = models.UUIDField(primary_key=True,default=uuid4)
    vhost = models.ForeignKey(VHost,on_delete=models.CASCADE)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    active = models.BooleanField(default=False,verbose_name=_("Enable Wagering Loss Limit"))
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    daily_limit = models.DecimalField(verbose_name=_("Daily Losses Limit"),default=0,max_digits=12,decimal_places=2)

    weekly_limit = models.DecimalField(verbose_name=_("Weekly Losses Limit"), default=0,
                                      max_digits=12, decimal_places=2)

    monthly_limit = models.DecimalField(verbose_name=_("Monthly Losses Limit"), default=0,
                                      max_digits=12, decimal_places=2)



@admin.register(AccountLossesLimits)
class AccountLossesLimitsAdmin(admin.ModelAdmin):
    pass

