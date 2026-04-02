from uuid import uuid4

from django.contrib import admin
from django.db import models


from parameters.models import VHost, VHostDomain


# Create your models here.
class CommonNotification(models.Model):
    class Meta:
        abstract = True
        ordering = ('-created_at',)
    uuid = models.UUIDField(primary_key=True, default=uuid4)
    name = models.TextField(verbose_name="Bonus Level Name")
    vhost = models.ForeignKey(VHost,on_delete=models.CASCADE)
    vdomain =  models.ForeignKey(VHostDomain,on_delete=models.CASCADE,null=True,blank=True)
    active = models.BooleanField(default=True)
    title = models.TextField(verbose_name="Title")
    type = models.TextField(verbose_name="Type",default="not")
    text = models.TextField(verbose_name="Text",blank=True,null=True)
    data = models.JSONField(verbose_name="Data",default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    seen_at = models.DateTimeField(null=True, blank=True,verbose_name="Seen At:")
    icon = models.TextField(verbose_name="Icon",blank=True,null=True)




# class AgentNotifications(CommonNotification):
#     agent = models.ForeignKey('agent.Agent',on_delete=models.CASCADE,related_name="+")
#     def __str__(self):
#         return f"Notification for Agent {self.agent}: {self.title} @ {self.created_at}"
#
# @admin.register(AgentNotifications)
# class AgentNotificationsAdmin(admin.ModelAdmin):
#     list_filter = ["vhost","vdomain","agent"]
#     search_filter = ["title","text"]


class AccountNotifications(CommonNotification):
    account = models.ForeignKey('account.Account',on_delete=models.CASCADE,related_name="+")
    def __str__(self):
        return f"Notification for Account {self.account}: {self.title} @ {self.created_at}"

@admin.register(AccountNotifications)
class AccountNotificationsAdmin(admin.ModelAdmin):
    list_filter = ["vhost","vdomain","account"]
    search_filter = ["title","text"]

class ManagerNotifications(CommonNotification):
    manager = models.ForeignKey('management.Manager', on_delete=models.CASCADE, related_name="+")

    def __str__(self):
        return f"Notification for Manager {self.manager.user}: {self.title} @ {self.created_at}"