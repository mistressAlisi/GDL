import datetime
import uuid

from django.contrib import admin
from django.db import models


class Group(models.Model):
    class Meta:
        ordering = ["slug"]
        unique_together = (('name','vhost'))
    uuid = models.UUIDField(primary_key=True,default=uuid.uuid4)
    vhost = models.ForeignKey('parameters.VHost',on_delete=models.CASCADE,related_name='ath_groups')
    slug = models.SlugField(verbose_name="Group Slug",null=True,blank=True)
    icon = models.CharField(verbose_name="Icon (use HTML!)",null=True,blank=True)
    name = models.CharField(verbose_name="Sport Group Name",null=True,blank=True)
    generic_icon = models.CharField(verbose_name="Generic FA Icon",help_text="Will be used for sports leagues that do not have a custom icon.",null=True,blank=True)
    card_trending_img = models.ImageField(verbose_name="Trending Card Image",null=True,blank=True)
    has_periods = models.BooleanField(default=False,verbose_name="Does the Sport Group have Period-based Props (for display in sportsbook)")
    has_teasers = models.BooleanField(default=False,verbose_name="Does the Sport group have Teaser bets")
    teaser_pts_mask = models.CharField(blank=True,null=True, verbose_name="Mask for selecting the points in Teaser bets (hint: amf, bab..) just like core sports maps.")
    bookmaker_uses_own_template = models.BooleanField(verbose_name="Bookmaker uses own template File for Lines",default=False)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"Group: {self.name}"

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    pass

class Country(models.Model):
    class Meta:
        ordering = ["name"]
        unique_together = (('name','vhost'))
    uuid = models.UUIDField(primary_key=True,default=uuid.uuid4)
    vhost = models.ForeignKey('parameters.VHost', on_delete=models.CASCADE,related_name="ath_countries")
    icon = models.CharField(verbose_name="Font Awesome Icon",null=True,blank=True)
    flag = models.FileField(verbose_name="Country Flag",null=True,blank=True)
    name = models.CharField(verbose_name="Country Name")
    code = models.CharField(verbose_name="Country Code")
    def __str__(self):
        return f"Country: {self.name}"

@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    pass

class Season(models.Model):
    class Meta:
        ordering = ['-season_key']
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    vhost = models.ForeignKey('parameters.VHost', on_delete=models.CASCADE,related_name="ath_seasons")
    season_key = models.CharField(verbose_name="Season Key", help_text="Season key (YYYY)", default='')
    name = models.CharField(verbose_name="Season Name")

    active = models.BooleanField(default=True)
    def __str__(self):
        return f"Season: {self.season_key}"


@admin.register(Season)
class SeasonAdmin(admin.ModelAdmin):
    pass


class Sport(models.Model):
    class Meta:
        ordering = ["key","priority"]
        unique_together = ()

    uuid = models.UUIDField(primary_key=True,default=uuid.uuid4)
    key = models.TextField(verbose_name="Key")
    apisport_id = models.CharField(verbose_name="API Sport ID",help_text="API Sport ID",null=True,db_index=True,blank=True)
    apitennis_id = models.CharField(verbose_name="API Sport ID",help_text="API Sport ID",null=True,db_index=True,blank=True)
    vhost = models.ForeignKey('parameters.VHost', on_delete=models.CASCADE,related_name="ath_sports")
    group = models.ForeignKey(Group,on_delete=models.RESTRICT,verbose_name="Sport Grouping",blank=True,null=True)
    title = models.TextField(verbose_name="Title")
    card_logo = models.FileField(verbose_name="Sports/League Logo for UI",blank=True,null=True)
    large_logo = models.FileField(verbose_name="Sports/League Large Logo for UI", blank=True, null=True)
    description = models.TextField(verbose_name="Description")
    active = models.BooleanField(verbose_name="Active",default=True)
    has_outrights = models.BooleanField(verbose_name="Has Outrights",default=True)
    has_wagers = models.BooleanField(verbose_name="Has Wagers",default=True)
    skip_index_display = models.BooleanField(verbose_name="Skip this League in the Sports index view.",default=False)
    country = models.ForeignKey(Country,on_delete=models.RESTRICT,verbose_name="League Country",blank=True,null=True)
    featured = models.BooleanField(default=False,verbose_name="Featured",help_text="Featured leagues show up in a separate tab in the player's ui.")
    priority = models.IntegerField(verbose_name="Priority #",help_text="Feature/Order Priority (lowest first)",default=0)
    wager_limit = models.IntegerField(verbose_name="Max Wager Limit",help_text="Maximum Wager allowed in this sport/league",default=10000)
    min_wager = models.IntegerField(verbose_name="Min Wager Limit", help_text="Minimum Wager allowed in this sport/league", default=100)
    season = models.ForeignKey(Season,on_delete=models.RESTRICT,verbose_name="Season",blank=True,null=True)
    start_date = models.DateField(verbose_name="Start Date",blank=True,null=True)
    end_date = models.DateField(verbose_name="End Date",null=True,blank=True)

    def get_season_start_delta(self):
        current_timedelta = datetime.datetime.now().date() - self.start_date
        return current_timedelta

    def get_season_week(self):
        ctd = self.get_season_start_delta()
        return ctd.days//7


    def __str__(self):
        return f"Sport: {self.title} in {self.group}"


@admin.register(Sport)
class SportAdmin(admin.ModelAdmin):
    search_fields = ["title","key"]
    list_filter = ["group","has_outrights","active","featured"]

class SportsGroupView(models.Model):
    class Meta:
        db_table = "sports_sport_group_view"
        managed = False
    id = models.UUIDField(primary_key=True)
    group_slug = models.SlugField()
    group_name = models.TextField()
    group_icon = models.TextField()
    sport_key = models.TextField()
    sport_title = models.TextField()
    sport_card_logo = models.FileField()
    sport_large_logo = models.FileField()
    sport_description = models.TextField()
    sport_featured = models.BooleanField()