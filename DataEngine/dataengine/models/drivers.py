from uuid import uuid4

from django.contrib import admin
from django.db import models


class DataEngineDriver(models.Model):
    uuid = models.UUIDField(primary_key=True,default=uuid4)
    name = models.TextField()
    class_name = models.TextField()
    dbobject_class_name = models.TextField(null=True)
    version = models.TextField()
    author = models.TextField()
    homepage = models.TextField()
    installed = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"Data Driver {self.name} by {self.author}: {self.class_name}"

@admin.register(DataEngineDriver)
class DataEngineDriverAdmin(admin.ModelAdmin):
    pass

class DataEngineDriverHistory(models.Model):
    uuid = models.UUIDField(primary_key=True,default=uuid4)
    driver = models.ForeignKey(DataEngineDriver, on_delete=models.CASCADE)
    updated = models.DateTimeField(auto_now=True)
    version = models.TextField()
    data = models.JSONField(default=dict)
    def __str__(self):
        return f"Data Driver {self.driver.name} Version update {self.updated.isoformat()}"


@admin.register(DataEngineDriverHistory)
class DataEngineDriverHistoryAdmin(admin.ModelAdmin):
    pass


class DataEngineVHostConfig(models.Model):
    class Meta:
        unique_together = (("driver","vhost"))
    uuid = models.UUIDField(primary_key=True,default=uuid4)
    driver = models.ForeignKey(DataEngineDriver, on_delete=models.CASCADE)
    vhost = models.ForeignKey('parameters.VHost', on_delete=models.CASCADE)
    active = models.BooleanField(default=True)
    priority = models.IntegerField(default=0)
    authoritative = models.BooleanField(default=False)
    def __str__(self):
        return f"Data Driver {self.driver.name} Config in Vhost {self.vhost}: active {self.active}"


@admin.register(DataEngineVHostConfig)
class DataEngineVHostConfigAdmin(admin.ModelAdmin):
    pass
