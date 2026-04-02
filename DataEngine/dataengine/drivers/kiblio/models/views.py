from django.contrib import admin
from django.db import models

from dataengine.drivers.kiblio.models import Fixture


class FixtureOutcomeView(models.Model):
    class Meta:
        db_table = 'kibl_fixture_outcome_view'
        managed = False
    uuid = models.UUIDField(primary_key=True)
    fixture_id = models.TextField()
    outcome_routing_key = models.TextField()
    routing_key = models.TextField()
    name = models.TextField()
    vhost_id = models.TextField()
    fixture_type_id = models.TextField()
    league_id = models.TextField()
    season_id = models.TextField()
    state_id = models.TextField()
    state_name = models.TextField()
    state_abrv = models.TextField()
    segment_name = models.TextField()
    segment_abrv = models.TextField()
    segment_id = models.TextField()
    clock = models.TextField()
    is_current = models.BooleanField()
    is_start_game = models.BooleanField()
    is_end_game = models.BooleanField()
    is_start_segment = models.BooleanField()
    is_end_segment = models.BooleanField()

@admin.register(FixtureOutcomeView)
class FixtureOutcomeViewAdmin(admin.ModelAdmin):
    pass

