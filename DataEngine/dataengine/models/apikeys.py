from django.contrib import admin
from django.db import models
from uuid import uuid4


class DataEngineAPIKey(models.Model):
    uuid = models.UUIDField(primary_key=True,default=uuid4)
    vhost =  models.ForeignKey('parameters.VHost',on_delete=models.CASCADE)

    name = models.TextField()
    apikey = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)
    def __str__(self):
        return f"Data Engine API Key {self.apikey}"



@admin.register(DataEngineAPIKey)
class DataEngineAPIKeyAdmin(admin.ModelAdmin):
    pass