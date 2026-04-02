import uuid

from django.contrib import admin
from django.db import models

from account.models import Account
from parameters.models import VHost, VHostDomain
from sports.models import Sport, Group


# Create your models here.

class GDLTicketCartCache(models.Model):
    uuid = models.UUIDField(primary_key=True,default=uuid.uuid4)
    vhost = models.ForeignKey(VHost,on_delete=models.CASCADE)
    domain = models.ForeignKey(VHostDomain,on_delete=models.CASCADE)
    account = models.ForeignKey(Account,on_delete=models.CASCADE)
    events = models.IntegerField(default=0)
    risk = models.IntegerField(default=0)
    returns = models.IntegerField(default=0)
    sports = models.ManyToManyField(Sport,related_name="sports")
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    selected_expires_at = models.DateTimeField()
    selected = models.BooleanField(default=False)
    ticket_data = models.JSONField(default=dict)


@admin.register(GDLTicketCartCache)
class GDLTicketCartCacheAdmin(admin.ModelAdmin):
    pass


class GDLFilterSettingsGroup(models.Model):
    uuid = models.UUIDField(primary_key=True,default=uuid.uuid4)
    vhost = models.ForeignKey(VHost,on_delete=models.CASCADE)
    domain = models.ForeignKey(VHostDomain,on_delete=models.CASCADE)
    name = models.TextField(verbose_name="Filter Settings Group Name",blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)
    group_filter = models.ManyToManyField(Group,blank=True)
    sport_filter = models.ManyToManyField(Sport,blank=True)
    def __str__(self):
        return f"Filter Settings Group {self.name} For {self.vhost}.{self.domain}: {self.name}"




@admin.register(GDLFilterSettingsGroup)
class GDLFilterSettingsGroupAdmin(admin.ModelAdmin):
    pass


class GDLFilterSettingsSportEntry(models.Model):
    uuid = models.UUIDField(primary_key=True,default=uuid.uuid4)
    parent = models.ForeignKey(GDLFilterSettingsGroup,on_delete=models.CASCADE)
    group = models.ForeignKey('sports.Group',on_delete=models.CASCADE)
    sport = models.ForeignKey(Sport,on_delete=models.CASCADE,null=True,blank=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        if self.sport:
            return f"User-Facing Filter Settings Group Entry for {self.parent.name}: {self.group.name}|{self.sport.title}"
        else:
            return f"User-Facing Filter Settings Group Entry for {self.parent.name}: {self.group.name}"



@admin.register(GDLFilterSettingsSportEntry)
class GDLFilterSettingsSportEntryAdmin(admin.ModelAdmin):
    pass




