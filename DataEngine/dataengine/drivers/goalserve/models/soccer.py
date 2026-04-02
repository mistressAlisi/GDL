import uuid

from django.contrib import admin
from django.db import models
from django.db.models import TextField

from dataengine.drivers.goalserve.models import Team, SportCategory


class SoccerFixture(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, primary_key=True)
    vhost = models.ForeignKey('parameters.VHost', on_delete=models.CASCADE,related_name='fixtures')
    category = models.ForeignKey(SportCategory,on_delete=models.CASCADE)
    static_id = models.IntegerField(blank=True, null=True)
    fixture_id = models.IntegerField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    intj_time = models.TextField(blank=True, null=True)
    intj_minute = models.TextField(blank=True, null=True)
    date = models.DateField(blank=True, null=True)
    home_team = models.ForeignKey(Team, on_delete=models.CASCADE,related_name="home_team")
    away_team = models.ForeignKey(Team, on_delete=models.CASCADE,related_name="away_team")
    formatted_date = models.TextField(blank=True, null=True)
    commence_time = models.DateTimeField(blank=True, null=True)
    time = models.TextField(blank=True, null=True)
    venue = models.TextField(blank=True, null=True)
    v_id = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"{self.category.name}: {self.fixture_id}: {self.status}"

@admin.register(SoccerFixture)
class SoccerFixtureAdmin(admin.ModelAdmin):
    pass


class SoccerEvent(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, primary_key=True)
    vhost = models.ForeignKey('parameters.VHost', on_delete=models.CASCADE,related_name='events')
    fixture = models.ForeignKey(SoccerFixture, on_delete=models.CASCADE)
    event_id = models.IntegerField(blank=True, null=True)
    type = models.TextField(blank=True, null=True)
    minute = models.TextField(blank=True, null=True)
    extra_min = TextField(blank=True, null=True)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    player = models.TextField(blank=True, null=True)
    player_id = models.IntegerField(blank=True, null=True)
    assist = models.TextField(blank=True, null=True)
    assist_id = models.IntegerField(blank=True, null=True)
    result = models.TextField(blank=True, null=True)
    is_penalty = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"{self.fixture.fixture_id}: {self.event_id}: {self.type}"

@admin.register(SoccerEvent)
class SoccerEventAdmin(admin.ModelAdmin):
    pass

class SoccerFixtureScore(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, primary_key=True)
    vhost = models.ForeignKey('parameters.VHost', on_delete=models.CASCADE,related_name='fixturescore')
    fixture = models.ForeignKey(SoccerFixture, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE,related_name="scores")
    score = models.IntegerField(blank=True, null=True,default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"{self.fixture.fixture_id}: {self.team.name}: {self.score}"


@admin.register(SoccerFixtureScore)
class SoccerFixtureScoreAdmin(admin.ModelAdmin):
    pass
