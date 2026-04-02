import uuid

from django.contrib import admin
from django.db import models

from matches.models import Match
from teams.models import Team
from .base_models import Bookmaker


class Match_Spreads_Q1(models.Model):
    class Meta:
        unique_together = (('match','bookmaker'))
        verbose_name = "Spreads 1st Quarter"
        verbose_name_plural = "Spreads 1st Quarter"
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    match = models.ForeignKey(Match,verbose_name="Match/Event",on_delete=models.CASCADE,related_name="+")
    bookmaker = models.ForeignKey(Bookmaker,on_delete=models.CASCADE)
    home_team = models.ForeignKey(Team,on_delete=models.CASCADE,null=True)
    home_price = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    home_point = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    away_team = models.ForeignKey(Team,on_delete=models.CASCADE,related_name="+",null=True)
    away_price = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    away_point = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    def __str__(self):
        return f"Match  1st Quarter Spreads: {self.match} from bookmaker {self.bookmaker.name}"

@admin.register(Match_Spreads_Q1)
class Match_Spreads_Q1_Admin(admin.ModelAdmin):
    list_filter = ["match","bookmaker"]

class Match_Spreads_Q1_View(models.Model):
    class Meta:
        managed = False
        db_table = "odds_match_spreads_q1_view"
        verbose_name = "Spreads 1st Quarter"
    uuid =models.UUIDField(primary_key=True, default=uuid.uuid4)
    match = models.ForeignKey(Match, verbose_name="Match/Event", on_delete=models.CASCADE,related_name="+")
    home_price = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    home_point = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    away_price = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    away_point = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    home_team = models.ForeignKey(Team, on_delete=models.CASCADE,null=True,related_name="+")
    away_team = models.ForeignKey(Team, on_delete=models.CASCADE,related_name="+",null=True)
    def __str__(self):
        return f"{self.match.away_team.name} at {self.match.home_team.name}:  Over P:{self.home_price}/{self.home_point}, U: {self.away_price}/{self.away_point}"

@admin.register(Match_Spreads_Q1_View)
class Match_Spreads_Q1_View_Admin(admin.ModelAdmin):
    list_filter = ["match"]


class Match_Spreads_Q2(models.Model):
    class Meta:
        unique_together = (('match','bookmaker'))
        verbose_name = "Spreads 2nd Quarter"
        verbose_name_plural = "Spreads 2nd Quarter"
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    match = models.ForeignKey(Match,verbose_name="Match/Event",on_delete=models.CASCADE,related_name="+")
    bookmaker = models.ForeignKey(Bookmaker,on_delete=models.CASCADE)
    home_team = models.ForeignKey(Team,on_delete=models.CASCADE,null=True)
    home_price = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    home_point = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    away_team = models.ForeignKey(Team,on_delete=models.CASCADE,related_name="+",null=True)
    away_price = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    away_point = models.DecimalField(max_digits=10, decimal_places=2,default=0)

    def __str__(self):
        return f"Match 2nd Quarter Spreads: {self.match} from bookmaker {self.bookmaker.name}"

@admin.register(Match_Spreads_Q2)
class Match_Spreads_Q2_Admin(admin.ModelAdmin):
    list_filter = ["match","bookmaker"]

class Match_Spreads_Q2_View(models.Model):
    class Meta:
        managed = False
        db_table = "odds_match_spreads_q2_view"
        verbose_name = "Spreads 2nd Quarter"
    uuid =models.UUIDField(primary_key=True, default=uuid.uuid4)
    match = models.ForeignKey(Match, verbose_name="Match/Event", on_delete=models.CASCADE,related_name="+")
    home_price = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    home_point = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    away_price = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    away_point = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    home_team = models.ForeignKey(Team, on_delete=models.CASCADE, null=True, related_name="+")
    away_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="+", null=True)
    def __str__(self):
        return f"{self.match.away_team.name} at {self.match.home_team.name}:  Over P:{self.home_price}/{self.home_point}, U: {self.away_price}/{self.away_point}"

@admin.register(Match_Spreads_Q2_View)
class Match_Spreads_Q2_View_Admin(admin.ModelAdmin):
    list_filter = ["match"]

class Match_Spreads_Q3(models.Model):
    class Meta:
        unique_together = (('match', 'bookmaker'))
        verbose_name = "Spreads 3rd Quarter"
        verbose_name_plural = "Spreads 3rd Quarter"
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    match = models.ForeignKey(Match, verbose_name="Match/Event", on_delete=models.CASCADE,related_name="+")
    bookmaker = models.ForeignKey(Bookmaker, on_delete=models.CASCADE)
    home_team = models.ForeignKey(Team, on_delete=models.CASCADE,null=True)
    home_price = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    home_point = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    away_team = models.ForeignKey(Team, on_delete=models.CASCADE,related_name="+",null=True)
    away_price = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    away_point = models.DecimalField(max_digits=10, decimal_places=2,default=0)

    def __str__(self):
        return f"Match 3rd Quarter Spreads: {self.match} from bookmaker {self.bookmaker.name}"

@admin.register(Match_Spreads_Q3)
class Match_Spreads_Q3_Admin(admin.ModelAdmin):
    list_filter = ["match", "bookmaker"]

class Match_Spreads_Q3_View(models.Model):
    class Meta:
        managed = False
        db_table = "odds_match_spreads_q3_view"
        verbose_name = "Spreads 3rd Quarter"
    uuid =models.UUIDField(primary_key=True, default=uuid.uuid4)
    match = models.ForeignKey(Match, verbose_name="Match/Event", on_delete=models.CASCADE,related_name="+")
    home_price = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    home_point = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    away_price = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    away_point = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    home_team = models.ForeignKey(Team, on_delete=models.CASCADE, null=True, related_name="+")
    away_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="+", null=True)
    def __str__(self):
        return f"{self.match.away_team.name} at {self.match.home_team.name}:  Over P:{self.home_price}/{self.home_point}, U: {self.away_price}/{self.away_point}"

@admin.register(Match_Spreads_Q3_View)
class Match_Spreads_Q3_View_Admin(admin.ModelAdmin):
    list_filter = ["match"]

class Match_Spreads_Q4(models.Model):
    class Meta:
        unique_together = (('match', 'bookmaker'))
        verbose_name = "Spreads 4th Quarter"
        verbose_name_plural = "Spreads 4th Quarter"
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    match = models.ForeignKey(Match, verbose_name="Match/Event", on_delete=models.CASCADE,related_name="+")
    bookmaker = models.ForeignKey(Bookmaker, on_delete=models.CASCADE)
    home_team = models.ForeignKey(Team, on_delete=models.CASCADE,null=True)
    home_price = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    home_point = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    away_team = models.ForeignKey(Team, on_delete=models.CASCADE,related_name="+",null=True)
    away_price = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    away_point = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    home_team = models.ForeignKey(Team, on_delete=models.CASCADE, null=True, related_name="+")
    away_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="+", null=True)

    def __str__(self):
        return f"Match Fourth Quarter Spreads Data: {self.match} from bookmaker {self.bookmaker.name}"

@admin.register(Match_Spreads_Q4)
class Match_Spreads_Q4_Admin(admin.ModelAdmin):
    list_filter = ["match", "bookmaker"]

class Match_Spreads_Q4_View(models.Model):
    class Meta:
        managed = False
        db_table = "odds_match_spreads_q4_view"
        verbose_name = "Spreads 4th Quarter"
    uuid =models.UUIDField(primary_key=True, default=uuid.uuid4)
    match = models.ForeignKey(Match, verbose_name="Match/Event", on_delete=models.CASCADE,related_name="+")
    home_price = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    home_point = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    away_price = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    away_point = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    home_team = models.ForeignKey(Team, on_delete=models.CASCADE, null=True, related_name="+")
    away_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="+", null=True)
    def __str__(self):
        return f"{self.match.away_team.name} at {self.match.home_team.name}:  Over P:{self.home_price}/{self.home_point}, U: {self.away_price}/{self.away_point}"

@admin.register(Match_Spreads_Q4_View)
class Match_Spreads_Q4_View_Admin(admin.ModelAdmin):
    list_filter = ["match"]


class Match_Spreads_H1(models.Model):
    class Meta:
        unique_together = (('match', 'bookmaker'))
        verbose_name = "Spreads 1st Half"
        verbose_name_plural = "Spreads 1st Half"
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    match = models.ForeignKey(Match, verbose_name="Match/Event", on_delete=models.CASCADE)
    bookmaker = models.ForeignKey(Bookmaker, on_delete=models.CASCADE)
    home_team = models.ForeignKey(Team, on_delete=models.CASCADE,null=True)
    home_price = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    home_point = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    away_team = models.ForeignKey(Team, on_delete=models.CASCADE,related_name="+",null=True)
    away_price = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    away_point = models.DecimalField(max_digits=10, decimal_places=2,default=0)


    def __str__(self):
        return f"Match First Half Spreads Data: {self.match} from bookmaker {self.bookmaker.name}"

@admin.register(Match_Spreads_H1)
class Match_Spreads_H1_Admin(admin.ModelAdmin):
    list_filter = ["match", "bookmaker"]

class Match_Spreads_H1_View(models.Model):
    class Meta:
        managed = False
        db_table = "odds_match_spreads_h1_view"
        verbose_name = "Spreads 1st Half"
    uuid =models.UUIDField(primary_key=True, default=uuid.uuid4)
    match = models.ForeignKey(Match, verbose_name="Match/Event", on_delete=models.CASCADE,related_name="+")
    home_price = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    home_point = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    away_price = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    away_point = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    home_team = models.ForeignKey(Team, on_delete=models.CASCADE, null=True, related_name="+")
    away_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="+", null=True)
    def __str__(self):
        return f"{self.match.away_team.name} at {self.match.home_team.name}:  Over P:{self.home_price}/{self.home_point}, U: {self.away_price}/{self.away_point}"

@admin.register(Match_Spreads_H1_View)
class Match_Spreads_H1_View_Admin(admin.ModelAdmin):
    list_filter = ["match"]

class Match_Spreads_H2(models.Model):
    class Meta:
        unique_together = (('match', 'bookmaker'))
        verbose_name = "Spreads 2nd Half"
        verbose_name_plural = "Spreads 2nd Half"
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    match = models.ForeignKey(Match, verbose_name="Match/Event", on_delete=models.CASCADE)
    bookmaker = models.ForeignKey(Bookmaker, on_delete=models.CASCADE)
    home_team = models.ForeignKey(Team, on_delete=models.CASCADE,null=True)
    home_price = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    home_point = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    away_team = models.ForeignKey(Team, on_delete=models.CASCADE,related_name="+",null=True)
    away_price = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    away_point = models.DecimalField(max_digits=10, decimal_places=2,default=0)

    def __str__(self):
        return f"Match Second Half Spreads Data: {self.match} from bookmaker {self.bookmaker.name}"

@admin.register(Match_Spreads_H2)
class Match_Spreads_H2_Admin(admin.ModelAdmin):
    list_filter = ["match", "bookmaker"]



class Match_Spreads_H2_View(models.Model):
    class Meta:
        managed = False
        db_table = "odds_match_spreads_h2_view"
        verbose_name = "Spreads 2nd Half"
    uuid =models.UUIDField(primary_key=True, default=uuid.uuid4)
    match = models.ForeignKey(Match, verbose_name="Match/Event", on_delete=models.CASCADE,related_name="+")
    home_price = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    home_point = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    away_price = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    away_point = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    home_team = models.ForeignKey(Team, on_delete=models.CASCADE, null=True, related_name="+")
    away_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="+", null=True)
    def __str__(self):
        return f"{self.match.away_team.name} at {self.match.home_team.name}:  Over P:{self.home_price}/{self.home_point}, U: {self.away_price}/{self.away_point}"

@admin.register(Match_Spreads_H2_View)
class Match_Spreads_H2_View_Admin(admin.ModelAdmin):
    list_filter = ["match"]