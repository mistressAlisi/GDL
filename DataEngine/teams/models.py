import uuid

from django.contrib import admin
from django.db import models


from sports.models import Sport, Country


# Create your models here.

class Team(models.Model):
    class Meta:
        ordering = ['name']
        permissions = [('can_relink_team','Can View/Edit API Link for Teams')]
        unique_together = (('key','apisports_id'))
    uuid = models.UUIDField(primary_key=True,default=uuid.uuid4)
    vhost = models.ForeignKey('parameters.VHost',null=True,blank=True,on_delete=models.CASCADE,related_name='sp_teams')
    key = models.SlugField(verbose_name="Key")
    apisports_id = models.IntegerField(null=True,blank=True,db_index=True,verbose_name="API sports Team ID")
    name = models.TextField(verbose_name="Team Name")
    card_logo = models.FileField(verbose_name="Sports/League Logo for UI", blank=True, null=True,upload_to="teams/cards/")
    large_logo = models.FileField(verbose_name="Sports/League Large Logo for UI", blank=True, null=True,upload_to="teams/large/")
    total_games = models.IntegerField(default=0,verbose_name="Recorded Games")
    total_wins = models.IntegerField(default=0, verbose_name="Recorded Wins")
    total_losses = models.IntegerField(default=0, verbose_name="Recorded Losses")
    total_draws = models.IntegerField(default=0, verbose_name="Recorded Draws")
    last_game = models.DateTimeField(verbose_name="Last Match Time",blank=True,null=True)
    created = models.DateTimeField(verbose_name="Team Created",auto_now_add=True)
    updated = models.DateTimeField(verbose_name="Team Last Updated",auto_now=True)
    #sport = models.ForeignKey(Sport, on_delete=models.RESTRICT,null=True)
    country = models.ForeignKey(Country, on_delete=models.SET_NULL,null=True,blank=True)
    flag = models.TextField(verbose_name="Country Flag", default='',null=True,blank=True)
    city = models.CharField(verbose_name="Team City", help_text="Team Home City", null=True, blank=True)
    owner = models.CharField(verbose_name="Team Owner", help_text="Team Owner", null=True, blank=True)
    stadium = models.CharField(verbose_name="Team Stadium", help_text="Team Stadium", null=True, blank=True)
    established = models.IntegerField(verbose_name="Team Established", null=True, blank=True)
    team_colour_primary = models.TextField(verbose_name="Team Colour, Primary (HEX, ommit #)",null=True,blank=True)
    team_colour_secondary = models.TextField(verbose_name="Team Colour, Secondary (HEX, ommit #)", null=True, blank=True)
    team_colour_tertiary = models.TextField(verbose_name="Team Colour, Tertiary (HEX, ommit #)", null=True, blank=True)


    def get_name(self):
        return self.name or self.key.replace('-', ' ').title()
    def __str__(self):
        if self.apisports_id:
            return f"{self.get_name()} (id: {self.apisports_id})"
        else:
            return f"{self.get_name()}"

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    search_fields = ["name","key"]


class TeamSport(models.Model):
    class Meta:
        unique_together = ()
    uuid = models.UUIDField(primary_key=True,default=uuid.uuid4)
    vhost = models.ForeignKey('parameters.VHost',null=True,blank=True,on_delete=models.CASCADE,related_name='tms_teams')
    team = models.ForeignKey(Team, on_delete=models.CASCADE,null=True,blank=True)
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE,null=True,blank=True)
    active = models.BooleanField(default=True)
    def __str__(self):
        return f"{self.team} Plays in {self.sport.title}"
@admin.register(TeamSport)
class TeamSportAdmin(admin.ModelAdmin):
    list_filter = ["sport","team"]
    search_fields = ["sport","team"]



class AccountTeamFavourite(models.Model):
    class Meta:
        unique_together = (("account", "team"),)
        ordering = ['account', 'team']
    uuid = models.UUIDField(primary_key=True,default=uuid.uuid4)
    account = models.ForeignKey('account.Account',on_delete=models.CASCADE)
    team = models.ForeignKey(Team,on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Account #{self.account.acctnum} follows {self.team.name}"

@admin.register(AccountTeamFavourite)
class AccountTeamFavouriteAdmin(admin.ModelAdmin):
    search_fields = ["account","team"]
