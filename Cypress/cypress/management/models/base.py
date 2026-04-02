# Create your models here.
from uuid import uuid4

from django.contrib import admin
from django.contrib.auth.models import User
from django.db import models
from django.db.models import OneToOneField

from parameters.models import VHost, VHostDomain, Timezone, Locales
from django.utils.translation import gettext_lazy as _

USER_MANAGER_NAME_STR = _("User/Manager Name")
PARENT_USER_AGENT_STR = _("Parent User/Agent")
MOBILE_NUM_STR = _("SMS/Mobile Number")
TWO_FACTOR_ALERT_STR = _("Used for 2FA and Alert management")
MANAGER_ACCT_PREFIX_STR = _("Manager Account Prefix")
ACCT_TZ_STR = _("Account Timezone")
ACCT_LOCALE_STR = _("Account Locale")

class Manager(models.Model):
    class Meta:
        unique_together = (('user','vhost','domain'))
    uuid = models.UUIDField(primary_key=True,default=uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE,verbose_name="User/Manager Name",related_name="manager")
    parent = models.ForeignKey(User, on_delete=models.CASCADE,blank=True,null=True,verbose_name="Parent User/Agent",related_name="manager_parent")
    vhost = models.ForeignKey(VHost, on_delete=models.CASCADE, null=True, blank=True)
    domain = models.ForeignKey(VHostDomain, on_delete=models.CASCADE, null=True, blank=True)
    mobile = models.TextField(verbose_name=MOBILE_NUM_STR,help_text=TWO_FACTOR_ALERT_STR,blank=True,null=True)
    acctnum_prefix = models.TextField(blank=True,null=True,verbose_name=MANAGER_ACCT_PREFIX_STR)
    timezone = models.ForeignKey(Timezone,verbose_name=ACCT_TZ_STR,on_delete=models.SET_NULL,null=True,blank=True)
    locale = models.ForeignKey(Locales, verbose_name=ACCT_LOCALE_STR, on_delete=models.SET_NULL, null=True, blank=True)
    must_change_pw = models.BooleanField(default=True)
    must_set_tz = models.BooleanField(default=True)
    enable_history_log = models.BooleanField(default=True)
    win_notification_threshold = models.IntegerField(default=500)
    def __str__(self):
        manager_user_str = _("Manager: {username}").format(username = self.user.username)
        return manager_user_str

@admin.register(Manager)
class ManagerAdmin(admin.ModelAdmin):
    pass

