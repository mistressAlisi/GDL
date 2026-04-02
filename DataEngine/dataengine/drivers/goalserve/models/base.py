import uuid

from django.contrib import admin
from django.db import models



class SportCategory(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, primary_key=True)
    vhost = models.ForeignKey('parameters.VHost', on_delete=models.CASCADE)
    gid = models.IntegerField(blank=True, null=True)
    name = models.TextField(blank=True, null=True)
    id = models.IntegerField(blank=True, null=True)
    file_group = models.TextField(blank=True, null=True)
    iscup = models.BooleanField(default=False)
    def __str__(self):
        return f"{self.gid}-{self.id}: {self.name}"

@admin.register(SportCategory)
class SportCategoryAdmin(admin.ModelAdmin):
    pass

class Team(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, primary_key=True)
    vhost = models.ForeignKey('parameters.VHost', on_delete=models.CASCADE,related_name='goalservedteams')
    name = models.TextField(blank=True, null=True)
    id = models.IntegerField(blank=True, null=True)
    def __str__(self):
        return f"{self.id}: {self.name}"

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    pass