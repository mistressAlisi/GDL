import uuid

from django.contrib import admin
from django.db import models

from . import League, Team,  Player, Season



class HOCKGame(models.Model):
    class Meta:
        ordering = ["id","commence_time"]
        unique_together = (('id','vhost'))
    uuid = models.UUIDField(primary_key=True,default=uuid.uuid4)
    vhost = models.ForeignKey('parameters.VHost', on_delete=models.CASCADE)
    id = models.IntegerField()
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)
    stage = models.TextField(null=True)
    week = models.TextField(null=True)
    commence_time = models.DateTimeField(null=True)
    city = models.TextField(null=True)
    venue = models.TextField(null=True)
    status_short = models.TextField(null=True)
    status_long = models.TextField(null=True)
    status_timer = models.TextField(null=True)
    league = models.ForeignKey(League, on_delete=models.RESTRICT, null=True)
    season = models.ForeignKey(Season, on_delete=models.RESTRICT, null=True)
    home_team = models.ForeignKey(Team, on_delete=models.RESTRICT, null=True)
    away_team = models.ForeignKey(Team, on_delete=models.RESTRICT, null=True,related_name='+')
    def get_name(self):
        return f"{self.away_team.name} at {self.home_team.name}"
    def get_time(self):
        return self.commence_time
    def __str__(self):
        return f"HOCK Game: {self.id}: {self.away_team.name} at {self.home_team.name} Status: {self.status_short}. Event Time: {self.commence_time}"

@admin.register(HOCKGame)
class HOCKGameAdmin(admin.ModelAdmin):
    list_filter = ["stage","week","status_short","home_team","away_team","league"]
    search_fields = ["id"]


class HOCKGameScore(models.Model):
    class Meta:
        unique_together = (("match","team","vhost"))
        ordering = ["match","team"]
    uuid = models.UUIDField(primary_key=True,default=uuid.uuid4)
    vhost = models.ForeignKey('parameters.VHost', on_delete=models.CASCADE)
    match = models.ForeignKey(HOCKGame, on_delete=models.RESTRICT, null=True)
    team = models.ForeignKey(Team, on_delete=models.RESTRICT, null=True)
    first = models.IntegerField(null=True)
    second = models.IntegerField(null=True)
    third = models.IntegerField(null=True)
    overtime = models.IntegerField(null=True)
    penalties = models.IntegerField(null=True)
    total = models.IntegerField(null=True)

    @property
    def score(self):
        return self.total

    def __str__(self):
        return f"Scores for HOCK Game {self.match.id}: Team: {self.team.name}: {self.total} "

@admin.register(HOCKGameScore)
class HOCKGameScoreAdmin(admin.ModelAdmin):
    list_filter = ["match","team"]

class HOCKGameScoreSummary(models.Model):
    uuid = models.UUIDField(primary_key=True,default=uuid.uuid4)
    vhost = models.ForeignKey('parameters.VHost', on_delete=models.CASCADE)
    match = models.ForeignKey(HOCKGame, on_delete=models.RESTRICT, null=True)
    team = models.ForeignKey(Team, on_delete=models.RESTRICT, null=True)
    score = models.IntegerField(null=True,default=0)

@admin.register(HOCKGameScoreSummary)
class HOCKGameScoreSummaryAdmin(admin.ModelAdmin):
    list_filter = ["match","team"]



class HOCKGamePlayerStats(models.Model):
    class Meta:
        unique_together = (('player', 'season', 'group','name','hock_game',"vhost"))

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    vhost = models.ForeignKey('parameters.VHost', on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.RESTRICT)
    season = models.ForeignKey(Season, on_delete=models.RESTRICT)
    hock_game = models.ForeignKey(HOCKGame, on_delete=models.RESTRICT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    group =  models.CharField(verbose_name="Stat Group", null=True)
    name = models.CharField(verbose_name="Stat Name", null=True)
    value = models.CharField(verbose_name="Stat Value", null=True)
    def __str__(self):
        return f"{self.player} (Season: {self.season}) (Group: {self.group}): Game {self.hock_game}: {self.name}: {self.value}"

@admin.register(HOCKGamePlayerStats)
class HOCKGamePlayerStatsAdmin(admin.ModelAdmin):
    list_filter = ["season","group","hock_game"]
    search_fields = ["name","group","player__name"]

class HOCKPlayerStats(models.Model):
    class Meta:
        unique_together = (('player', 'season', 'group', 'name',"vhost"))

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    vhost = models.ForeignKey('parameters.VHost', on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.RESTRICT)
    season = models.ForeignKey(Season, on_delete=models.RESTRICT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    group = models.CharField(verbose_name="Stat Group", null=True)
    name = models.CharField(verbose_name="Stat Name", null=True)
    value = models.CharField(verbose_name="Stat Value", null=True)

    def __str__(self):
        return f"{self.player} (Season: {self.season}) (Group: {self.group}): {self.name}: {self.value}"

@admin.register(HOCKPlayerStats)
class HOCKPlayerStatsAdmin(admin.ModelAdmin):
    list_filter = ["season", "group"]
    search_fields = ["name", "group", "player__name"]


class HOCKGameEvent(models.Model):
    uuid = models.UUIDField(primary_key=True,default=uuid.uuid4)
    vhost = models.ForeignKey('parameters.VHost', on_delete=models.CASCADE,related_name='as_hock')
    hock_game = models.ForeignKey(HOCKGame, on_delete=models.RESTRICT)
    quarter = models.CharField(verbose_name="Quarter")
    minute = models.CharField(verbose_name="Minute")
    team = models.ForeignKey(Team, on_delete=models.RESTRICT)
    player = models.ForeignKey(Player, on_delete=models.RESTRICT)
    season = models.ForeignKey(Season, on_delete=models.RESTRICT)
    type = models.CharField(verbose_name="Type",max_length=100)
    comment = models.TextField(verbose_name="Comment")
    score  = models.JSONField(verbose_name="Score Data",default=dict)
    def __str__(self):
        return f"{self.hock_game}: {self.team.name}->{self.player.name}: {self.type} @ {self.minute}: {self.comment}"



@admin.register(HOCKGameEvent)
class HOCKGameEventAdmin(admin.ModelAdmin):
    list_filter = ["hock_game", "quarter","minute","team"]
    search_fields = ["name", "group", "player__name"]
