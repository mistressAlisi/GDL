import uuid

from django.contrib import admin
from django.db import models
from django.db.models import TextField

from dataengine.drivers.goalserve.models import Team, SportCategory

class AmericanFBallFixture(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, primary_key=True)
    vhost = models.ForeignKey('parameters.VHost', on_delete=models.CASCADE,related_name='amffixture')
    category = models.ForeignKey(SportCategory,on_delete=models.CASCADE)
    fixture_id = models.IntegerField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    date = models.DateField(blank=True, null=True)
    commence_time = models.DateTimeField(blank=True, null=True)
    home_team = models.ForeignKey(Team, on_delete=models.CASCADE,related_name="amf_home")
    away_team = models.ForeignKey(Team, on_delete=models.CASCADE,related_name="amf_away")
    time = models.TextField(blank=True, null=True)
    timer = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    venue_id = models.TextField(blank=True, null=True)
    venue = models.TextField(blank=True, null=True)
    def __str__(self):
        return f"{self.category.name}: {self.fixture_id}: {self.status}"

@admin.register(AmericanFBallFixture)
class AmericanFBallFixtureAdmin(admin.ModelAdmin):
    pass

class AmericanFBallScore(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, primary_key=True)
    vhost = models.ForeignKey('parameters.VHost', on_delete=models.CASCADE,related_name='amf_vhostf')
    fixture = models.ForeignKey(AmericanFBallFixture, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE,related_name="amf_team")
    q1 = models.IntegerField(blank=True, null=True,default=0)
    q2 = models.IntegerField(blank=True, null=True,default=0)
    q3 = models.IntegerField(blank=True, null=True,default=0)
    q4 = models.IntegerField(blank=True, null=True,default=0)
    ot = models.IntegerField(blank=True, null=True,default=0)
    score = models.IntegerField(blank=True, null=True,default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"{self.fixture.fixture_id}: {self.team.name}: {self.score}"


@admin.register(AmericanFBallScore)
class AmericanFBallScoreAdmin(admin.ModelAdmin):
    pass
