import uuid

from django.contrib import admin
from django.db import models

from parameters.models import VHost, VHostDomain
from sports.models import Sport, Group
from teams.models import Team


# Create your models here.



class GDLTicketCacheIndex(models.Model):
    uuid = models.UUIDField( default=uuid.uuid4,primary_key=True)
    created = models.DateTimeField(auto_now_add=True)
    vhost = models.ForeignKey(VHost, on_delete=models.CASCADE,blank=True, null=True)
    domain = models.ForeignKey(VHostDomain, on_delete=models.CASCADE,blank=True, null=True)
    sports = models.ManyToManyField(Sport,blank=True)
    teams = models.ManyToManyField(Team,blank=True)
    min_payout = models.IntegerField(null=True,blank=True)
    max_event_date = models.DateTimeField(null=True,blank=True)
    depth = models.IntegerField(null=True,blank=True)
    stake = models.IntegerField(null=True,blank=True)
    ticket_count = models.IntegerField(default=0)
    max_ticket_count = models.IntegerField(default=1000)
    request_count = models.IntegerField(default=0)


class GDLTicketCache(models.Model):
    uuid = models.UUIDField( default=uuid.uuid4,primary_key=True)
    cache_index = models.ForeignKey(GDLTicketCacheIndex, on_delete=models.CASCADE,blank=True, null=True)
    expires = models.DateTimeField(null=True,blank=True)
    ticket_data = models.JSONField(null=True,blank=True)
    ticket_meta = models.JSONField(null=True, blank=True)
    ticket_count = models.IntegerField(default=0)

class GDLCoreSportGroupFilters(models.Model):
    uuid = models.UUIDField( default=uuid.uuid4,primary_key=True)
    vhost = models.ForeignKey(VHost, on_delete=models.CASCADE,blank=True, null=True)
    domain = models.ForeignKey(VHostDomain, on_delete=models.CASCADE,blank=True, null=True)
    group_filter = models.ManyToManyField(Group,blank=True)
    sport_filter = models.ManyToManyField(Sport,blank=True)
    def __str__(self):
        return f"GDL Sport/Group Filters: {self.vhost}|{self.domain}"

@admin.register(GDLCoreSportGroupFilters)
class GDLCoreSportGroupFiltersAdmin(admin.ModelAdmin):
    pass

class GDLTypeSettingsEntry(models.Model):
    uuid = models.UUIDField( default=uuid.uuid4,primary_key=True)
    vhost = models.ForeignKey(VHost, on_delete=models.CASCADE,blank=True, null=True)
    domain = models.ForeignKey(VHostDomain, on_delete=models.CASCADE,blank=True, null=True)
    group_filter = models.ManyToManyField(Group,blank=True,verbose_name="Sports to Include in selection")
    sport_filter = models.ManyToManyField(Sport,blank=True,verbose_name="Leagues to Include in selection")
    name = models.TextField(null=True,blank=True)
    icon = models.TextField(null=True,blank=True)
    class_name = models.TextField(null=True,blank=True,verbose_name="CSS class for button", default="btn sport-btn w-100 basketball-btn")
    order_by = models.TextField(null=True,blank=True,default=1)
    active = models.BooleanField(null=True,blank=True)
    def __str__(self):
        return f"GDL Type Settings Entry: {self.vhost}|{self.domain}"


@admin.register(GDLTypeSettingsEntry)
class GDLTypeSettingsEntryAdmin(admin.ModelAdmin):
    pass
