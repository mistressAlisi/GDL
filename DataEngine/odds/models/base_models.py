import uuid

from django.contrib import admin
from django.db import models

from matches.models import Match
from parameters.models import VHost
from sports.models import Sport
from teams.models import Team


class Bookmaker(models.Model):
    uuid = models.UUIDField(primary_key=True,default=uuid.uuid4)
    vhost = models.ForeignKey('parameters.VHost',on_delete=models.CASCADE,null=True,blank=True)
    key = models.SlugField(verbose_name="Key",unique=True)
    name = models.CharField(verbose_name="Bookmaker Name")
    card_logo = models.FileField(verbose_name="Sports/League Logo for UI", blank=True, null=True)
    large_logo = models.FileField(verbose_name="Sports/League Large Logo for UI", blank=True, null=True)
    feed_source_id = models.CharField(verbose_name="Feed Source ID",max_length=255,null=True,blank=True)
    feed_type_id = models.CharField(verbose_name="Feed Type ID",max_length=255,null=True,blank=True)
    active = models.BooleanField(verbose_name="Active", default=True)
    def get_name(self):
        if len(self.name) > 0:
            return self.name
        else:
            return self.key.title().replace("_"," ")
    def __str__(self):
        return f"Bookmaker: {self.get_name()} in region: {self.key}"

@admin.register(Bookmaker)
class BookmakerAdmin(admin.ModelAdmin):
    pass

# Create your models here.

class MatchOdds(models.Model):
    uuid = models.UUIDField(primary_key=True,default= uuid.uuid4)
    match = models.ForeignKey(Match,verbose_name="Match",on_delete=models.CASCADE,null=True)
    bookmaker = models.ForeignKey(Bookmaker,verbose_name="Bookmaker",on_delete=models.RESTRICT)
    vhost = models.ForeignKey('parameters.VHost', on_delete=models.CASCADE, null=True, blank=True)
    last_update = models.DateTimeField(verbose_name="Last Updated",auto_now=True)
    market = models.CharField(verbose_name="Bet Market",default="h2h")
    team = models.ForeignKey(Team, verbose_name="Team", related_name="+", on_delete=models.RESTRICT)
    price = models.DecimalField(verbose_name="Price",max_digits=20,decimal_places=5,default=0)
    def __str__(self):
        return f"Odds: Match: {self.match.id} -> Bookmaker: {self.bookmaker.key}, Team: {self.team.name}, Price: {self.price}, Updated: {self.last_update}"

@admin.register(MatchOdds)
class MatchOddsAdmin(admin.ModelAdmin):
    list_filter=["team","match","bookmaker"]


class MatchOddsSummary(models.Model):
    class Meta:
        unique_together = ["match","bookmaker","home_team","away_team"]
        ordering = ["-last_update"]
    uuid = models.UUIDField(primary_key=True,default= uuid.uuid4)
    vhost = models.ForeignKey(VHost,verbose_name="VHost",on_delete=models.CASCADE,null=True)
    match = models.ForeignKey(Match,verbose_name="Match",on_delete=models.CASCADE,null=True)
    bookmaker = models.ForeignKey(Bookmaker,verbose_name="Bookmaker",on_delete=models.RESTRICT,null=True)
    driver = models.TextField(db_index=True, null=True,blank=True)
    juice_pct = models.DecimalField(verbose_name="Juice Pct (%)",max_digits=20,decimal_places=5,default=0)
    last_update = models.DateTimeField(verbose_name="Last Updated",auto_now=True)
    home_team = models.ForeignKey(Team, verbose_name="Home Team", related_name="+", on_delete=models.RESTRICT,null=True,blank=True)
    home_price = models.DecimalField(verbose_name="Home Price",max_digits=20,decimal_places=5,default=0)
    home_price_fraction = models.CharField(verbose_name="Home Price Fraction",max_length=20,default=0)
    away_team = models.ForeignKey(Team, verbose_name="Away Team", related_name="+", on_delete=models.RESTRICT,null=True,blank=True)
    away_price = models.DecimalField(verbose_name="Away Price", max_digits=20, decimal_places=5,default=0)
    away_price_fraction = models.CharField(verbose_name="Away Price Fraction", max_length=20, default=0)
    draw_price = models.DecimalField(verbose_name="Draw Price", max_digits=20, decimal_places=5, default=0)
    draw_price_fraction = models.CharField(verbose_name="Draw Price Fraction", max_length=20, default=0)
    created_at = models.DateTimeField(verbose_name="Created At",auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="Updated At",auto_now=True)


    def __str__(self):
        return f"Odds Summary: Match: {self.match.id} -> Bookmaker: {self.bookmaker}, Home Team: {self.home_team.name}:{self.home_price} Away Team :{self.away_team.name}:{self.away_price} Draw: {self.draw_price}"



@admin.register(MatchOddsSummary)
class MatchOddsSummaryAdmin(admin.ModelAdmin):
    list_filter = ["home_team", "match", "bookmaker","away_team"]
    search_fields = ["match__uuid"]



class MatchOddsSummaryHistoryH2H(models.Model):
    class Meta:
        ordering = ["-last_update"]
    uuid = models.UUIDField(primary_key=True,default= uuid.uuid4)
    match = models.ForeignKey(Match,verbose_name="Match",on_delete=models.CASCADE,null=True)
    bookmaker = models.ForeignKey(Bookmaker,verbose_name="Bookmaker",on_delete=models.RESTRICT)
    parent = models.UUIDField(verbose_name="Parent Odds Summary Object",null=True,blank=True)
    created = models.DateTimeField(verbose_name="Match Odds created",auto_now=True)
    last_update = models.DateTimeField(verbose_name="Last Updated",auto_now=True)
    home_team = models.ForeignKey(Team, verbose_name="Home Team", related_name="+", on_delete=models.RESTRICT)
    home_price = models.DecimalField(verbose_name="Home Price",max_digits=20,decimal_places=5,default=0)
    draw_price = models.DecimalField(verbose_name="Draw Price", max_digits=20, decimal_places=5, default=0)
    away_team = models.ForeignKey(Team, verbose_name="Away Team", related_name="+", on_delete=models.RESTRICT)
    away_price = models.DecimalField(verbose_name="Away Price", max_digits=20, decimal_places=5)
    spread = models.DecimalField(verbose_name="Spread",max_digits=20,decimal_places=5,default=0)

    def __str__(self):
        return f"Odds H2H Summary: Match: {self.match.id} -> Bookmaker: {self.bookmaker.key}, Home Team: {self.home_team.name}:${self.home_price} Away Team :{self.away_team.name}:${self.away_price} Draw ${self.draw_price}"



@admin.register(MatchOddsSummaryHistoryH2H)
class MatchOddsSummaryHistoryH2HAdmin(admin.ModelAdmin):
    list_filter = ["home_team", "match", "bookmaker","away_team"]

class MatchOddsOutrightsSummary(models.Model):
    class Meta:
        unique_together = ["match","bookmaker","team"]
        ordering = ["-last_update"]
    uuid = models.UUIDField(primary_key=True,default= uuid.uuid4)
    match = models.ForeignKey(Match,verbose_name="Match",on_delete=models.CASCADE,null=True)
    bookmaker = models.ForeignKey(Bookmaker,verbose_name="Bookmaker",on_delete=models.RESTRICT)
    last_update = models.DateTimeField(verbose_name="Last Updated",auto_now=True)
    team = models.ForeignKey(Team, verbose_name="Team", related_name="+", on_delete=models.RESTRICT)
    price = models.DecimalField(verbose_name="Price",max_digits=20,decimal_places=5,default=0)
    def __str__(self):
        return f"Odds Outrights Summary: Match: {self.match.id} -> Bookmaker: {self.bookmaker.key}, Team: {self.team.name}:${self.price}."

@admin.register(MatchOddsOutrightsSummary)
class MatchOddsOutrightsSummaryAdmin(admin.ModelAdmin):
    list_filter = ["team", "match", "bookmaker"]


class MatchOddsOutrightsSummaryHistory(models.Model):
    class Meta:
        ordering = ["-last_update"]
    uuid = models.UUIDField(primary_key=True,default= uuid.uuid4)
    match = models.ForeignKey(Match,verbose_name="Match",on_delete=models.CASCADE,null=True)
    bookmaker = models.ForeignKey(Bookmaker,verbose_name="Bookmaker",on_delete=models.RESTRICT)
    parent = models.UUIDField(verbose_name="Parent Odds Summary Object", null=True, blank=True)
    created = models.DateTimeField(verbose_name="Date Created",auto_now=True)
    last_update = models.DateTimeField(verbose_name="Last Updated",auto_now=True)
    team = models.ForeignKey(Team, verbose_name="Team", related_name="+", on_delete=models.RESTRICT)
    price = models.DecimalField(verbose_name="Price",max_digits=20,decimal_places=5,default=0)
    def __str__(self):
        return f"Odds Outrights Summary History: Match: {self.match.id} -> Bookmaker: {self.bookmaker.key}, Team: {self.team.name}:${self.price}."

@admin.register(MatchOddsOutrightsSummaryHistory)
class MatchOddsOutrightsSummaryHistoryAdmin(admin.ModelAdmin):
    list_filter = ["team", "match", "bookmaker"]

class MatchOddsAPISettings(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    api_key_str = models.CharField(verbose_name="API Key",help_text="API Key for 'The Odds API' Access",default='')
    update_frequency = models.IntegerField(verbose_name="Update Interval",help_text="Match Data Update Interval. BEWARE: This setting can chew through a lot of API requests per day if set to a low threshold!",default=600)
    requests_remaining = models.IntegerField(help_text="API KEY Requests remaining before period reset.",verbose_name="Requests Remaining",default=0,blank=True,null=True)

@admin.register(MatchOddsAPISettings)
class MatchOddsAPISettingsAdmin(admin.ModelAdmin):
    pass






class MatchOddsTotalsSummary(models.Model):
    class Meta:
        unique_together = ["match","bookmaker"]
        ordering = ["-last_update"]
    uuid = models.UUIDField(primary_key=True,default= uuid.uuid4)
    match = models.ForeignKey(Match,verbose_name="Match",on_delete=models.CASCADE,null=True)
    bookmaker = models.ForeignKey(Bookmaker,verbose_name="Bookmaker",on_delete=models.RESTRICT)
    last_update = models.DateTimeField(verbose_name="Last Updated",auto_now=True)
    over_price = models.DecimalField(verbose_name="Over Price",max_digits=20,decimal_places=5,default=0)
    over_points = models.DecimalField(verbose_name="Over Points",max_digits=20,decimal_places=5,default=0)
    under_price = models.DecimalField(verbose_name="Under Price",max_digits=20,decimal_places=5,default=0)
    under_points = models.DecimalField(verbose_name="Under Points", max_digits=20, decimal_places=5,default=0)
    spread_price = models.DecimalField(verbose_name="Spread (Price)",max_digits=20,decimal_places=5,default=0)
    spread_points = models.DecimalField(verbose_name="Spread (Points)", max_digits=20, decimal_places=5,default=0)

    def __str__(self):
        return f"Odds Totals Summary: Match: {self.match} -> Bookmaker: {self.bookmaker.key}, {self.over_price}/{self.over_points} {self.under_price}/{self.under_points}"



@admin.register(MatchOddsTotalsSummary)
class MatchOddsTotalsSummaryAdmin(admin.ModelAdmin):
    list_filter = ["match", "bookmaker"]



class MatchOddsTotalsSummaryHistory(models.Model):
    class Meta:
        ordering = ["-last_update"]
    uuid = models.UUIDField(primary_key=True,default= uuid.uuid4)
    match = models.ForeignKey(Match,verbose_name="Match",on_delete=models.CASCADE,null=True)
    bookmaker = models.ForeignKey(Bookmaker,verbose_name="Bookmaker",on_delete=models.RESTRICT)
    created = models.DateTimeField(verbose_name="History created",auto_now_add=True)
    last_update = models.DateTimeField(verbose_name="Last Updated",auto_now=True)
    over_price = models.DecimalField(verbose_name="Over Price",max_digits=20,decimal_places=5,default=0)
    over_points = models.DecimalField(verbose_name="Over Points",max_digits=20,decimal_places=5,default=0)
    under_price = models.DecimalField(verbose_name="Under Price",max_digits=20,decimal_places=5,default=0)
    under_points = models.DecimalField(verbose_name="Under Points", max_digits=20, decimal_places=5,default=0)
    spread_price = models.DecimalField(verbose_name="Spread (Price)",max_digits=20,decimal_places=5,default=0)
    spread_points = models.DecimalField(verbose_name="Spread (Points)", max_digits=20, decimal_places=5,default=0)
    def __str__(self):
        return f"Odds Totals History: Match: {self.match} -> Bookmaker: {self.bookmaker.key}, {self.over_price}/{self.over_points} {self.under_price}/{self.under_points} [Created at: {self.created}]"



@admin.register(MatchOddsTotalsSummaryHistory)
class MatchOdMatchOddsTotalsSummaryHistoryAdmin(admin.ModelAdmin):
    list_filter = ["bookmaker","match"]


class MatchOddsSpreadsSummary(models.Model):
    class Meta:
        unique_together = ["match", "bookmaker"]
        ordering = ["-last_update"]
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    match = models.ForeignKey(Match,verbose_name="Match",on_delete=models.CASCADE,null=True)
    bookmaker = models.ForeignKey(Bookmaker, verbose_name="Bookmaker", on_delete=models.CASCADE)
    last_update = models.DateTimeField(verbose_name="Last Updated",auto_now=True)
    home_price = models.DecimalField(verbose_name="Home Price", max_digits=20, decimal_places=5, default=0)
    home_points = models.DecimalField(verbose_name="Home Price", max_digits=20, decimal_places=5, default=0)
    away_price = models.DecimalField(verbose_name="Away Price", max_digits=20, decimal_places=5, default=0)
    away_points = models.DecimalField(verbose_name="Away Points", max_digits=20, decimal_places=5, default=0)
    spread_price = models.DecimalField(verbose_name="Spread (Price)", max_digits=20, decimal_places=5, default=0)
    spread_points = models.DecimalField(verbose_name="Spread (Points)", max_digits=20, decimal_places=5, default=0)
    draw_price = models.DecimalField(verbose_name="Home Price", max_digits=20, decimal_places=5, default=0)
    def __str__(self):
        return f"Odds Spreads History: Match: {self.match} -> Bookmaker: {self.bookmaker.key}, Home Price/points:{self.home_price}/{self.home_points} Away Price/Points:{self.away_price}/{self.away_points} Spread Price/points: {self.spread_price}/{self.spread_points}"

@admin.register(MatchOddsSpreadsSummary)
class MatchOddsSpreadsSummaryAdmin(admin.ModelAdmin):
    list_filter = ["match","bookmaker"]


class MatchOddsSpreadsSummaryView(models.Model):
    match = models.ForeignKey(Match, verbose_name="Match", on_delete=models.CASCADE)
    last_update = models.DateTimeField(verbose_name="Last Updated", null=True, blank=True)
    avg_home_price = models.DecimalField(verbose_name="Home Price", max_digits=20, decimal_places=5, default=0)
    avg_home_points = models.DecimalField(verbose_name="Home Price", max_digits=20, decimal_places=5, default=0)
    avg_away_price = models.DecimalField(verbose_name="Away Price", max_digits=20, decimal_places=5, default=0)
    avg_away_points = models.DecimalField(verbose_name="Away Points", max_digits=20, decimal_places=5, default=0)
    avg_spread_price = models.DecimalField(verbose_name="Spread (Price)", max_digits=20, decimal_places=5, default=0)
    avg_spread_points = models.DecimalField(verbose_name="Spread (Points)", max_digits=20, decimal_places=5, default=0)
    def __str__(self):
        return f"Spreads: Match: {self.match}"
@admin.register(MatchOddsSpreadsSummaryView)
class MatchOddsSpreadsSummaryViewAdmin(admin.ModelAdmin):
    list_filter = ["match","match__sport"]

class MatchOddsTotalsSummaryView(models.Model):
    match = models.ForeignKey(Match, verbose_name="Match", on_delete=models.CASCADE)
    last_update = models.DateTimeField(verbose_name="Last Updated", null=True, blank=True)
    avg_over_price = models.DecimalField(verbose_name="Average Over Price",max_digits=20,decimal_places=5,default=0)
    avg_over_points = models.DecimalField(verbose_name="Average Over Points",max_digits=20,decimal_places=5,default=0)
    avg_under_price = models.DecimalField(verbose_name="Average Under Price",max_digits=20,decimal_places=5,default=0)
    avg_under_points = models.DecimalField(verbose_name="Average Under Points", max_digits=20, decimal_places=5,default=0)
    avg_spread_price = models.DecimalField(verbose_name="Average Spread (Price)",max_digits=20,decimal_places=5,default=0)
    avg_spread_points = models.DecimalField(verbose_name="Average Spread (Points)", max_digits=20, decimal_places=5,default=0)
    def __str__(self):
        return f"Totals: Match: {self.match}"

@admin.register(MatchOddsTotalsSummaryView)
class MatchOddsTotalsSummaryViewAdmin(admin.ModelAdmin):
    list_filter = ["match","match__sport"]

class MatchOddsOutrightsSummaryView(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    match = models.ForeignKey(Match, verbose_name="Match", on_delete=models.CASCADE)
    team = models.ForeignKey(Team,verbose_name="Team",on_delete=models.RESTRICT)
    last_update = models.DateTimeField(verbose_name="Last Updated", null = True, blank=True)
    avg_price = models.DecimalField(verbose_name="Average Price",max_digits=20,decimal_places=5,default=0)
    def __str__(self):
        return f"Outrights: Match: {self.match.uuid} - Team: {self.team.name}: Price: {self.avg_price}"

@admin.register(MatchOddsOutrightsSummaryView)
class MatchOddsOutrightsSummaryViewAdmin(admin.ModelAdmin):
    list_filter = ["match","match__sport","team"]




class MatchOddsSpreadsSummaryHistory(models.Model):
    class Meta:
        ordering = ["-last_update"]
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    match = models.ForeignKey(Match,verbose_name="Match",on_delete=models.CASCADE,null=True)
    bookmaker = models.ForeignKey(Bookmaker, verbose_name="Bookmaker", on_delete=models.RESTRICT)
    created = models.DateTimeField(verbose_name="History created", auto_now_add=True)
    last_update = models.DateTimeField(verbose_name="Last Updated", auto_now=True)
    home_price = models.DecimalField(verbose_name="Home Price", max_digits=20, decimal_places=5, default=0)
    home_points = models.DecimalField(verbose_name="Home Price", max_digits=20, decimal_places=5, default=0)
    away_price = models.DecimalField(verbose_name="Away Price", max_digits=20, decimal_places=5, default=0)
    away_points = models.DecimalField(verbose_name="Away Points", max_digits=20, decimal_places=5, default=0)
    spread_price = models.DecimalField(verbose_name="Spread (Price)", max_digits=20, decimal_places=5, default=0)
    spread_points = models.DecimalField(verbose_name="Spread (Points)", max_digits=20, decimal_places=5, default=0)

    def __str__(self):
        return f"Odds Spreads History: Match: {self.match} -> Bookmaker: {self.bookmaker.key}, {self.home_price}/{self.home_points} {self.away_price}/{self.away_points} [Created at: {self.created}]"


@admin.register(MatchOddsSpreadsSummaryHistory)
class MatchOddsSpreadsSummaryHistoryAdmin(admin.ModelAdmin):
    list_filter = ["match","bookmaker"]


class DynamicMarket(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    key = models.SlugField(verbose_name="Dynamic Market Key", unique=True,max_length=250)
    name = models.TextField(verbose_name="Dynamic Market Name",blank=True,null=True)
    active = models.BooleanField(default=True, verbose_name="Dynamic Market Is Active")
    def __str__(self):
        return f"Dynamic Market: {self.name or self.key}: Active[{self.active}]"

@admin.register(DynamicMarket)
class DynamicMarketAdmin(admin.ModelAdmin):
    search_fields = ["name","key"]
    list_filter = ["key","name","active"]


class SportDynamicMarkets(models.Model):
    uuid = models.UUIDField(primary_key=True,default=uuid.uuid4)
    sport = models.ForeignKey(Sport,verbose_name="Sport to apply Dynamic Market to",on_delete=models.CASCADE)
    market = models.ForeignKey(DynamicMarket,verbose_name="Market to apply to sport",on_delete=models.CASCADE)
    active = models.BooleanField(default=True, verbose_name="Dynamic Market Is Active")
    def __str__(self):
        return f"Dynamic Market to Sport Link: {self.market.name or self.market.key}->{self.sport.title or self.sport.key}: Active[{self.active}]"

@admin.register(SportDynamicMarkets)
class SportDynamicMarketsAdmin(admin.ModelAdmin):
    list_filter = ["sport","market","active"]


