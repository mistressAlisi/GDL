import uuid
from django.contrib import admin
from django.db import models
from parameters.models import VHost
from django.db.models import ForeignKey

from . import Sides
from .base import League, Season, Location, FixtureType, Participant, Segment
from .fixtures import Fixture

class Outcome(models.Model):
    uuid = models.UUIDField(primary_key=True,default=uuid.uuid4)
    vhost = models.ForeignKey(VHost, on_delete=models.CASCADE)
    fixture = models.ForeignKey(Fixture, on_delete=models.CASCADE)
    segment = models.ForeignKey(Segment, on_delete=models.CASCADE)
    outcome_id = models.IntegerField(db_index=True)
    routing_key = models.TextField(db_index=True,null=True)
    clock = models.TextField(null=True)
    is_current = models.BooleanField(default=False)
    is_start_game = models.BooleanField(default=False)
    is_end_game = models.BooleanField(default=False)
    is_start_segment = models.BooleanField(default=False)
    is_end_segment = models.BooleanField(default=False)
    inserted_on = models.DateTimeField(auto_now_add=True)
    state_id = models.IntegerField(default=0)
    def __str__(self):
        return f"{self.outcome_id}  in VHost {self.vhost}"

@admin.register(Outcome)
class OutcomeAdmin(admin.ModelAdmin):
    list_filter = ["fixture", "vhost","segment"]


class OutcomeSegmentScore(models.Model):
    uuid = models.UUIDField(primary_key=True,default=uuid.uuid4)
    outcome = models.ForeignKey(Outcome, on_delete=models.CASCADE)
    vhost = models.ForeignKey(VHost, on_delete=models.CASCADE)
    segment = models.ForeignKey(Segment, on_delete=models.CASCADE)
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE)
    routing_key = models.TextField(db_index=True,null=True)
    score = models.FloatField(default=0)
    inserted_on = models.DateTimeField(auto_now_add=True)
    is_winner = models.BooleanField(default=False)
    state_id = models.IntegerField(default=0)
    def __str__(self):
        return f"{self.outcome}: {self.segment}|{self.participant}"

@admin.register(OutcomeSegmentScore)
class OutcomeSegmentScoreAdmin(admin.ModelAdmin):
    list_filter = ["outcome","segment","participant","is_winner"]

class OutcomeParticipants(models.Model):
    uuid = models.UUIDField(primary_key=True,default=uuid.uuid4)
    outcome = models.ForeignKey(Outcome, on_delete=models.CASCADE)
    vhost = models.ForeignKey(VHost, on_delete=models.CASCADE)
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE)
    routing_key = models.TextField(db_index=True,null=True)
    score = models.FloatField(default=0)
    inserted_on = models.DateTimeField(auto_now_add=True)
    is_winner = models.BooleanField(default=False)
    def __str__(self):
        return f"Outcome Participant in Outcome#{self.outcome.outcome_id}: {self.participant}"

@admin.register(OutcomeParticipants)
class OutcomeParticipantsAdmin(admin.ModelAdmin):
    list_filter = ["outcome","participant","is_winner"]

