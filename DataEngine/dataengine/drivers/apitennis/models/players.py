from uuid import uuid4

from django.db import models

from django.contrib import admin


class Players(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid4)
    vhost = models.ForeignKey('parameters.VHost', on_delete=models.CASCADE, related_name='at_players')
    inserted_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    player_key = models.TextField(db_index=True)
    player_name = models.TextField()
    player_country = models.TextField(null=True,blank=True)
    player_bday = models.DateField(null=True,blank=True)
    player_logo = models.TextField(null=True,blank=True)
    def get_name(self):
        return self.player_name

    def __str__(self):
        return f"{self.player_key}:{self.player_name}"


@admin.register(Players)
class PlayersAdmin(admin.ModelAdmin):
    pass



class PlayerStats(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid4)
    vhost = models.ForeignKey('parameters.VHost', on_delete=models.CASCADE, related_name='at_playerstats')
    inserted_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    player = models.ForeignKey(Players, on_delete=models.CASCADE)
    season = models.CharField(max_length=4)
    type = models.TextField()
    rank = models.IntegerField()
    titles = models.IntegerField()
    matches_won = models.IntegerField()
    matches_lost = models.IntegerField()
    hard_won = models.IntegerField()
    hard_lost = models.IntegerField()
    clay_won = models.IntegerField()
    clay_lost = models.IntegerField()
    grass_won = models.IntegerField()
    grass_lost = models.IntegerField()
    def __str__(self):
        return f"{self.player}:{self.season}: {self.type}"

@admin.register(PlayerStats)
class PlayerStatsAdmin(admin.ModelAdmin):
    pass

