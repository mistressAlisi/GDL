import uuid
from django.contrib import admin
from django.db import models
from parameters.models import VHost
from django.db.models import ForeignKey

from . import Sides, State
from .base import League, Season, Location, FixtureType, Participant


class Fixture(models.Model):
    class Meta:
        unique_together = (('vhost','fixture_id'))
    uuid = models.UUIDField(primary_key=True,default=uuid.uuid4)
    vhost = models.ForeignKey(VHost, on_delete=models.CASCADE)
    fixture_id = models.IntegerField()
    parent_fixture_id = models.IntegerField()
    league = models.ForeignKey(League, on_delete=models.CASCADE)
    season = models.ForeignKey(Season, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    fixture_type = models.ForeignKey(FixtureType, on_delete=models.CASCADE)
    routing_key = models.TextField(db_index=True,null=True)
    start_time = models.DateTimeField(null=True, blank=True)
    cutoff_time = models.DateTimeField(null=True, blank=True)
    feed_source_id = models.CharField(null=True, blank=True, max_length=255)
    name = models.TextField(null=True)
    abrv = models.TextField(null=True)
    state = models.ForeignKey(State, on_delete=models.CASCADE,null=True)
    inserted_on_epoch = models.BigIntegerField(null=True)
    inserted_on = models.DateTimeField(null=True)
    timestamp = models.DateTimeField(null=True)
    informations = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    teams_morphed = models.BooleanField(default=False)
    def get_name(self):
        return self.name
    def get_time(self):
        return self.start_time
    def __str__(self):
        return f"{self.fixture_id} | {self.name} in VHost {self.vhost}"

@admin.register(Fixture)
class FixtureAdmin(admin.ModelAdmin):
    list_filter = ["fixture_id", "vhost","league","season","fixture_type"]


class FixtureParticipants(models.Model):
    uuid = models.UUIDField(primary_key=True,default=uuid.uuid4)
    vhost = models.ForeignKey(VHost, on_delete=models.CASCADE)
    fixture = models.ForeignKey(Fixture, on_delete=models.CASCADE)
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE)
    fixture_participant_id = models.IntegerField(db_index=True)
    side = models.ForeignKey(Sides,on_delete=models.CASCADE)
    rotation = models.IntegerField(null=True)
    routing_key = models.TextField(db_index=True,null=True)
    inserted_on = models.DateTimeField(null=True)
    inserted_on_epoch =models.BigIntegerField(null=True)
    timestamp = models.DateTimeField(null=True)
    def __str__(self):
        return f"{self.participant} | {self.side} | {self.rotation} | {self.routing_key}"


@admin.register(FixtureParticipants)
class FixtureParticipantsAdmin(admin.ModelAdmin):
    list_filter = ["fixture","vhost","participant","side","rotation","routing_key"]
