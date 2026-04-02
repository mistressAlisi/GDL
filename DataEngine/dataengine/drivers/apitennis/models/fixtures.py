from uuid import uuid4

from django.contrib import admin
from django.db import models
from dataengine.drivers.apitennis.models.players import Players
from dataengine.drivers.apitennis.models.tournaments import EventType, Tournament


class Fixture(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid4)
    vhost = models.ForeignKey('parameters.VHost', on_delete=models.CASCADE,related_name='at_fixture')
    inserted_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    event_key = models.IntegerField(db_index=True)
    event_date = models.DateField(null=True,blank=True)
    event_time = models.TimeField(null=True,blank=True)
    commence_time = models.DateTimeField(null=True,blank=True)
    event_first_player = models.ForeignKey(Players, on_delete=models.CASCADE,related_name='at_fixture_first_player')
    event_second_player = models.ForeignKey(Players, on_delete=models.CASCADE,related_name='at_fixture_second_player')
    event_final_result = models.TextField(null=True,blank=True),
    event_game_result  = models.TextField(null=True,blank=True),
    event_serve = models.TextField(null=True,blank=True),
    event_winner = models.ForeignKey(Players, on_delete=models.CASCADE,null=True,related_name='at_fixture_winner')
    event_status = models.TextField(null=True,blank=True)
    event_type = models.ForeignKey(EventType, on_delete=models.CASCADE,related_name='at_fixture_type')
    tournament =  models.ForeignKey(Tournament, on_delete=models.CASCADE,related_name='at_fixture',null=True)
    tournament_round = models.TextField(null=True,blank=True)
    tournament_season = models.TextField(null=True,blank=True)
    event_live = models.IntegerField(default=0)
    event_qualification = models.BooleanField(default=False,null=True,blank=True)
    pointbypoint = models.JSONField(default=dict)
    scores = models.JSONField(default=dict)
    statistics = models.JSONField(default=dict)
    _being_processed = models.BooleanField(default=False)
    def get_name(self):
        return f"{self.event_second_player.player_name} vs {self.event_first_player.player_name} ({self.event_date} {self.event_time})"
    def get_time(self):
        return self.commence_time
    def __str__(self):
        return str(self.event_key)

@admin.register(Fixture)
class FixtureAdmin(admin.ModelAdmin):
    pass

class FixtureView(models.Model):
    class Meta:
        managed = False
        db_table = 'apitennis_fixture_view'
    uuid = models.UUIDField(primary_key=True, default=uuid4)
    vhost = models.ForeignKey('parameters.VHost', on_delete=models.CASCADE,related_name='+')
    inserted_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    event_key = models.IntegerField(db_index=True)
    event_date = models.DateField(null=True,blank=True)
    event_time = models.TimeField(null=True,blank=True)
    event_datetime = models.DateTimeField(null=True,blank=True)
    commence_time = models.DateTimeField(null=True,blank=True)
    event_first_player = models.ForeignKey(Players, on_delete=models.CASCADE,related_name='+')
    event_second_player = models.ForeignKey(Players, on_delete=models.CASCADE,related_name='+')
    event_final_result = models.TextField(null=True,blank=True),
    event_game_result  = models.TextField(null=True,blank=True),
    event_serve = models.TextField(null=True,blank=True),
    event_winner = models.ForeignKey(Players, on_delete=models.CASCADE,null=True,related_name='+')
    event_status = models.TextField(null=True,blank=True)
    event_type = models.ForeignKey(EventType, on_delete=models.CASCADE,related_name='+')
    tournament =  models.ForeignKey(Tournament, on_delete=models.CASCADE,related_name='+',null=True)
    tournament_round = models.TextField(null=True,blank=True)
    tournament_season = models.TextField(null=True,blank=True)
    event_live = models.IntegerField(default=0)
    event_qualification = models.BooleanField(default=False,null=True,blank=True)
    pointbypoint = models.JSONField(default=dict)
    scores = models.JSONField(default=dict)
    statistics = models.JSONField(default=dict)
    def get_name(self):
        return f"{self.event_second_player.player_name} vs {self.event_first_player.player_name} ({self.event_date} {self.event_time})"
    def get_time(self):
        return self.commence_time
    def __str__(self):
        return str(self.event_key)

@admin.register(FixtureView)
class FixtureViewAdmin(admin.ModelAdmin):
    pass