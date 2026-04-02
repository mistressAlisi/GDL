import uuid

from django.contrib import admin
from django.db import models

from matches.models import Match
from parameters.models import VHost
from sports.models import Country
from teams.models import Team


# Create your models here.
class Player(models.Model):
    class Meta:
        ordering = ["key", "name"]
        unique_together = (('key','name'))
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    vhost = models.ForeignKey(VHost, on_delete=models.CASCADE,null=True,blank=True,related_name='players')
    key = models.TextField(verbose_name="Key")
    apiid = models.IntegerField(verbose_name="API ID", null=True)
    name = models.TextField(verbose_name="Name")
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    games = models.IntegerField(default=0)
    wins = models.IntegerField(default=0)
    losses = models.IntegerField(default=0)
    draws = models.IntegerField(default=0)
    image = models.FileField(verbose_name="Player Image",blank=True,null=True)
    large_image = models.FileField(verbose_name="Player Large Image", blank=True, null=True)
    description = models.TextField(verbose_name="Description")
    active = models.BooleanField(verbose_name="Active",default=True)
    has_events = models.BooleanField(verbose_name="Has Active Events",default=True)
    country = models.ForeignKey(Country,on_delete=models.RESTRICT,verbose_name="Origin Country",blank=True,null=True)
    height = models.CharField(verbose_name="Player Height", null=True)
    weight = models.CharField(verbose_name="Player Weight", null=True)
    group = models.CharField(verbose_name="Player Group", null=True)
    college = models.CharField(verbose_name="Player College", null=True)
    position = models.CharField(verbose_name="Player Position", null=True)
    number = models.CharField(verbose_name="Player Number", null=True)
    salary = models.CharField(verbose_name="Player Salary", null=True)
    experience = models.CharField(verbose_name="Player Experience", null=True)
    age = models.CharField(verbose_name="Player Age", null=True)
    def __str__(self):
        return f"{self.name} [{self.key}]"

@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    search_fields = ["name"]
    list_filter = ["group", "position","active","apiid"]


class PlayerTeamAssignment(models.Model):
    class Meta:
        unique_together = (("player", "team"),)
    uuid = models.UUIDField(primary_key=True,default=uuid.uuid4)
    player = models.OneToOneField(Player,on_delete=models.CASCADE)
    team = models.ForeignKey(Team,on_delete=models.CASCADE,null=True)
    active = models.BooleanField(default=True,null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    position = models.TextField(verbose_name="Position on the Team",null=True,blank=True)
    number = models.CharField(verbose_name="Player Number", null=True)
    remarks = models.TextField(verbose_name="Remarks regarding Position",null=True,blank=True)
    def __str__(self):
        return f"{self.player.name}, assigned to {self.team.name}: {self.position or '(No Position)'} #{self.number}"

@admin.register(PlayerTeamAssignment)
class PlayerTeamAssignmentAdmin(admin.ModelAdmin):
    list_filter = ["position","active","team","player__group","player__position"]
    search_fields = ["player"]

class PlayerMatchAssignment(models.Model):
    class Meta:
        unique_together = (("player", "team","match"),)
    uuid = models.UUIDField(primary_key=True,default=uuid.uuid4)
    player = models.ForeignKey(Player,on_delete=models.CASCADE)
    team = models.ForeignKey(Team,on_delete=models.CASCADE)
    match = models.ForeignKey(Match,on_delete=models.CASCADE)
    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    position = models.TextField(verbose_name="Position on the Match",null=True,blank=True)
    number = models.CharField(verbose_name="Player Number", null=True)
    remarks = models.TextField(verbose_name="Remarks regarding Position",null=True,blank=True)
    def __str__(self):
        return f"{self.player.name}, assigned to {self.team.name}: {self.position or '(No Position)'} #{self.number} for match {self.match}"

@admin.register(PlayerMatchAssignment)
class PlayerMatchAssignmentAdmin(admin.ModelAdmin):
    list_filter = ["position","active","team","player__group","player__position","match"]
    search_fields = ["player"]
