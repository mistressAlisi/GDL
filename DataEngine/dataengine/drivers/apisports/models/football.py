import uuid

from django.contrib import admin
from django.db import models

from . import League, Team, Player, Venue, Season



class FBALLGame(models.Model):
    class Meta:
        ordering = ["id","commence_time"]
        unique_together = (('id','vhost'))
    uuid = models.UUIDField(primary_key=True,default=uuid.uuid4)
    vhost = models.ForeignKey('parameters.VHost', on_delete=models.CASCADE)
    id = models.IntegerField()
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)
    round = models.TextField(null=True)
    week = models.TextField(null=True)
    commence_time = models.DateTimeField(null=True)
    city = models.TextField(null=True)
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE,null=True,blank=True)
    status_short = models.TextField(null=True)
    status_long = models.TextField(null=True)
    status_extra = models.TextField(null=True)
    status_timer = models.TextField(null=True)
    stage = models.TextField(null=True)
    league = models.ForeignKey(League, on_delete=models.RESTRICT, null=True)
    season = models.ForeignKey(Season, on_delete=models.RESTRICT, null=True)
    home_team = models.ForeignKey(Team, on_delete=models.RESTRICT, null=True)
    away_team = models.ForeignKey(Team, on_delete=models.RESTRICT, null=True,related_name='+')
    first_period = models.DateTimeField(null=True,blank=True)
    second_period = models.DateTimeField(null=True,blank=True)
    referee = models.TextField(null=True)
    def get_name(self):
        return f"{self.away_team.name} at {self.home_team.name}"
    def get_time(self):
        return self.commence_time
    def __str__(self):
        return f"FBALL Game: {self.id}: {self.away_team.name} at {self.home_team.name} Status: {self.status_short}. Event Time: {self.commence_time}"

@admin.register(FBALLGame)
class FBALLGameAdmin(admin.ModelAdmin):
    list_filter = ["round","week","status_short","home_team","away_team","league"]
    search_fields = ["id"]

class FBALLGameScore(models.Model):
    class Meta:
        unique_together = (("match","team","vhost"))
        ordering = ["match","team"]
    uuid = models.UUIDField(primary_key=True,default=uuid.uuid4)
    vhost = models.ForeignKey('parameters.VHost', on_delete=models.CASCADE)
    match = models.ForeignKey(FBALLGame, on_delete=models.RESTRICT, null=True)
    team = models.ForeignKey(Team, on_delete=models.RESTRICT, null=True)
    halftime = models.IntegerField(null=True)
    fulltime = models.IntegerField(null=True)
    extratime = models.IntegerField(null=True)
    penalty = models.IntegerField(null=True)
    total = models.IntegerField(null=True)
    goals = models.IntegerField(null=True)

    @property
    def score(self):
        if not self.goals:
            goals = 0
        else:
            goals = self.goals
        if not self.total:
            total = 0
        else:
            total = self.total
        return max(goals,total)

    def __str__(self):
        return f"Scores for FBALL Game {self.match.id}: Team: {self.team.name} "

@admin.register(FBALLGameScore)
class FBALLGameScoreAdmin(admin.ModelAdmin):
    list_filter = ["match","team"]

class FBALLGameScoreSummary(models.Model):
    uuid = models.UUIDField(primary_key=True,default=uuid.uuid4)
    vhost = models.ForeignKey('parameters.VHost', on_delete=models.CASCADE)
    match = models.ForeignKey(FBALLGame, on_delete=models.RESTRICT, null=True)
    team = models.ForeignKey(Team, on_delete=models.RESTRICT, null=True)
    score = models.IntegerField(null=True,default=0)

@admin.register(FBALLGameScoreSummary)
class FBALLGameScoreSummaryAdmin(admin.ModelAdmin):
    list_filter = ["match","team"]


class FBALLPlayerStats(models.Model):
    class Meta:
        unique_together = (("player","team","league","vhost"))

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vhost = models.ForeignKey('parameters.VHost', on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    league = models.ForeignKey(League, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE,blank=True, null=True)
    season = models.ForeignKey(Season, on_delete=models.RESTRICT,blank=True, null=True)

    # Games
    games_appearances = models.IntegerField(null=True, blank=True)
    games_lineups = models.IntegerField(null=True, blank=True)
    games_minutes = models.IntegerField(null=True, blank=True)
    games_number = models.IntegerField(null=True, blank=True)
    games_position = models.CharField(max_length=50, null=True, blank=True)
    games_rating = models.FloatField(null=True, blank=True)
    games_captain = models.BooleanField(default=False)

    # Substitutes
    subtitutes_in = models.IntegerField(null=True, blank=True)
    subtitutes_out = models.IntegerField(null=True, blank=True)
    subtitutes_bench = models.IntegerField(null=True, blank=True)

    # Shots
    shots_total = models.IntegerField(null=True, blank=True)
    shots_on = models.IntegerField(null=True, blank=True)

    # Goals
    goals_total = models.IntegerField(null=True, blank=True)
    goals_conceded = models.IntegerField(null=True, blank=True)
    goals_assists = models.IntegerField(null=True, blank=True)
    goals_saves = models.IntegerField(null=True, blank=True)

    # Passes
    passes_total = models.IntegerField(null=True, blank=True)
    passes_key = models.IntegerField(null=True, blank=True)
    pass_accuracy = models.IntegerField(null=True, blank=True)

    # Tackles
    tackles_total = models.IntegerField(null=True, blank=True)
    tackles_blocks = models.IntegerField(null=True, blank=True)
    tackles_interceptions = models.IntegerField(null=True, blank=True)

    # Duels
    duels_total = models.IntegerField(null=True, blank=True)
    duels_won = models.IntegerField(null=True, blank=True)

    # Dribbles
    dribble_attempts = models.IntegerField(null=True, blank=True)
    dribble_success = models.IntegerField(null=True, blank=True)
    dribbled_past = models.IntegerField(null=True, blank=True)

    # Fouls
    fouls_drawn = models.IntegerField(null=True, blank=True)
    fouls_committed = models.IntegerField(null=True, blank=True)

    # Cards
    cards_yellow = models.IntegerField(null=True, blank=True)
    cards_yellowred = models.IntegerField(null=True, blank=True)
    cards_red = models.IntegerField(null=True, blank=True)

    # Penalties
    penalties_won = models.IntegerField(null=True, blank=True)
    penalties_committed = models.IntegerField(null=True, blank=True)
    penalties_scored = models.IntegerField(null=True, blank=True)
    penalties_missed = models.IntegerField(null=True, blank=True)
    penalties_saved = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.player} (Season: {self.season}) (Team: {self.team})"



@admin.register(FBALLPlayerStats)
class FBALLPlayerStatsAdmin(admin.ModelAdmin):
    list_filter = ["league","team","player","season"]
    search_fields = ["id","player__name","player__lastname","player__firstname"]


