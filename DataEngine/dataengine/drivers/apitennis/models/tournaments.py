from uuid import uuid4

from django.contrib import admin
from django.db import models


class EventType(models.Model):
    uuid = models.UUIDField(primary_key=True,default=uuid4)
    vhost = models.ForeignKey('parameters.VHost', on_delete=models.CASCADE,related_name='at_event_type')
    inserted_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    event_type_key = models.IntegerField(unique=True,db_index=True,null=True)
    event_type_type = models.TextField()

    def __str__(self):
        return self.event_type_type


@admin.register(EventType)
class EventTypeAdmin(admin.ModelAdmin):
    pass

class Tournament(models.Model):
    uuid = models.UUIDField(primary_key=True,default=uuid4)
    vhost = models.ForeignKey('parameters.VHost', on_delete=models.CASCADE,related_name='at_tournament')
    event_type = models.ForeignKey(EventType, on_delete=models.CASCADE)
    active = models.BooleanField(default=True)
    inserted_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    tournament_key = models.IntegerField(db_index=True)
    tournament_name = models.TextField()
    tournament_surface = models.TextField(null=True,blank=True)
    def get_name(self):
        return self.tournament_name
    def __str__(self):
        return f"{self.tournament_name}: {self.tournament_surface}"


@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):
    list_filter = ["vhost","event_type","active"]