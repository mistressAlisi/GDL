import uuid

from django.contrib import admin
from django.db import models

from players.models import Player as Sys_Player
from sports.models import Sport, Season


# class APISportsAPISettings(models.Model):
#     uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
#     api_key_str = models.CharField(verbose_name="API Key",help_text="API Key for 'API sports' Access",default='')
#     update_frequency = models.IntegerField(verbose_name="Update Interval",help_text="Match Data Update Interval. BEWARE: This setting can chew through a lot of API requests per day if set to a low threshold!",default=600)
#     requests_remaining = models.IntegerField(help_text="API KEY Requests remaining before period reset.",verbose_name="Requests Remaining",default=0,blank=True,null=True)

# @admin.register(APISportsAPISettings)
# class APISportsAPISettingsAdmin(admin.ModelAdmin):
#     pass

class Season(models.Model):
    class Meta:
        ordering = ['-season_key']
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    vhost = models.ForeignKey('parameters.VHost', on_delete=models.CASCADE,related_name="as_season")
    season_key = models.CharField(verbose_name="Season Key", help_text="Season key (YYYY)", default='')
    active = models.BooleanField(default=True)
    def get_season_key_full(self):
        try:
            sk = int(self.season_key)-1
            return f"{sk}-{self.season_key}"
        except ValueError:
            return f"{self.season_key}"

    def __str__(self):
        return f"Season: {self.season_key}"


@admin.register(Season)
class SeasonAdmin(admin.ModelAdmin):
    pass


class League(models.Model):
    class Meta:
        ordering = ['name']
        unique_together = (("id","sport_mask","vhost"))

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    vhost = models.ForeignKey('parameters.VHost', on_delete=models.CASCADE,related_name='as_league')
    id = models.IntegerField(verbose_name="API League ID")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    name = models.CharField(verbose_name="League Name", help_text="League Name", default='')
    logo = models.TextField(verbose_name="League Logo", help_text="League Logo", default='')
    country_name = models.CharField(verbose_name="Country Name", default='')
    country_code = models.CharField(verbose_name="Country Code", default='')
    flag = models.TextField(verbose_name="Country Flag", null=True)
    seasons = models.JSONField(verbose_name="Seasons Data", default=dict)
    season_override = models.TextField(verbose_name="Season value override", null=True,blank=True)
    active = models.BooleanField(default=False)
    needs_plusone = models.BooleanField(default=False,verbose_name="Add One year to Season map in APIsports calls")
    sport_mask = models.TextField(verbose_name="Sport Mask", help_text="Sport Mask", default='')
    sync_sport_mask = models.TextField(null=True,blank=True,verbose_name="Sync Sport Mask to match Groups in DataEngine"),
    statistics_enabled = models.BooleanField(default=False)
    player_stats_enabled = models.BooleanField(default=False)
    standings_enabled = models.BooleanField(default=False)
    players_enabled = models.BooleanField(default=False)
    top_scorers_enabled = models.BooleanField(default=False)
    top_assists_enabled = models.BooleanField(default=False)
    injuries_enabled = models.BooleanField(default=False)
    predictions_enabled = models.BooleanField(default=False)
    odds_enabled = models.BooleanField(default=False)
    def __str__(self):
        return f"{self.name} (ID: {self.id})"

@admin.register(League)
class LeagueAdmin(admin.ModelAdmin):
    list_filter = ["name","sport_mask","country_code","active"]
    search_fields = ["name"]

class CoreSportMap(models.Model):
    class Meta:
        unique_together = (('sport','league','vhost'))
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    vhost = models.ForeignKey('parameters.VHost', on_delete=models.CASCADE)
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE)
    league = models.ForeignKey(League, on_delete=models.CASCADE)
    sport_mask = models.CharField(verbose_name="Sport Mask", help_text="Sport Mask: Must match the API class to be picked up by the map_***games commands/tasks.",default="CHANGEME")
    stage_mask = models.CharField(verbose_name="Stage Mask", help_text="Stage Mask: Matches must have THIS STAGE in the API to be linked up into the Athena League.", null=True,blank=True)
    def __str__(self):
        return f"CoreSports Map: Athena[{self.sport}]<-->API[{self.league}]"
@admin.register(CoreSportMap)
class CoreSportMapAdmin(admin.ModelAdmin):
    pass


class Team(models.Model):
    class Meta:
        ordering = ['name']
        unique_together = (('id','sport_mask','vhost'))
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    vhost = models.ForeignKey('parameters.VHost', on_delete=models.CASCADE)
    id = models.IntegerField(verbose_name="API Team ID")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    name = models.CharField(verbose_name="Team Name", help_text="Team Name",null=True, blank=True)
    logo = models.TextField(verbose_name="Team Logo", help_text="Team Logo", null=True, blank=True)
    sport_mask = models.CharField(verbose_name="Sport Mask", help_text="Sport Mask", default='')
    country_name = models.CharField(verbose_name="Country Name", default='',null=True,blank=True)
    country_code = models.CharField(verbose_name="Country Code", default='',null=True,blank=True)
    flag = models.TextField(verbose_name="Country Flag", default='',null=True,blank=True)
    city = models.CharField(verbose_name="Team City", help_text="Team Home City", null=True, blank=True)
    owner = models.CharField(verbose_name="Team Owner", help_text="Team Owner", null=True, blank=True)
    stadium = models.CharField(verbose_name="Team Stadium", help_text="Team Stadium", null=True, blank=True)
    established = models.IntegerField(verbose_name="Team Established", null=True, blank=True)
    need_sync_players = models.BooleanField(default=True)
    need_sync_player_stats = models.BooleanField(default=True)
    def get_name(self):
        return self.name
    def __str__(self):
        return f"{self.name} (ID: {self.id}) (Sport Mask: {self.sport_mask})"


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    search_fields = ["name"]
    list_filter = ["sport_mask","country_name"]

class TeamLeagues(models.Model):
    class Meta:
        unique_together = (("team","league","sport_mask",'vhost'))
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    vhost = models.ForeignKey('parameters.VHost', on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    league = models.ForeignKey(League, on_delete=models.CASCADE)
    sport_mask = models.CharField(verbose_name="Sport Mask", help_text="Sport Mask", default='')

@admin.register(TeamLeagues)
class TeamLeaguesAdmin(admin.ModelAdmin):
    search_fields = ["team__name","league__name","sport_mask"]
    list_filter = ["league","team","sport_mask"]





class Player(models.Model):
    class Meta:
        ordering = ['name']
        unique_together = (('id','league','vhost'))

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    vhost = models.ForeignKey('parameters.VHost', on_delete=models.CASCADE)
    id = models.IntegerField( verbose_name="API Player ID")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    name = models.CharField(verbose_name="Player Name", help_text="Player Name",null=True, blank=True)
    firstname = models.CharField(verbose_name="Player First Name", help_text="Player Name", null=True, blank=True)
    lastname = models.CharField(verbose_name="Player Last Name", help_text="Player Name", null=True, blank=True)
    nationality = models.CharField(verbose_name="Player Nationality", help_text="Player Nationality", null=True, blank=True)
    image = models.TextField(verbose_name="Player Image", help_text="Player Image", null=True, blank=True)
    team = models.ForeignKey(Team, on_delete=models.RESTRICT,null=True,blank=True)
    season = models.ForeignKey(Season, on_delete=models.RESTRICT,null=True,blank=True)
    league = models.ForeignKey(League, on_delete=models.RESTRICT,null=True)
    height = models.CharField(verbose_name="Player Height", null=True)
    weight = models.CharField(verbose_name="Player Weight", null=True)
    group = models.CharField(verbose_name="Player Group", null=True)
    college = models.CharField(verbose_name="Player College", null=True)
    position = models.CharField(verbose_name="Player Position", null=True)
    number = models.CharField(verbose_name="Player Number", null=True)
    salary = models.CharField(verbose_name="Player Salary", null=True)
    experience = models.CharField(verbose_name="Player Experience", null=True)
    age = models.CharField(verbose_name="Player Age", null=True)
    birth_place = models.CharField(verbose_name="Player Birth Place", null=True)
    birth_date = models.CharField(verbose_name="Player Birth Date", null=True)
    birth_country = models.CharField(verbose_name="Player Birth Country", null=True)
    injured = models.BooleanField(verbose_name="Player Injured", default=False)
    need_sync_player_stats = models.BooleanField(default=True)
    def get_name(self):
        return self.name
    def get_time(self):
        return self.commence_time
    def __str__(self):
        return f"{self.name} (ID: {self.id}) (Team: {self.team.name})"


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    search_fields = ["name","team"]
    list_filter = ["name","team","season"]



class PlayerStats(models.Model):
    class Meta:
        unique_together = (('player', 'season', 'group','name','vhost'))

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    player = models.ForeignKey(Player, on_delete=models.RESTRICT)
    vhost = models.ForeignKey('parameters.VHost', on_delete=models.CASCADE)
    season = models.ForeignKey(Season, on_delete=models.RESTRICT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    group =  models.CharField(verbose_name="Stat Group", null=True)
    name = models.CharField(verbose_name="Stat Name", null=True)
    value = models.CharField(verbose_name="Stat Value", null=True)
    def __str__(self):
        return f"{self.player} (Season: {self.season}) (Group: {self.group}): {self.name}: {self.value}"

@admin.register(PlayerStats)
class PlayerStatsAdmin(admin.ModelAdmin):
    list_filter = ["season","group"]
    search_fields = ["name","group","player__name"]



class Venue(models.Model):
    class Meta:
        ordering = ['-name']

        unique_together = (('id','vhost'))
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    vhost = models.ForeignKey('parameters.VHost', on_delete=models.CASCADE)
    id = models.IntegerField( verbose_name="API Venue ID")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    name = models.CharField(verbose_name="Venue Name", help_text="Venue Name",null=True, blank=True)
    address = models.CharField(verbose_name="Venue Address", help_text="Venue Address",null=True, blank=True)
    city = models.CharField(verbose_name="Venue City", help_text="Venue City",null=True, blank=True)
    capacity = models.IntegerField(verbose_name="Venue Capacity", help_text="Venue Capacity",null=True, blank=True)
    surface = models.CharField(verbose_name="Venue Surface", help_text="Venue Surface",null=True, blank=True)
    image = models.TextField(verbose_name="Venue Image", help_text="Venue Image", null=True, blank=True)
    active = models.BooleanField(default=True)
    def __str__(self):
        return f"{self.name} (ID: {self.id})"


@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    pass

class TeamVenue(models.Model):
    class Meta:
        unique_together = (('team', 'venue','vhost'))
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    vhost = models.ForeignKey('parameters.VHost', on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.RESTRICT)
    venue = models.ForeignKey(Venue, on_delete=models.RESTRICT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"{self.team.name} plays in {self.venue.name}"