from django.contrib import admin
from django.db import models
import uuid

from django.db.models import ForeignKey

from parameters.models import VHost


class Sport(models.Model):
    class Meta:
        unique_together = (('vhost','sport_id'))
    uuid = models.UUIDField(primary_key=True,default=uuid.uuid4)
    sport_id = models.IntegerField(default=0)
    vhost = models.ForeignKey(VHost, on_delete=models.CASCADE)
    name = models.TextField(null=True)
    abrv = models.TextField(null=True)
    inserted_on = models.DateTimeField(null=True)
    inserted_on_epoch = models.BigIntegerField(null=True)
    active = models.BooleanField(default=True)
    def get_name(self):
        return self.name
    def __str__(self):
        return f"{self.sport_id} | {self.name} in VHost {self.vhost}"

@admin.register(Sport)
class SportAdmin(admin.ModelAdmin):
    list_filter = ["sport_id","vhost"]

class Region(models.Model):
    uuid = models.UUIDField(primary_key=True,default=uuid.uuid4)
    vhost = models.ForeignKey(VHost, on_delete=models.CASCADE)
    region_id = models.IntegerField(default=0)
    name = models.TextField(null=True)
    abrv = models.TextField(null=True)
    inserted_on = models.DateTimeField(null=True)
    inserted_on_epoch = models.BigIntegerField(null=True)
    def get_name(self):
        return self.name
    def __str__(self):
        return f"{self.region_id} | {self.name} in VHost {self.vhost}"

@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_filter = ["region_id", "vhost"]


class League(models.Model):
    uuid = models.UUIDField(primary_key=True,default=uuid.uuid4)
    vhost = models.ForeignKey(VHost, on_delete=models.CASCADE)
    league_id = models.IntegerField(default=0)
    sport = ForeignKey("Sport", on_delete=models.CASCADE)
    region = models.ForeignKey("Region", on_delete=models.CASCADE)
    name = models.TextField(null=True)
    abrv = models.TextField(null=True)
    combined_line_type_id = models.IntegerField(default=0)
    inserted_on = models.DateTimeField(null=True)
    inserted_on_epoch = models.BigIntegerField(null=True)
    def get_name(self):
        return self.name
    def __str__(self):
        return f"{self.region_id} | {self.name} in VHost {self.vhost}"

@admin.register(League)
class LeagueAdmin(admin.ModelAdmin):
    list_filter = ["league_id", "vhost","sport","region"]



class MarketGenres(models.Model):
    uuid = models.UUIDField(primary_key=True,default=uuid.uuid4)
    vhost = models.ForeignKey(VHost, on_delete=models.CASCADE)
    market_genre_id = models.IntegerField(default=0)
    name = models.TextField(null=True)
    abrv = models.TextField(null=True)
    combined_line_type_id = models.IntegerField(default=0)
    inserted_on = models.DateTimeField(null=True)
    inserted_on_epoch = models.BigIntegerField(null=True)

    def __str__(self):
        return f"{self.market_genre_id} | {self.name} in VHost {self.vhost}"

@admin.register(MarketGenres)
class MarketGenresAdmin(admin.ModelAdmin):
    list_filter = ["market_genre_id", "vhost"]



class MarketType(models.Model):
    uuid = models.UUIDField(primary_key=True,default=uuid.uuid4)
    vhost = models.ForeignKey(VHost, on_delete=models.CASCADE)
    market_type_id = models.IntegerField(default=0)
    name = models.TextField(null=True)
    abrv = models.TextField(null=True)
    combined_line_type_id = models.IntegerField(default=0)
    inserted_on = models.DateTimeField(null=True)
    inserted_on_epoch = models.BigIntegerField(null=True)
    is_active_internal = models.BooleanField(default=False)
    is_active_external = models.BooleanField(default=False)
    genre = models.ForeignKey(MarketGenres, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.market_type_id} | {self.name} in VHost {self.vhost}"

@admin.register(MarketType)
class MarketTypeAdmin(admin.ModelAdmin):
    list_filter = ["market_type_id", "vhost"]

class MarketTypeSport(models.Model):
    uuid = models.UUIDField(primary_key=True,default=uuid.uuid4)
    market_type = models.ForeignKey(MarketType,on_delete=models.CASCADE)
    for_sport = models.ForeignKey(Sport, on_delete=models.CASCADE)

@admin.register(MarketTypeSport)
class MarketTypeSportAdmin(admin.ModelAdmin):
    pass

class MarketStatus(models.Model):
    uuid = models.UUIDField(primary_key=True,default=uuid.uuid4)
    vhost = models.ForeignKey(VHost, on_delete=models.CASCADE)
    market_status_id = models.IntegerField(default=0)
    name = models.TextField(null=True)
    abrv = models.TextField(null=True)
    inserted_on = models.DateTimeField(null=True)

@admin.register(MarketStatus)
class MarketStatusAdmin(admin.ModelAdmin):
    pass

class BetType(models.Model):
    uuid = models.UUIDField(primary_key=True,default=uuid.uuid4)
    vhost = models.ForeignKey(VHost, on_delete=models.CASCADE)
    betting_type_id = models.IntegerField(default=0)
    name = models.TextField(null=True)
    abrv = models.TextField(null=True)
    combined_line_type_id = models.IntegerField(default=0)
    inserted_on = models.DateTimeField(null=True)
    inserted_on_epoch = models.BigIntegerField(null=True)
    def __str__(self):
        return f"{self.betting_type_id} | {self.name} in VHost {self.vhost}"

@admin.register(BetType)
class BetTypeAdmin(admin.ModelAdmin):
    list_filter = ["betting_type_id", "vhost"]

class Segment(models.Model):
    uuid = models.UUIDField(primary_key=True,default=uuid.uuid4)
    vhost = models.ForeignKey(VHost, on_delete=models.CASCADE)
    segment_id = models.IntegerField(default=0)
    name = models.TextField(null=True)
    abrv = models.TextField(null=True)
    inserted_on = models.DateTimeField(null=True)
    inserted_on_epoch = models.BigIntegerField(null=True)
    def __str__(self):
        return f"{self.segment_id} | {self.name} in VHost {self.vhost}"

@admin.register(Segment)
class SegmentAdmin(admin.ModelAdmin):
    list_filter = ["segment_id", "vhost"]

class Season(models.Model):
    uuid = models.UUIDField(primary_key=True,default=uuid.uuid4)
    vhost = models.ForeignKey(VHost, on_delete=models.CASCADE)
    season_id = models.IntegerField(default=0)
    name = models.TextField(null=True)
    abrv = models.TextField(null=True)
    inserted_on = models.DateTimeField(null=True)
    inserted_on_epoch = models.BigIntegerField(null=True)
    def __str__(self):
        return f"{self.season_id} | {self.name} in VHost {self.vhost}"

@admin.register(Season)
class SeasonAdmin(admin.ModelAdmin):
    list_filter = ["season_id", "vhost"]


class State(models.Model):
    uuid = models.UUIDField(primary_key=True,default=uuid.uuid4)
    vhost = models.ForeignKey(VHost, on_delete=models.CASCADE)
    state_id = models.IntegerField(default=0)
    name = models.TextField(null=True)
    abrv = models.TextField(null=True)

    inserted_on = models.DateTimeField(null=True)
    inserted_on_epoch = models.BigIntegerField(null=True)
    def __str__(self):
        return f"{self.state_id} | {self.name} in VHost {self.vhost}"

@admin.register(State)
class StateAdmin(admin.ModelAdmin):
    list_filter = ["state_id", "vhost"]


class Participant(models.Model):
    uuid = models.UUIDField(primary_key=True,default=uuid.uuid4)
    vhost = models.ForeignKey(VHost, on_delete=models.CASCADE)
    league = models.ForeignKey(League, on_delete=models.CASCADE)
    participant_id = models.IntegerField(default=0)
    parent_participant_id = models.IntegerField(default=0)
    name = models.TextField(null=True)
    abrv = models.TextField(null=True)
    mascot = models.TextField(null=True)
    morphed = models.BooleanField(default=False)
    inserted_on = models.DateTimeField(null=True)
    def get_name(self):
        return self.name
    def __str__(self):
        return f"{self.participant_id} | {self.name} in VHost {self.vhost}"

@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_filter = ["participant_id", "vhost","league"]


class Sides(models.Model):
    uuid = models.UUIDField(primary_key=True,default=uuid.uuid4)
    vhost = models.ForeignKey(VHost, on_delete=models.CASCADE)

    side_id = models.IntegerField(default=0)
    name = models.TextField(null=True)
    abrv = models.TextField(null=True)
    inserted_on = models.DateTimeField(null=True)

    def __str__(self):
        return f"{self.side_id} | {self.name} in VHost {self.vhost}"

@admin.register(Sides)
class SidesAdmin(admin.ModelAdmin):
    list_filter = ["side_id", "vhost"]

class Location(models.Model):
    uuid = models.UUIDField(primary_key=True,default=uuid.uuid4)
    vhost = models.ForeignKey(VHost, on_delete=models.CASCADE)
    location_id = models.IntegerField(default=0)
    name = models.TextField(null=True)
    abrv = models.TextField(null=True)
    inserted_on = models.DateTimeField(null=True)

    def __str__(self):
        return f"{self.location_id} | {self.name} in VHost {self.vhost}"

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_filter = ["location_id", "vhost"]


class FixtureType(models.Model):
    uuid = models.UUIDField(primary_key=True,default=uuid.uuid4)
    vhost = models.ForeignKey(VHost, on_delete=models.CASCADE)
    fixture_type_id = models.IntegerField(default=0)
    name = models.TextField(null=True)
    abrv = models.TextField(null=True)
    inserted_on = models.DateTimeField(null=True)

    def __str__(self):
        return f"{self.fixture_type_id} | {self.name} in VHost {self.vhost}"

@admin.register(FixtureType)
class FixtureTypeAdmin(admin.ModelAdmin):
    list_filter = ["fixture_type_id", "vhost"]


class Sportsbook(models.Model):
    uuid = models.UUIDField(primary_key=True,default=uuid.uuid4)
    vhost = models.ForeignKey(VHost, on_delete=models.CASCADE)
    feed_source_id = models.IntegerField(default=0)
    feed_type_id = models.IntegerField(default=0)
    name = models.TextField(null=True)
    tag = models.TextField(null=True)
    inserted_on = models.DateTimeField(null=True)
    active = models.BooleanField(default=False)
    def __str__(self):
        return f"{self.feed_source_id} | {self.name} in VHost {self.vhost}"

@admin.register(Sportsbook)
class SportsbookAdmin(admin.ModelAdmin):
    list_filter = ["feed_source_id", "vhost"]

