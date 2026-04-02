import uuid

from django.contrib import admin
from django.db import models
from django.db.models import TextField

from dataengine.drivers.goalserve.models import Team, SportCategory

class TennisFixture(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, primary_key=True)
    vhost = models.ForeignKey('parameters.VHost', on_delete=models.CASCADE,related_name='tennisfixture')
    category = models.ForeignKey(SportCategory,on_delete=models.CASCADE)
    fixture_id = models.IntegerField(blank=True, null=True)
    tb = models.TextField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    date = models.DateField(blank=True, null=True)
    home_team = models.ForeignKey(Team, on_delete=models.CASCADE,related_name="tennis_home")
    away_team = models.ForeignKey(Team, on_delete=models.CASCADE,related_name="tennis_away")
    time = models.TextField(blank=True, null=True)
    commence_time = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"{self.category.name}: {self.fixture_id}: {self.status}"

@admin.register(TennisFixture)
class TennisFixtureAdmin(admin.ModelAdmin):
    pass

class TennisScore(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, primary_key=True)
    vhost = models.ForeignKey('parameters.VHost', on_delete=models.CASCADE,related_name='tennisscore')
    fixture = models.ForeignKey(TennisFixture, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE,related_name="tennisscore")
    s1 = models.DecimalField(blank=True, null=True,default=0,decimal_places=2,max_digits=10)
    s2 = models.DecimalField(blank=True, null=True,default=0,decimal_places=2,max_digits=10)
    s3 = models.DecimalField(blank=True, null=True,default=0,decimal_places=2,max_digits=10)
    s4 = models.DecimalField(blank=True, null=True,default=0,decimal_places=2,max_digits=10)
    s5 = models.DecimalField(blank=True, null=True,default=0,decimal_places=2,max_digits=10)
    game_score = models.DecimalField(blank=True, null=True,default=0,decimal_places=2,max_digits=10)
    serve = models.FloatField(blank=True, null=True, default=0)
    winner = models.BooleanField(default=False)
    score = models.IntegerField(blank=True, null=True,default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"{self.fixture.fixture_id}: {self.team.name}: {self.score}"


@admin.register(TennisScore)
class TennisScoreAdmin(admin.ModelAdmin):
    pass
