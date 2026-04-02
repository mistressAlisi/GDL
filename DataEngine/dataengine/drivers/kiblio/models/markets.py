import uuid
from django.contrib import admin
from django.db import models


from parameters.models import VHost
from django.db.models import ForeignKey

from . import Sides, Sportsbook
from .base import League, Season, Location, FixtureType, Participant, MarketType, Segment, MarketStatus,BetType
from .fixtures import Fixture,FixtureParticipants


class FixtureMarket(models.Model):
    class Meta:
        ordering = ["updated_at"]
    uuid = models.UUIDField(primary_key=True,default=uuid.uuid4)
    vhost = models.ForeignKey(VHost, on_delete=models.CASCADE)
    market_id = models.BigIntegerField()
    fixture = models.ForeignKey(Fixture, on_delete=models.CASCADE)
    league = models.ForeignKey(League, on_delete=models.CASCADE,null=True)
    participant= models.ForeignKey(Participant, on_delete=models.CASCADE)
    side = models.ForeignKey(Sides, on_delete=models.CASCADE)
    sportsbook = models.ForeignKey(Sportsbook, on_delete=models.CASCADE)
    market_type = models.ForeignKey(MarketType, on_delete=models.CASCADE)
    segment = models.ForeignKey(Segment, on_delete=models.CASCADE)
    market_status = models.ForeignKey(MarketStatus, on_delete=models.CASCADE)
    betting_type = models.ForeignKey(BetType,on_delete=models.CASCADE)
    routing_key = models.TextField(db_index=True,null=True)
    point = models.DecimalField(decimal_places=2, max_digits=5,default=0)
    price_american = models.IntegerField(default=0)
    price_fraction = models.CharField(default="0")
    max_limit = models.DecimalField(decimal_places=2, max_digits=5,default=0)
    is_live = models.BooleanField(default=False)
    is_opener = models.BooleanField(default=False)
    is_previous = models.BooleanField(default=False)
    is_current = models.BooleanField(default=False)
    is_main = models.BooleanField(default=False)
    inserted_on = models.DateTimeField(auto_now_add=True)
    inserted_on_epoch = models.BigIntegerField(null=True)
    info = models.JSONField(default=dict)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"{self.fixture} | {self.market_id} | {self.market_type} | {self.segment} [{self.sportsbook}] in VHost {self.vhost}"


@admin.register(FixtureMarket)
class FixtureMarketAdmin(admin.ModelAdmin):
    list_filter = ["fixture","participant","side","sportsbook","segment","market_status","betting_type"]







