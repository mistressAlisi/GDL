import uuid

from django.contrib import admin
from django.db import models

from dataengine.models import DataEngineDriver
from matches.models import Match
from parameters.models import VHost
from teams.models import Team


# Create your models here.
class Segment(models.Model):
    uuid = models.UUIDField(primary_key=True,default=uuid.uuid4)
    vhost = models.ForeignKey(VHost, on_delete=models.CASCADE,related_name="segments")
    segment_id = models.IntegerField(default=0)
    name = models.TextField(null=True)
    abrv = models.TextField(db_index=True)
    inserted_on = models.DateTimeField(null=True)
    inserted_on_epoch = models.BigIntegerField(null=True)
    def __str__(self):
        return f"{self.segment_id} | {self.name} in VHost {self.vhost}"

@admin.register(Segment)
class SegmentAdmin(admin.ModelAdmin):
    list_filter = ["segment_id", "vhost"]

class Outcome(models.Model):
    uuid = models.UUIDField(primary_key=True,default=uuid.uuid4)
    vhost = models.ForeignKey(VHost, on_delete=models.CASCADE,related_name="outcomes")
    match = models.ForeignKey(Match, on_delete=models.CASCADE,null=True,blank=True)
    # segment = models.ForeignKey(Segment, on_delete=models.CASCADE,null=True,blank=True)
    segment = models.TextField(db_index=True, null=True,blank=True)
    driver = models.TextField(db_index=True, null=True,blank=True)
    outcome_id = models.TextField(db_index=True)
    routing_key = models.TextField(db_index=True,null=True)
    clock = models.TextField(null=True)
    status_short = models.TextField(null=True)
    status_long = models.TextField(null=True)
    is_current = models.BooleanField(default=False,null=True,blank=True)
    is_start_game = models.BooleanField(default=False,null=True,blank=True)
    is_end_game = models.BooleanField(default=False,null=True,blank=True)
    is_start_segment = models.BooleanField(default=False,null=True,blank=True)
    is_end_segment = models.BooleanField(default=False,null=True,blank=True)
    last_home_score = models.DecimalField(max_digits=10, decimal_places=2, null=True,blank=True)
    last_away_score = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    inserted_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    state_id = models.TextField(null=True,blank=True)
    def __str__(self):
        return f"{self.match}  in VHost {self.vhost}: Outcome for {self.match}"

@admin.register(Outcome)
class OutcomeAdmin(admin.ModelAdmin):
    list_filter = ["match", "vhost","segment"]


class OutcomeSegmentScore(models.Model):
    uuid = models.UUIDField(primary_key=True,default=uuid.uuid4)
    outcome = models.ForeignKey(Outcome, on_delete=models.CASCADE)
    vhost = models.ForeignKey(VHost, on_delete=models.CASCADE,related_name="outcome_segment_score")
    # segment = models.ForeignKey(Segment, on_delete=models.CASCADE)
    segment = models.TextField(db_index=True, null=True, blank=True)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    driver = models.TextField(db_index=True, null=True,blank=True)
    routing_key = models.TextField(db_index=True,null=True)
    score = models.FloatField(default=0)
    inserted_on = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_winner = models.BooleanField(default=False,null=True,blank=True)
    state_id = models.TextField(null=True,blank=True)
    def __str__(self):
        return f"{self.outcome}: {self.segment}|{self.team}"

@admin.register(OutcomeSegmentScore)
class OutcomeSegmentScoreAdmin(admin.ModelAdmin):
    list_filter = ["outcome","segment","team","is_winner"]

class OutcomeTeams(models.Model):
    uuid = models.UUIDField(primary_key=True,default=uuid.uuid4)
    outcome = models.ForeignKey(Outcome, on_delete=models.CASCADE,related_name="outcome_teams",null=True,blank=True)
    vhost = models.ForeignKey(VHost, on_delete=models.CASCADE)
    driver = models.TextField(db_index=True, null=True,blank=True)
    team = models.ForeignKey(Team, on_delete=models.CASCADE,null=True,blank=True)
    routing_key = models.TextField(db_index=True,null=True)
    score = models.FloatField(default=0,null=True,blank=True)
    inserted_on = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_winner = models.BooleanField(default=False,null=True,blank=True)
    is_current = models.BooleanField(default=False,null=True,blank=True)
    def __str__(self):
        return f"{self.outcome}: {self.team}: [{self.score}]"

@admin.register(OutcomeTeams)
class OutcomeTeamsAdmin(admin.ModelAdmin):
    list_filter = ["outcome","team","is_winner"]

class OutcomeFinalMatchScores(models.Model):
    uuid = models.UUIDField(primary_key=True,default=uuid.uuid4)
    vhost = models.ForeignKey(VHost, on_delete=models.CASCADE)
    match = models.ForeignKey(Match, on_delete=models.CASCADE,null=True,blank=True)
    winner = models.ForeignKey(Team, on_delete=models.CASCADE,blank=True,null=True)
    draw = models.BooleanField(default=False,null=True,blank=True)
    manual = models.BooleanField(default=False,null=True,blank=True)
    home_team_score = models.IntegerField(default=0)
    away_team_score = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    consensus_data = models.JSONField(null=True,blank=True)

@admin.register(OutcomeFinalMatchScores)
class OutcomeFinalMatchScoresAdmin(admin.ModelAdmin):
    list_filter = ["vhost", "match"]

class OutcomeTeamsLatestScoreView(models.Model):
    class Meta:
        managed = False
        db_table = "outcomes_outcome_latest_team_score_view"
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    vhost = models.ForeignKey(VHost, on_delete=models.CASCADE)
    match = models.ForeignKey(Match, on_delete=models.CASCADE,null=True,blank=True)
    team = models.ForeignKey(Team, on_delete=models.CASCADE,null=True,blank=True)
    name = models.TextField(null=True,blank=True)
    outcome = models.ForeignKey(Outcome, on_delete=models.CASCADE,null=True,blank=True)
    driver = models.TextField(blank=True,null=True)
    clock = models.TextField(blank=True,null=True)
    updated_on = models.DateTimeField(auto_now=True)
    is_current = models.BooleanField(default=False,null=True,blank=True)
    is_winner = models.BooleanField(default=False,null=True,blank=True)
    status_short = models.TextField(null=True,blank=True)
    status_long = models.TextField(null=True,blank=True)
    score = models.IntegerField(default=0)


@admin.register(OutcomeTeamsLatestScoreView)
class OutcomeTeamsLatestScoreViewAdmin(admin.ModelAdmin):
    list_filter = ["outcome","team","is_winner","match"]


