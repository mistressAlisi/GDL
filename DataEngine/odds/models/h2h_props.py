import uuid

from django.contrib import admin
from django.db import models

from matches.models import Match
from teams.models import Team
from .base_models import Bookmaker


# Create your models here.
class Match_H2H_H1(models.Model):
    class Meta:
        unique_together = (('match','bookmaker'))
        verbose_name = "Moneyline 1st Half"
        verbose_name_plural = "Moneyline 1st Half"
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    match = models.ForeignKey(Match,verbose_name="Match/Event",on_delete=models.CASCADE,related_name="+")
    bookmaker = models.ForeignKey(Bookmaker,on_delete=models.CASCADE)
    home_team = models.ForeignKey(Team,on_delete=models.CASCADE,null=True)
    home_price = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    away_team = models.ForeignKey(Team,on_delete=models.CASCADE,related_name="+",null=True)
    away_price = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    def __str__(self):
        return f"Moneyline 1st Half: {self.match} from bookmaker {self.bookmaker.name}"

@admin.register(Match_H2H_H1)
class Match_H2H_H1_Admin(admin.ModelAdmin):
    list_filter = ["match","bookmaker"]


class Match_H2H_H1_View(models.Model):
    class Meta:
        managed = False
        db_table = "odds_match_h2h_h1_view"
        verbose_name = "H2H 1st Half"
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    match = models.ForeignKey(Match, verbose_name="Match/Event", on_delete=models.CASCADE,related_name="+")
    home_team = models.ForeignKey(Team,on_delete=models.CASCADE,null=True,related_name="+")
    away_team = models.ForeignKey(Team,on_delete=models.CASCADE,null=True,related_name="+")
    home_price = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    away_price = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    def __str__(self):
        return f"{self.match.away_team.name} [{self.away_price}] at {self.match.home_team.name} [{self.home_price}]"

@admin.register(Match_H2H_H1_View)
class Match_H2H_H1_View_Admin(admin.ModelAdmin):
    list_filter = ["match","home_team","away_team"]


class Match_H2H_H2(models.Model):
    class Meta:
        unique_together = (('match','bookmaker'))
        verbose_name = "Moneyline 2nd Half"
        verbose_name_plural = "Moneyline 2nd Half"
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    match = models.ForeignKey(Match,verbose_name="Match/Event",on_delete=models.CASCADE,related_name="+")
    bookmaker = models.ForeignKey(Bookmaker,on_delete=models.CASCADE)
    home_team = models.ForeignKey(Team,on_delete=models.CASCADE,null=True)
    home_price = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    away_team = models.ForeignKey(Team,on_delete=models.CASCADE,related_name="+",null=True)
    away_price = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    def __str__(self):
        return f"Moneyline 2nd Half: {self.match} from bookmaker {self.bookmaker.name}"

@admin.register(Match_H2H_H2)
class Match_H2H_H2_Admin(admin.ModelAdmin):
    list_filter = ["match","bookmaker"]

class Match_H2H_H2_View(models.Model):
    class Meta:
        managed = False
        db_table = "odds_match_h2h_h2_view"
        verbose_name = "H2H 2nd Half"
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    match = models.ForeignKey(Match, verbose_name="Match/Event", on_delete=models.CASCADE,related_name="+")
    home_team = models.ForeignKey(Team,on_delete=models.CASCADE,null=True,related_name="+")
    away_team = models.ForeignKey(Team,on_delete=models.CASCADE,null=True,related_name="+")
    home_price = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    away_price = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    def __str__(self):
        return f"{self.match.away_team.name} [{self.away_price}] at {self.match.home_team.name} [{self.home_price}]"

@admin.register(Match_H2H_H2_View)
class Match_H2H_H2_View_Admin(admin.ModelAdmin):
    list_filter = ["match","home_team","away_team"]


class Match_H2H_Q1(models.Model):
    class Meta:
        unique_together = (('match','bookmaker'))
        verbose_name = "Moneyline 1st Quarter"
        verbose_name_plural = "Moneyline 1st Quarter"
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    match = models.ForeignKey(Match,verbose_name="Match/Event",on_delete=models.CASCADE,related_name="+")
    bookmaker = models.ForeignKey(Bookmaker,on_delete=models.CASCADE)
    home_team = models.ForeignKey(Team,on_delete=models.CASCADE,null=True)
    home_price = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    away_team = models.ForeignKey(Team,on_delete=models.CASCADE,related_name="+",null=True)
    away_price = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    def __str__(self):
        return f"Moneyline 1st Quarter: {self.match} from bookmaker {self.bookmaker.name}"

@admin.register(Match_H2H_Q1)
class Match_H2H_Q1_Admin(admin.ModelAdmin):
    list_filter = ["match","bookmaker"]


class Match_H2H_Q1_View(models.Model):
    class Meta:
        managed = False
        db_table = "odds_match_h2h_q1_view"
        verbose_name = "H2H 1st Quarter"
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    match = models.ForeignKey(Match, verbose_name="Match/Event", on_delete=models.CASCADE,related_name="+")
    home_team = models.ForeignKey(Team,on_delete=models.CASCADE,null=True,related_name="+")
    away_team = models.ForeignKey(Team,on_delete=models.CASCADE,null=True,related_name="+")
    home_price = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    away_price = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    def __str__(self):
        return f"{self.match.away_team.name} [{self.away_price}] at {self.match.home_team.name} [{self.home_price}]"

@admin.register(Match_H2H_Q1_View)
class Match_H2H_Q1_View_Admin(admin.ModelAdmin):
    list_filter = ["match","home_team","away_team"]


class Match_H2H_Q2(models.Model):
    class Meta:
        unique_together = (('match','bookmaker'))
        verbose_name = "Moneyline 2nd Quarter"
        verbose_name_plural = "Moneyline 2nd Quarter"
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    match = models.ForeignKey(Match,verbose_name="Match/Event",on_delete=models.CASCADE,related_name="+")
    bookmaker = models.ForeignKey(Bookmaker,on_delete=models.CASCADE)
    home_team = models.ForeignKey(Team,on_delete=models.CASCADE,null=True)
    home_price = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    away_team = models.ForeignKey(Team,on_delete=models.CASCADE,related_name="+",null=True)
    away_price = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    def __str__(self):
        return f"Moneyline 2nd Quarter: {self.match} from bookmaker {self.bookmaker.name}"

@admin.register(Match_H2H_Q2)
class Match_H2H_Q2_Admin(admin.ModelAdmin):
    list_filter = ["match","bookmaker"]



class Match_H2H_Q2_View(models.Model):
    class Meta:
        managed = False
        db_table = "odds_match_h2h_q2_view"
        verbose_name = "H2H 2nd Quarter"
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    match = models.ForeignKey(Match, verbose_name="Match/Event", on_delete=models.CASCADE,related_name="+")
    home_team = models.ForeignKey(Team,on_delete=models.CASCADE,null=True,related_name="+")
    away_team = models.ForeignKey(Team,on_delete=models.CASCADE,null=True,related_name="+")
    home_price = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    away_price = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    def __str__(self):
        return f"{self.match.away_team.name} [{self.away_price}] at {self.match.home_team.name} [{self.home_price}]"

@admin.register(Match_H2H_Q2_View)
class Match_H2H_Q1_View_Admin(admin.ModelAdmin):
    list_filter = ["match","home_team","away_team"]


class Match_H2H_Q3(models.Model):
    class Meta:
        unique_together = (('match', 'bookmaker'))
        verbose_name = "Moneyline 3rd Quarter"
        verbose_name_plural = "Moneyline 3rd Quarter"

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    match = models.ForeignKey(Match, verbose_name="Match/Event", on_delete=models.CASCADE)
    bookmaker = models.ForeignKey(Bookmaker, on_delete=models.CASCADE)
    home_team = models.ForeignKey(Team, on_delete=models.CASCADE,null=True)
    home_price = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    away_team = models.ForeignKey(Team, on_delete=models.CASCADE,related_name="+",null=True)
    away_price = models.DecimalField(max_digits=10, decimal_places=2,default=0)

    def __str__(self):
        return f"Moneyline 3rd Quarter: {self.match} from bookmaker {self.bookmaker.name}"

@admin.register(Match_H2H_Q3)
class Match_H2H_Q3_Admin(admin.ModelAdmin):
    list_filter = ["match", "bookmaker"]


class Match_H2H_Q3_View(models.Model):
    class Meta:
        managed = False
        db_table = "odds_match_h2h_q3_view"
        verbose_name = "H2H 3rd Quarter"
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    match = models.ForeignKey(Match, verbose_name="Match/Event", on_delete=models.CASCADE,related_name="+")
    home_team = models.ForeignKey(Team,on_delete=models.CASCADE,null=True,related_name="+")
    away_team = models.ForeignKey(Team,on_delete=models.CASCADE,null=True,related_name="+")
    home_price = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    away_price = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    def __str__(self):
        return f"{self.match.away_team.name} [{self.away_price}] at {self.match.home_team.name} [{self.home_price}]"

@admin.register(Match_H2H_Q3_View)
class Match_H2H_Q3_View_Admin(admin.ModelAdmin):
    list_filter = ["match","home_team","away_team"]

class Match_H2H_Q4(models.Model):
    class Meta:
        unique_together = (('match', 'bookmaker'))
        verbose_name = "Moneyline 4th Quarter"
        verbose_name_plural = "Moneyline 4th Quarter"
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    match = models.ForeignKey(Match, verbose_name="Match/Event", on_delete=models.CASCADE)
    bookmaker = models.ForeignKey(Bookmaker, on_delete=models.CASCADE)
    home_team = models.ForeignKey(Team, on_delete=models.CASCADE,null=True)
    home_price = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    away_team = models.ForeignKey(Team, on_delete=models.CASCADE,related_name="+",null=True)
    away_price = models.DecimalField(max_digits=10, decimal_places=2,default=0)

    def __str__(self):
        return f"Moneyline 4th Quarter: {self.match} from bookmaker {self.bookmaker.name}"

@admin.register(Match_H2H_Q4)
class Match_H2H_Q4_Admin(admin.ModelAdmin):
    list_filter = ["match", "bookmaker"]


class Match_H2H_Q4_View(models.Model):
    class Meta:
        managed = False
        db_table = "odds_match_h2h_q4_view"
        verbose_name = "H2H 4rd Quarter"
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    match = models.ForeignKey(Match, verbose_name="Match/Event", on_delete=models.CASCADE,related_name="+")
    home_team = models.ForeignKey(Team,on_delete=models.CASCADE,null=True,related_name="+")
    away_team = models.ForeignKey(Team,on_delete=models.CASCADE,null=True,related_name="+")
    home_price = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    away_price = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    def __str__(self):
        return f"{self.match.away_team.name} [{self.away_price}] at {self.match.home_team.name} [{self.home_price}]"

@admin.register(Match_H2H_Q4_View)
class Match_H2H_Q4_View_Admin(admin.ModelAdmin):
    list_filter = ["match","home_team","away_team"]