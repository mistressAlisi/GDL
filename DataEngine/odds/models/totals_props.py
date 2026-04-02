import uuid

from django.contrib import admin
from django.db import models

from matches.models import Match
from teams.models import Team
from .base_models import Bookmaker


class Match_Totals_Q1(models.Model):
    class Meta:
        unique_together = (('match', 'bookmaker'))
        verbose_name = "Totals Over/Under 1st Quarter"
        verbose_name_plural = "Totals Over/Under 1st Quarter"
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    match = models.ForeignKey(Match, verbose_name="Match/Event", on_delete=models.CASCADE,related_name="+")
    bookmaker = models.ForeignKey(Bookmaker, on_delete=models.CASCADE)
    over_price = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    over_point = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    under_price = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    under_point = models.DecimalField(max_digits=10, decimal_places=2,default=0)

    def __str__(self):
        return f"Match Totals 1st Quarter Data: {self.match} from bookmaker {self.bookmaker.name}"

@admin.register(Match_Totals_Q1)
class Match_Totals_Q1_Admin(admin.ModelAdmin):
    list_filter = ["match", "bookmaker"]

class Match_Totals_Q1_View(models.Model):
    class Meta:
        managed = False
        db_table = "odds_match_totals_q1_view"
        verbose_name = "Totals Over/Under 1st Quarter View"
    uuid =models.UUIDField(primary_key=True, default=uuid.uuid4)
    match = models.ForeignKey(Match, verbose_name="Match/Event", on_delete=models.CASCADE,related_name="+")
    over_price = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    over_point = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    under_price = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    under_point = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    def __str__(self):
        return f"{self.match.away_team.name} at {self.match.home_team.name}: Over P:{self.over_price}/{self.over_point}, U: {self.under_price}/{self.under_point}"

@admin.register(Match_Totals_Q1_View)
class Match_Totals_Q1_View_Admin(admin.ModelAdmin):
    list_filter = ["match"]

class Match_Totals_Q2(models.Model):
    class Meta:
        unique_together = (('match', 'bookmaker'))
        verbose_name = "Totals Over/Under 2nd Quarter"
        verbose_name_plural = "Totals Over/Under 2nd Quarter"
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    match = models.ForeignKey(Match, verbose_name="Match/Event", on_delete=models.CASCADE,related_name="+")
    bookmaker = models.ForeignKey(Bookmaker, on_delete=models.CASCADE)
    over_price = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    over_point = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    under_price = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    under_point = models.DecimalField(max_digits=10, decimal_places=2,default=0)

    def __str__(self):
        return f"Match Totals 2nd Quarter Data: {self.match} from bookmaker {self.bookmaker.name}"

@admin.register(Match_Totals_Q2)
class Match_Totals_Q2_Admin(admin.ModelAdmin):
    list_filter = ["match", "bookmaker"]

class Match_Totals_Q2_View(models.Model):
    class Meta:
        managed = False
        db_table = "odds_match_totals_q2_view"
        verbose_name = "Totals Over/Under 2nd Quarter"
    uuid =models.UUIDField(primary_key=True, default=uuid.uuid4)
    match = models.ForeignKey(Match, verbose_name="Match/Event", on_delete=models.CASCADE,related_name="+")
    over_price = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    over_point = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    under_price = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    under_point = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    def __str__(self):
        return f"{self.match.away_team.name} at {self.match.home_team.name}:  Over P:{self.over_price}/{self.over_point}, U: {self.under_price}/{self.under_point}"

@admin.register(Match_Totals_Q2_View)
class Match_Totals_Q2_View_Admin(admin.ModelAdmin):
    list_filter = ["match"]

class Match_Totals_Q3(models.Model):
    class Meta:
        unique_together = (('match', 'bookmaker'))
        verbose_name = "Totals Over/Under 3rd Quarter"
        verbose_name_plural = "Totals Over/Under 3rd Quarter"
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    match = models.ForeignKey(Match, verbose_name="Match/Event", on_delete=models.CASCADE,related_name="+")
    bookmaker = models.ForeignKey(Bookmaker, on_delete=models.CASCADE)
    over_price = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    over_point = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    under_price = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    under_point = models.DecimalField(max_digits=10, decimal_places=2,default=0)

    def __str__(self):
        return f"Match 3rd Quarter Totals Data: {self.match} from bookmaker {self.bookmaker.name}"


@admin.register(Match_Totals_Q3)
class Match_Totals_Q3_Admin(admin.ModelAdmin):
    list_filter = ["match", "bookmaker"]


class Match_Totals_Q3_View(models.Model):
    class Meta:
        managed = False
        db_table = "odds_match_totals_q3_view"
        verbose_name = "Totals Over/Under 3rd Quarter"
    uuid =models.UUIDField(primary_key=True, default=uuid.uuid4)
    match = models.ForeignKey(Match, verbose_name="Match/Event", on_delete=models.CASCADE,related_name="+")
    over_price = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    over_point = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    under_price = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    under_point = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    def __str__(self):
        return f"{self.match.away_team.name} at {self.match.home_team.name}:  Over P:{self.over_price}/{self.over_point}, U: {self.under_price}/{self.under_point}"

@admin.register(Match_Totals_Q3_View)
class Match_Totals_Q3_View_Admin(admin.ModelAdmin):
    list_filter = ["match"]


class Match_Totals_Q4(models.Model):
    class Meta:
        unique_together = (('match', 'bookmaker'))
        verbose_name = "Totals Over/Under 4th Quarter"
        verbose_name_plural = "Totals Over/Under 4th Quarter"
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    match = models.ForeignKey(Match, verbose_name="Match/Event", on_delete=models.CASCADE,related_name="+")
    bookmaker = models.ForeignKey(Bookmaker, on_delete=models.CASCADE)
    over_price = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    over_point = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    under_price = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    under_point = models.DecimalField(max_digits=10, decimal_places=2,default=0)

    def __str__(self):
        return f"Match Fourth Quarter Totals Data: {self.match} from bookmaker {self.bookmaker.name}"


@admin.register(Match_Totals_Q4)
class Match_Totals_Q4_Admin(admin.ModelAdmin):
    list_filter = ["match", "bookmaker"]


class Match_Totals_Q4_View(models.Model):
    class Meta:
        managed = False
        db_table = "odds_match_totals_q4_view"
        verbose_name = "Totals 4th Quarter"
    uuid =models.UUIDField(primary_key=True, default=uuid.uuid4)
    match = models.ForeignKey(Match, verbose_name="Match/Event", on_delete=models.CASCADE,related_name="+")
    over_price = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    over_point = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    under_price = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    under_point = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    def __str__(self):
        return f"{self.match.away_team.name} at {self.match.home_team.name}:  Over P:{self.over_price}/{self.over_point}, U: {self.under_price}/{self.under_point}"

@admin.register(Match_Totals_Q4_View)
class Match_Totals_Q4_View_Admin(admin.ModelAdmin):
    list_filter = ["match"]


class Match_Totals_H1(models.Model):
    class Meta:
        unique_together = (('match', 'bookmaker'))
        verbose_name = "Totals Over/Under 1st Half"
        verbose_name_plural = "Totals Over/Under 1st Half"
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    match = models.ForeignKey(Match, verbose_name="Match/Event", on_delete=models.CASCADE,related_name="+")
    bookmaker = models.ForeignKey(Bookmaker, on_delete=models.CASCADE)
    over_price = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    over_point = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    under_price = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    under_point = models.DecimalField(max_digits=10, decimal_places=2,default=0)

    def __str__(self):
        return f"Match Totals 1st Half Data: {self.match} from bookmaker {self.bookmaker.name}"


@admin.register(Match_Totals_H1)
class Match_Totals_H1_Admin(admin.ModelAdmin):
    list_filter = ["match", "bookmaker"]


class Match_Totals_H1_View(models.Model):
    class Meta:
        managed = False
        db_table = "odds_match_totals_h1_view"
        verbose_name = "Totals  1st Half"
    uuid =models.UUIDField(primary_key=True, default=uuid.uuid4)
    match = models.ForeignKey(Match, verbose_name="Match/Event", on_delete=models.CASCADE,related_name="+")
    over_price = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    over_point = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    under_price = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    under_point = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    def __str__(self):
        return f"{self.match.away_team.name} at {self.match.home_team.name}:  Over P:{self.over_price}/{self.over_point}, U: {self.under_price}/{self.under_point}"

@admin.register(Match_Totals_H1_View)
class Match_Totals_H1_View_Admin(admin.ModelAdmin):
    list_filter = ["match"]


class Match_Totals_H2(models.Model):
    class Meta:
        unique_together = (('match', 'bookmaker'))
        verbose_name = "Totals Over/Under 2nd Half"
        verbose_name_plural = "Totals Over/Under 2nd Half"
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    match = models.ForeignKey(Match, verbose_name="Match/Event", on_delete=models.CASCADE,related_name="+")
    bookmaker = models.ForeignKey(Bookmaker, on_delete=models.CASCADE)
    over_price = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    over_point = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    under_price = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    under_point = models.DecimalField(max_digits=10, decimal_places=2,default=0)

    def __str__(self):
        return f"Match Second Half Totals Data: {self.match} from bookmaker {self.bookmaker.name}"


@admin.register(Match_Totals_H2)
class Match_Totals_H2_Admin(admin.ModelAdmin):
    list_filter = ["match", "bookmaker"]


class Match_Totals_H2_View(models.Model):
    class Meta:
        managed = False
        db_table = "odds_match_totals_h2_view"
        verbose_name = "Totals Over/Under 2nd Half View"
        verbose_name_plural = "Totals 2nd Half "
    uuid =models.UUIDField(primary_key=True, default=uuid.uuid4)
    match = models.ForeignKey(Match, verbose_name="Match/Event", on_delete=models.CASCADE,related_name="+")
    over_price = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    over_point = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    under_price = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    under_point = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    def __str__(self):
        return f"{self.match.away_team.name} at {self.match.home_team.name}:  Over P:{self.over_price}/{self.over_point}, U: {self.under_price}/{self.under_point}"

@admin.register(Match_Totals_H2_View)
class Match_Totals_H2_View_Admin(admin.ModelAdmin):
    list_filter = ["match"]




class Match_Team_Totals_Q1(models.Model):
    class Meta:
        unique_together = (('match', 'bookmaker'))
        verbose_name = "Team Totals Over/Under 1st Quarter"
        verbose_name_plural = "Team Totals Over/Under 1st Quarter"
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    match = models.ForeignKey(Match, verbose_name="Match/Event", on_delete=models.CASCADE,related_name="+")
    bookmaker = models.ForeignKey(Bookmaker, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="+",null=True)
    over_price = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    over_point = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    under_price = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    under_point = models.DecimalField(max_digits=10, decimal_places=2,default=0)

    def __str__(self):
        return f"Match Team Totals 1st Quarter Data: {self.match} from bookmaker {self.bookmaker.name}"

@admin.register(Match_Team_Totals_Q1)
class Match_Team_Totals_Q1_Admin(admin.ModelAdmin):
    list_filter = ["match", "bookmaker"]


class Match_Team_Totals_Q1_View(models.Model):
    class Meta:

        verbose_name = "Team Totals Over/Under 1st Quarter View"
        verbose_name_plural = "Team Totals Over/Under 1st Quarter View"
        managed = False
        db_table = "odds_match_team_totals_q1_view"
    uuid =models.UUIDField(primary_key=True, default=uuid.uuid4)
    match = models.ForeignKey(Match, verbose_name="Match/Event", on_delete=models.CASCADE,related_name="+")

    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="+",null=True)
    over_price = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    over_point = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    under_price = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    under_point = models.DecimalField(max_digits=10, decimal_places=2,default=0)

    def __str__(self):
        return f"Match Team Totals 1st Quarter Data: {self.match}: {self.over_price},{self.over_point},{self.under_price},{self.under_point}"

@admin.register(Match_Team_Totals_Q1_View)
class Match_Team_Totals_Q1_View_Admin(admin.ModelAdmin):
    list_filter = ["match", "team"]



class Match_Team_Totals_Q2(models.Model):
    class Meta:
        unique_together = (('match', 'bookmaker'))
        verbose_name = "Team Totals Over/Under 2nd Quarter"
        verbose_name_plural = "Team Totals Over/Under 2nd Quarter"
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    match = models.ForeignKey(Match, verbose_name="Match/Event", on_delete=models.CASCADE,related_name="+")
    bookmaker = models.ForeignKey(Bookmaker, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="+",null=True)
    over_price = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    over_point = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    under_price = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    under_point = models.DecimalField(max_digits=10, decimal_places=2,default=0)

    def __str__(self):
        return f"Match Team Totals 2nd Quarter Data: {self.match} from bookmaker {self.bookmaker.name}"

@admin.register(Match_Team_Totals_Q2)
class Match_Team_Totals_Q2_Admin(admin.ModelAdmin):
    list_filter = ["match", "bookmaker"]

class Match_Team_Totals_Q2_View(models.Model):
    class Meta:

        verbose_name = "Team Totals Over/Under 2nd Quarter View"
        verbose_name_plural = "Team Totals Over/Under 2nd Quarter View"
        managed = False
        db_table = "odds_match_team_totals_q2_view"
    uuid =models.UUIDField(primary_key=True, default=uuid.uuid4)
    match = models.ForeignKey(Match, verbose_name="Match/Event", on_delete=models.CASCADE,related_name="+")

    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="+",null=True)
    over_price = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    over_point = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    under_price = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    under_point = models.DecimalField(max_digits=10, decimal_places=2,default=0)

    def __str__(self):
        return f"Match Team Totals 2nd Quarter Data: {self.match}: {self.over_price},{self.over_point},{self.under_price},{self.under_point}"

@admin.register(Match_Team_Totals_Q2_View)
class Match_Team_Totals_Q2_View_Admin(admin.ModelAdmin):
    list_filter = ["match", "team"]




class Match_Team_Totals_Q3(models.Model):
    class Meta:
        unique_together = (('match', 'bookmaker'))
        verbose_name = "Team Totals Over/Under 3rd Quarter"
        verbose_name_plural = "Team Totals Over/Under 3rd Quarter"
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    match = models.ForeignKey(Match, verbose_name="Match/Event", on_delete=models.CASCADE,related_name="+")
    bookmaker = models.ForeignKey(Bookmaker, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="+",null=True)
    over_price = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    over_point = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    under_price = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    under_point = models.DecimalField(max_digits=10, decimal_places=2,default=0)

    def __str__(self):
        return f"Match Team 3rd Quarter Totals Data: {self.match} from bookmaker {self.bookmaker.name}"


@admin.register(Match_Team_Totals_Q3)
class Match_Team_Totals_Q3_Admin(admin.ModelAdmin):
    list_filter = ["match", "bookmaker"]


class Match_Team_Totals_Q3_View(models.Model):
    class Meta:
        verbose_name = "Team Totals Over/Under 3rd Quarter View"
        verbose_name_plural = "Team Totals Over/Under 3rd Quarter View"
        managed = False
        db_table = "odds_match_team_totals_q3_view"

    uuid =models.UUIDField(primary_key=True, default=uuid.uuid4)
    match = models.ForeignKey(Match, verbose_name="Match/Event", on_delete=models.CASCADE, related_name="+")

    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="+", null=True)
    over_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    over_point = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    under_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    under_point = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"Match Team Totals 3rd Quarter Data: {self.match}: {self.over_price},{self.over_point},{self.under_price},{self.under_point}"


@admin.register(Match_Team_Totals_Q3_View)
class Match_Team_Totals_Q3_View_Admin(admin.ModelAdmin):
    list_filter = ["match", "team"]




class Match_Team_Totals_Q4(models.Model):
    class Meta:
        unique_together = (('match', 'bookmaker'))
        verbose_name = "Team Totals Over/Under 4th Quarter"
        verbose_name_plural = "Team Totals Over/Under 4th Quarter"
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    match = models.ForeignKey(Match, verbose_name="Match/Event", on_delete=models.CASCADE,related_name="+")
    bookmaker = models.ForeignKey(Bookmaker, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="+",null=True)
    over_price = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    over_point = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    under_price = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    under_point = models.DecimalField(max_digits=10, decimal_places=2,default=0)

    def __str__(self):
        return f"Match Team Fourth Quarter Totals Data: {self.match} from bookmaker {self.bookmaker.name}"


@admin.register(Match_Team_Totals_Q4)
class Match_Team_Totals_Q4_Admin(admin.ModelAdmin):
    list_filter = ["match", "bookmaker"]


class Match_Team_Totals_Q4_View(models.Model):
    class Meta:
        verbose_name = "Team Totals Over/Under 4th Quarter View"
        verbose_name_plural = "Team Totals Over/Under 4th Quarter View"
        managed = False
        db_table = "odds_match_team_totals_q4_view"

    uuid =models.UUIDField(primary_key=True, default=uuid.uuid4)
    match = models.ForeignKey(Match, verbose_name="Match/Event", on_delete=models.CASCADE, related_name="+")

    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="+", null=True)
    over_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    over_point = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    under_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    under_point = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"Match Team Totals 4th Quarter Data: {self.match}: {self.over_price},{self.over_point},{self.under_price},{self.under_point}"


@admin.register(Match_Team_Totals_Q4_View)
class Match_Team_Totals_Q4_View_Admin(admin.ModelAdmin):
    list_filter = ["match", "team"]
