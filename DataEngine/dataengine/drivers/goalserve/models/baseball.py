import uuid

from django.contrib import admin
from django.db import models
from django.db.models import TextField

from dataengine.drivers.goalserve.models import Team, SportCategory

class BaseBallFixture(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, primary_key=True)
    vhost = models.ForeignKey('parameters.VHost', on_delete=models.CASCADE,related_name='baseballfixture')
    category = models.ForeignKey(SportCategory,on_delete=models.CASCADE)
    fixture_id = models.IntegerField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    date = models.DateField(blank=True, null=True)
    home_team = models.ForeignKey(Team, on_delete=models.CASCADE,related_name="basehome_team")
    away_team = models.ForeignKey(Team, on_delete=models.CASCADE,related_name="baseaway_team")
    time = models.TextField(blank=True, null=True)
    commence_time = models.DateTimeField(blank=True, null=True)
    extra_inn = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"{self.category.name}: {self.fixture_id}: {self.status}"

@admin.register(BaseBallFixture)
class BaseBallFixtureAdmin(admin.ModelAdmin):
    pass

class BaseBallScore(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, primary_key=True)
    vhost = models.ForeignKey('parameters.VHost', on_delete=models.CASCADE,related_name='baseballscore')
    fixture = models.ForeignKey(BaseBallFixture, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE,related_name="basescores")
    in1 = models.IntegerField(blank=True, null=True,default=0)
    in2 = models.IntegerField(blank=True, null=True,default=0)
    in3 = models.IntegerField(blank=True, null=True,default=0)
    in4 = models.IntegerField(blank=True, null=True,default=0)
    in5 = models.IntegerField(blank=True, null=True,default=0)
    in6 = models.IntegerField(blank=True, null=True,default=0)
    in7 = models.IntegerField(blank=True, null=True,default=0)
    in8 = models.IntegerField(blank=True, null=True,default=0)
    in9 = models.IntegerField(blank=True, null=True,default=0)
    extra = models.TextField(blank=True, null=True,default=0)
    hits = models.IntegerField(blank=True, null=True,default=0)
    errors = models.IntegerField(blank=True, null=True,default=0)
    score = models.IntegerField(blank=True, null=True,default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"{self.fixture.fixture_id}: {self.team.name}: {self.score}"


@admin.register(BaseBallScore)
class BaseBallFixtureScoreAdmin(admin.ModelAdmin):
    pass
