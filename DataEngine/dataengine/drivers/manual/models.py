from uuid import uuid4

from django.contrib import admin
from django.db import models

# Create your models here.

class Team(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid4)
    vhost = models.ForeignKey('parameters.VHost', on_delete=models.CASCADE, related_name='manual_team')
    inserted_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    key = models.TextField(db_index=True)
    name = models.TextField()

    def get_name(self):
        return self.name
    def __str__(self):
        return f"{self.key}:{self.name}"


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    pass


class Game(models.Model):
    class Meta:
        ordering = ["id","commence_time"]
    uuid = models.UUIDField(primary_key=True,default=uuid4)
    vhost = models.ForeignKey('parameters.VHost', on_delete=models.CASCADE)
    id = models.IntegerField(unique=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)
    stage = models.TextField(null=True)
    week = models.TextField(null=True)
    commence_time = models.DateTimeField(null=True)
    city = models.TextField(null=True)
    venue = models.TextField(null=True)
    status_short = models.TextField(null=True)
    status_long = models.TextField(null=True)
    status_timer = models.TextField(null=True)
    home_team = models.ForeignKey(Team, on_delete=models.RESTRICT, null=True)
    away_team = models.ForeignKey(Team, on_delete=models.RESTRICT, null=True,related_name='+')
    def get_name(self):
        return f"{self.away_team.name} at {self.home_team.name}"
    def get_time(self):
        return self.commence_time
    def __str__(self):
        return f"Game: {self.id}: {self.away_team.name} at {self.home_team.name} Status: {self.status_short}. Event Time: {self.commence_time}"