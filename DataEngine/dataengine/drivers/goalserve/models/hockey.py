import uuid

from django.contrib import admin
from django.db import models
from django.db.models import TextField

from dataengine.drivers.goalserve.models import Team, SportCategory


class HockeyFixture(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, primary_key=True)
    vhost = models.ForeignKey('parameters.VHost', on_delete=models.CASCADE,related_name='hockeyfixture')
    category = models.ForeignKey(SportCategory,on_delete=models.CASCADE)
    id = models.IntegerField(blank=True, null=True)
    fixture_id = models.IntegerField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    date = models.DateField(blank=True, null=True)
    commence_time = models.DateTimeField(blank=True, null=True)
    home_team = models.ForeignKey(Team, on_delete=models.CASCADE,related_name="hockey_home_team")
    away_team = models.ForeignKey(Team, on_delete=models.CASCADE,related_name="hockey_away_team")
    time = models.TextField(blank=True, null=True)
    timer = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"{self.category.name}: {self.fixture_id}: {self.status}"

@admin.register(HockeyFixture)
class HockeyFixtureAdmin(admin.ModelAdmin):
    pass


class HockeyEvent(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, primary_key=True)
    vhost = models.ForeignKey('parameters.VHost', on_delete=models.CASCADE,related_name='hockeyevents')
    fixture = models.ForeignKey(HockeyFixture, on_delete=models.CASCADE)
    event_id = models.IntegerField(blank=True, null=True)
    type = models.TextField(blank=True, null=True)
    minute = models.TextField(blank=True, null=True)
    extra_min = TextField(blank=True, null=True)
    period = models.TextField(blank=True, null=True)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    player = models.TextField(blank=True, null=True)
    player_id = models.IntegerField(blank=True, null=True)
    assist = models.TextField(blank=True, null=True)
    assist_id = models.TextField(blank=True, null=True)
    result = models.TextField(blank=True, null=True)
    is_penalty = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"{self.fixture.fixture_id}: {self.event_id}: {self.type}"

@admin.register(HockeyEvent)
class HockeyEventAdmin(admin.ModelAdmin):
    pass

class HockeyFixtureScore(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, primary_key=True)
    vhost = models.ForeignKey('parameters.VHost', on_delete=models.CASCADE,related_name='hockeyscore')
    fixture = models.ForeignKey(HockeyFixture, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE,related_name="hockey_scores")
    score = models.IntegerField(blank=True, null=True,default=0)
    first = models.IntegerField(blank=True, null=True,default=0)
    second = models.IntegerField(blank=True, null=True,default=0)
    third = models.IntegerField(blank=True, null=True,default=0)
    overtime = models.IntegerField(blank=True, null=True,default=0)
    penalty = models.IntegerField(blank=True, null=True,default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"{self.fixture.fixture_id}: {self.team.name}: {self.score}"


@admin.register(HockeyFixtureScore)
class HockeyFixtureScoreAdmin(admin.ModelAdmin):
    pass
