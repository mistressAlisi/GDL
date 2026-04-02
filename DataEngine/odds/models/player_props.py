import uuid

from django.contrib import admin
from django.db import models

from matches.models import Match
from players.models import Player
from .base_models import Bookmaker


class Match_First_TD(models.Model):
    class Meta:
        unique_together = (('match','bookmaker','player'))
        verbose_name = "1st Touchdown Scorer"
        verbose_name_plural = "1st Touchdown Scorer"
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    match = models.ForeignKey(Match, verbose_name="Match/Event", on_delete=models.CASCADE)
    bookmaker = models.ForeignKey(Bookmaker, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE,null=True)
    price = models.DecimalField(max_digits=10,decimal_places=2,default=0)
    def __str__(self):
        return f"Match {self.match}: First TD by {self.player.name}: P{self.price}"

@admin.register(Match_First_TD)
class Match_First_TD_Admin(admin.ModelAdmin):
    list_filter = ["match","player","bookmaker"]


class Match_First_TD_View(models.Model):
    TYPES = (('o', 'Over'), ('u', 'Under'))

    class Meta:
        managed = False
        db_table = "odds_match_first_td_view"
        verbose_name = "Match First TD"

    uuid =models.UUIDField(primary_key=True, default=uuid.uuid4)
    match = models.ForeignKey(Match, verbose_name="Match/Event", on_delete=models.CASCADE, related_name="+")
    player = models.ForeignKey(Player, verbose_name="Player", on_delete=models.CASCADE, related_name="+")
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.match.away_team.name} at {self.match.home_team.name}:  {self.player.name}: {self.price}"


@admin.register(Match_First_TD_View)
class Match_First_TD_View_Admin(admin.ModelAdmin):
    list_filter = ["match", "player"]

class Match_Anytime_TD(models.Model):
    class Meta:
        unique_together = (('match', 'bookmaker', 'player'))
        verbose_name = "Anytime Touchdown Scorer"
        verbose_name_plural = "Anytime Touchdown Scorer"
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    match = models.ForeignKey(Match, verbose_name="Match/Event", on_delete=models.CASCADE)
    bookmaker = models.ForeignKey(Bookmaker, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE,null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2,default=0)

    def __str__(self):
        return f"Match {self.match}: Anytime TD by {self.player.name}: P{self.price}"


@admin.register(Match_Anytime_TD)
class Match_Anytime_TD_Admin(admin.ModelAdmin):
    list_filter = ["match", "player", "bookmaker"]

class Match_Anytime_TD_View(models.Model):
    TYPES = (('o', 'Over'), ('u', 'Under'))

    class Meta:
        managed = False
        db_table = "odds_match_anytime_td_view"
        verbose_name = "Match Last TD"

    uuid =models.UUIDField(primary_key=True, default=uuid.uuid4)
    match = models.ForeignKey(Match, verbose_name="Match/Event", on_delete=models.CASCADE, related_name="+")
    player = models.ForeignKey(Player, verbose_name="Player", on_delete=models.CASCADE, related_name="+")
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.match.away_team.name} at {self.match.home_team.name}:  {self.player.name}: {self.price}"


@admin.register(Match_Anytime_TD_View)
class Match_Anytime_TD_View_Admin(admin.ModelAdmin):
    list_filter = ["match", "player"]


class Match_Last_TD(models.Model):
    class Meta:
        unique_together = (('match', 'bookmaker', 'player'))
        verbose_name = "Last Touchdown Scorer"
        verbose_name_plural = "Last Touchdown Scorer"
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    match = models.ForeignKey(Match, verbose_name="Match/Event", on_delete=models.CASCADE)
    bookmaker = models.ForeignKey(Bookmaker, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE,null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2,default=0)

    def __str__(self):
        return f"Match {self.match}: Last TD by {self.player.name}: P{self.price}"


@admin.register(Match_Last_TD)
class Match_Last_TD_Admin(admin.ModelAdmin):
    list_filter = ["match", "player", "bookmaker"]



class Match_Last_TD_View(models.Model):
    TYPES = (('o', 'Over'), ('u', 'Under'))

    class Meta:
        managed = False
        db_table = "odds_match_last_td_view"
        verbose_name = "Match Last TD"

    uuid =models.UUIDField(primary_key=True, default=uuid.uuid4)
    match = models.ForeignKey(Match, verbose_name="Match/Event", on_delete=models.CASCADE, related_name="+")
    player = models.ForeignKey(Player, verbose_name="Player", on_delete=models.CASCADE, related_name="+")
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.match.away_team.name} at {self.match.home_team.name}:  {self.player.name}: {self.price}"


@admin.register(Match_Last_TD_View)
class Match_Last_TD_View_Admin(admin.ModelAdmin):
    list_filter = ["match", "player"]


class Match_Pass_TD(models.Model):
    TYPES = (('o','Over'),('u','Under'))
    class Meta:
        unique_together = (('match', 'bookmaker', 'player','type'))
        verbose_name = "Pass Touchdowns"
        verbose_name_plural = "Pass Touchdowns"
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    match = models.ForeignKey(Match, verbose_name="Match/Event", on_delete=models.CASCADE)
    bookmaker = models.ForeignKey(Bookmaker, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE,null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    point = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    type = models.CharField(choices=TYPES, max_length=2,verbose_name="Type")
    def __str__(self):
        return f"Match {self.match}: Pass TDs by {self.player.name}: P{self.price}/Po:{self.point}"


@admin.register(Match_Pass_TD)
class Match_Pass_TD_Admin(admin.ModelAdmin):
    list_filter = ["match", "player", "bookmaker","type"]


class Match_Pass_TD_View(models.Model):
    TYPES = (('o', 'Over'), ('u', 'Under'))

    class Meta:
        managed = False
        db_table = "odds_match_pass_td_view"
        verbose_name = "Match Pass TDs"

    uuid =models.UUIDField(primary_key=True, default=uuid.uuid4)
    match = models.ForeignKey(Match, verbose_name="Match/Event", on_delete=models.CASCADE, related_name="+")
    player = models.ForeignKey(Player, verbose_name="Player", on_delete=models.CASCADE, related_name="+")
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    point = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    type = models.CharField(choices=TYPES, max_length=2, verbose_name="Type")

    def __str__(self):
        return f"{self.match.away_team.name} at {self.match.home_team.name}:  {self.player.name} [{self.type}]: {self.price}/{self.point}"


@admin.register(Match_Pass_TD_View)
class Match_Pass_TD_View_Admin(admin.ModelAdmin):
    list_filter = ["match", "player"]


class Match_Pass_YDS(models.Model):
    TYPES = (('o', 'Over'), ('u', 'Under'))

    class Meta:
        unique_together = (('match', 'bookmaker', 'player', 'type'))
        verbose_name = "Pass Yards"
        verbose_name_plural = "Pass Yards"
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    match = models.ForeignKey(Match, verbose_name="Match/Event", on_delete=models.CASCADE)
    bookmaker = models.ForeignKey(Bookmaker, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE,null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    point = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    type = models.CharField(choices=TYPES, max_length=2, verbose_name="Type")

    def __str__(self):
        return f"Match {self.match}: Pass Yards by {self.player.name}: P{self.price}/Po:{self.point}"


@admin.register(Match_Pass_YDS)
class Match_Pass_YDS_Admin(admin.ModelAdmin):
    list_filter = ["match", "player", "bookmaker", "type"]

class Match_Pass_YDS_View(models.Model):
    TYPES = (('o', 'Over'), ('u', 'Under'))
    class Meta:
        managed = False
        db_table = "odds_match_pass_yds_view"
        verbose_name = "Match  Pass Yards"
    uuid =models.UUIDField(primary_key=True, default=uuid.uuid4)
    match = models.ForeignKey(Match, verbose_name="Match/Event", on_delete=models.CASCADE,related_name="+")
    player = models.ForeignKey(Player, verbose_name="Player", on_delete=models.CASCADE, related_name="+")
    price = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    point = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    type = models.CharField(choices=TYPES, max_length=2, verbose_name="Type")
    def __str__(self):
        return f"{self.match.away_team.name} at {self.match.home_team.name}:  {self.player.name} [{self.type}]: {self.price}/{self.point}"

@admin.register(Match_Pass_YDS_View)
class Match_Pass_YDS_View_Admin(admin.ModelAdmin):
    list_filter = ["match","player"]




class Match_Reception_YDS(models.Model):
    TYPES = (('o', 'Over'), ('u', 'Under'))

    class Meta:
        unique_together = (('match', 'bookmaker', 'player', 'type'))
        verbose_name = "Reception Yards"
        verbose_name_plural = "Reception Yards"
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    match = models.ForeignKey(Match, verbose_name="Match/Event", on_delete=models.CASCADE)
    bookmaker = models.ForeignKey(Bookmaker, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE,null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    point = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    type = models.CharField(choices=TYPES, max_length=2, verbose_name="Type")
    def __str__(self):
        return f"Match {self.match}: Reception Yrds by {self.player.name}: P{self.price}/Po:{self.point}"


@admin.register(Match_Reception_YDS)
class Match_Reception_YDS_Admin(admin.ModelAdmin):
    list_filter = ["match", "player", "bookmaker", "type"]


class Match_Reception_YDS_View(models.Model):
    TYPES = (('o', 'Over'), ('u', 'Under'))
    class Meta:
        managed = False
        db_table = "odds_match_reception_yds_view"
        verbose_name = "Match  Reception Yards"
    uuid =models.UUIDField(primary_key=True, default=uuid.uuid4)
    match = models.ForeignKey(Match, verbose_name="Match/Event", on_delete=models.CASCADE,related_name="+")
    player = models.ForeignKey(Player, verbose_name="Player", on_delete=models.CASCADE, related_name="+")
    price = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    point = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    type = models.CharField(choices=TYPES, max_length=2, verbose_name="Type")
    def __str__(self):
        return f"{self.match.away_team.name} at {self.match.home_team.name}:  {self.player.name} [{self.type}]: {self.price}/{self.point}"

@admin.register(Match_Reception_YDS_View)
class Match_Reception_YDS_View_Admin(admin.ModelAdmin):
    list_filter = ["match","player"]




class Match_Reception_Longest(models.Model):
    TYPES = (('o', 'Over'), ('u', 'Under'))
    class Meta:
        unique_together = (('match', 'bookmaker', 'player', 'type'))
        verbose_name = "Longest Reception"
        verbose_name_plural = "Longest Reception"
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    match = models.ForeignKey(Match, verbose_name="Match/Event", on_delete=models.CASCADE)
    bookmaker = models.ForeignKey(Bookmaker, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE,null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    point = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    type = models.CharField(choices=TYPES, max_length=2, verbose_name="Type")

    def __str__(self):
        return f"Match {self.match}: Longest Reception by {self.player.name}: P{self.price}/Po:{self.point}"
@admin.register(Match_Reception_Longest)
class Match_Reception_Longest_Admin(admin.ModelAdmin):
    list_filter = ["match","player","bookmaker","type"]

class Match_Reception_Longest_View(models.Model):
    TYPES = (('o', 'Over'), ('u', 'Under'))
    class Meta:
        managed = False
        db_table = "odds_match_reception_longest_view"
        verbose_name = "Match Longest Reception"
    uuid =models.UUIDField(primary_key=True, default=uuid.uuid4)
    match = models.ForeignKey(Match, verbose_name="Match/Event", on_delete=models.CASCADE,related_name="+")
    player = models.ForeignKey(Player, verbose_name="Player", on_delete=models.CASCADE, related_name="+")
    price = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    point = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    type = models.CharField(choices=TYPES, max_length=2, verbose_name="Type")
    def __str__(self):
        return f"{self.match.away_team.name} at {self.match.home_team.name}:  {self.player.name} [{self.type}]: {self.price}/{self.point}"

@admin.register(Match_Reception_Longest_View)
class Match_Reception_Longest_View_Admin(admin.ModelAdmin):
    list_filter = ["match","player"]



class Match_Reception(models.Model):
    TYPES = (('o', 'Over'), ('u', 'Under'))

    class Meta:
        unique_together = (('match', 'bookmaker', 'player', 'type'))
        verbose_name = "Receptions"
        verbose_name_plural = "Receptions"
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    match = models.ForeignKey(Match, verbose_name="Match/Event", on_delete=models.CASCADE)
    bookmaker = models.ForeignKey(Bookmaker, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE,null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    point = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    type = models.CharField(choices=TYPES, max_length=2, verbose_name="Type")

    def __str__(self):
        return f"Match {self.match}: Receptions by {self.player.name}: P{self.price}/Po:{self.point}"
@admin.register(Match_Reception)
class Match_Reception_Admin(admin.ModelAdmin):
    list_filter = ["match","player","bookmaker","type"]


class Match_Reception_View(models.Model):
    TYPES = (('o', 'Over'), ('u', 'Under'))
    class Meta:
        managed = False
        db_table = "odds_match_reception_view"
        verbose_name = "Match Reception"
    uuid =models.UUIDField(primary_key=True, default=uuid.uuid4)
    match = models.ForeignKey(Match, verbose_name="Match/Event", on_delete=models.CASCADE,related_name="+")
    player = models.ForeignKey(Player, verbose_name="Player", on_delete=models.CASCADE, related_name="+")
    price = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    point = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    type = models.CharField(choices=TYPES, max_length=2, verbose_name="Type")
    def __str__(self):
        return f"{self.match.away_team.name} at {self.match.home_team.name}:  {self.player.name} [{self.type}]: {self.price}/{self.point}"

@admin.register(Match_Reception_View)
class Match_Reception_View_Admin(admin.ModelAdmin):
    list_filter = ["match","player"]


class Match_Rush_YDS(models.Model):
    TYPES = (('o', 'Over'), ('u', 'Under'))

    class Meta:
        unique_together = (('match', 'bookmaker', 'player', 'type'))
        verbose_name = "Rush Yards"
        verbose_name_plural = "Rush Yards"
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    match = models.ForeignKey(Match, verbose_name="Match/Event", on_delete=models.CASCADE)
    bookmaker = models.ForeignKey(Bookmaker, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE,null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    point = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    type = models.CharField(choices=TYPES, max_length=2, verbose_name="Type")

    def __str__(self):
        return f"Match {self.match}: Rush Yards by {self.player.name}: P{self.price}/Po:{self.point}"


@admin.register(Match_Rush_YDS)
class Match_Rush_YDS_Admin(admin.ModelAdmin):
    list_filter = ["match", "player", "bookmaker", "type"]

class Match_Rush_YDS_View(models.Model):
    TYPES = (('o', 'Over'), ('u', 'Under'))
    class Meta:
        managed = False
        db_table = "odds_match_rush_yds_view"
        verbose_name = "Match Rush Yards"
    uuid =models.UUIDField(primary_key=True, default=uuid.uuid4)
    match = models.ForeignKey(Match, verbose_name="Match/Event", on_delete=models.CASCADE,related_name="+")
    player = models.ForeignKey(Player, verbose_name="Player", on_delete=models.CASCADE, related_name="+")
    price = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    type = models.CharField(choices=TYPES, max_length=2, verbose_name="Type")
    def __str__(self):
        return f"{self.match.away_team.name} at {self.match.home_team.name}:  {self.player.name} [{self.type}]: {self.price}"

@admin.register(Match_Rush_YDS_View)
class Match_TD_Over_View(admin.ModelAdmin):
    list_filter = ["match","player"]


class Match_TD_Over(models.Model):
    class Meta:
        unique_together = (('match', 'bookmaker', 'player'))
        verbose_name = "Touchdowns Over"
        verbose_name_plural = "Touchdowns Over"
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    match = models.ForeignKey(Match, verbose_name="Match/Event", on_delete=models.CASCADE)
    bookmaker = models.ForeignKey(Bookmaker, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE,null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2,default=0)

    def __str__(self):
        return f"Match {self.match}: Touchdowns over by {self.player.name}: P{self.price}"


@admin.register(Match_TD_Over)
class Match_TD_Over_Admin(admin.ModelAdmin):
    list_filter = ["match", "player", "bookmaker"]


class Match_TD_Over_View(models.Model):
    class Meta:
        managed = False
        db_table = "odds_match_td_over_view"
        verbose_name = "Match TD Over"
    uuid =models.UUIDField(primary_key=True, default=uuid.uuid4)
    match = models.ForeignKey(Match, verbose_name="Match/Event", on_delete=models.CASCADE,related_name="+")
    player = models.ForeignKey(Player, verbose_name="Player", on_delete=models.CASCADE, related_name="+")
    price = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    def __str__(self):
        return f"{self.match.away_team.name} at {self.match.home_team.name}:  {self.player.name}: {self.price}"

@admin.register(Match_TD_Over_View)
class Match_TD_Over_View_Admin(admin.ModelAdmin):
    list_filter = ["match","player"]




""" Basketball """
class Match_Player_Assists(models.Model):
    TYPES = (('o','Over'),('u','Under'))
    class Meta:
        unique_together = (('match', 'bookmaker', 'player','type'))
        verbose_name = "Player Assists"
        verbose_name_plural = "Player Assists"
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    match = models.ForeignKey(Match, verbose_name="Match/Event", on_delete=models.CASCADE)
    bookmaker = models.ForeignKey(Bookmaker, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE,null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    point = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    type = models.CharField(choices=TYPES, max_length=2,verbose_name="Type")
    def __str__(self):
        return f"Match {self.match}: Player Assists for {self.player.name}: P:{self.price}/Po:{self.point}"

@admin.register(Match_Player_Assists)
class Match_Player_Assists_Admin(admin.ModelAdmin):
    list_filter = ["match","player","type"]

class Match_Player_Assists_View(models.Model):
    TYPES = (('o','Over'),('u','Under'))
    class Meta:

        verbose_name = "Player Assists "
        verbose_name_plural = "Player Assists"
        managed = False
        db_table = "odds_match_player_assists_view"
    uuid =models.UUIDField(primary_key=True, default=uuid.uuid4)
    match = models.ForeignKey(Match, verbose_name="Match/Event", on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE,null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    point = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    type = models.CharField(choices=TYPES, max_length=2,verbose_name="Type")
    def __str__(self):
        return f"Match {self.match}: Player Assists for {self.player.name}: P:{self.price}/Po:{self.point}"

@admin.register(Match_Player_Assists_View)
class Match_Player_Assists_View_Admin(admin.ModelAdmin):
    list_filter = ["match","player","type"]


class Match_Player_Blocks(models.Model):
    TYPES = (('o','Over'),('u','Under'))
    class Meta:
        unique_together = (('match', 'bookmaker', 'player','type'))
        verbose_name = "Player Blocks"
        verbose_name_plural = "Player Blocks"
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    match = models.ForeignKey(Match, verbose_name="Match/Event", on_delete=models.CASCADE)
    bookmaker = models.ForeignKey(Bookmaker, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE,null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    point = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    type = models.CharField(choices=TYPES, max_length=2,verbose_name="Type")
    def __str__(self):
        return f"Match {self.match}: Player Blocks for {self.player.name}: P:{self.price}/Po:{self.point}"

@admin.register(Match_Player_Blocks)
class Match_Player_Blocks_Admin(admin.ModelAdmin):
    list_filter = ["match","player","bookmaker","type"]

class Match_Player_Blocks_View(models.Model):
    TYPES = (('o','Over'),('u','Under'))
    class Meta:

        verbose_name = "Player Blocks "
        verbose_name_plural = "Player Blocks View"
        db_table = "odds_match_player_blocks_view"
        managed = False
    uuid =models.UUIDField(primary_key=True, default=uuid.uuid4)
    match = models.ForeignKey(Match, verbose_name="Match/Event", on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE,null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    point = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    type = models.CharField(choices=TYPES, max_length=2,verbose_name="Type")
    def __str__(self):
        return f"Match {self.match}: Player Blocks View for {self.player.name}: P:{self.price}/Po:{self.point}"

@admin.register(Match_Player_Blocks_View)
class Match_Player_Blocks_View_Admin(admin.ModelAdmin):
    list_filter = ["match","player","type"]

class Match_Player_Block_Steals(models.Model):
    TYPES = (('o','Over'),('u','Under'))
    class Meta:
        unique_together = (('match', 'bookmaker', 'player','type'))
        verbose_name = "Player Blocks Steals"
        verbose_name_plural = "Player Blocks Steals"
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    match = models.ForeignKey(Match, verbose_name="Match/Event", on_delete=models.CASCADE)
    bookmaker = models.ForeignKey(Bookmaker, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE,null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    point = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    type = models.CharField(choices=TYPES, max_length=2,verbose_name="Type")
    def __str__(self):
        return f"Match {self.match}: Player Blocks Steals for {self.player.name}: P:{self.price}/Po:{self.point}"

@admin.register(Match_Player_Block_Steals)
class Match_Player_Block_Steals_Admin(admin.ModelAdmin):
    list_filter = ["match","player","bookmaker","type"]

class Match_Player_Block_Steals_View(models.Model):
    TYPES = (('o','Over'),('u','Under'))
    class Meta:

        verbose_name = "Player Blocks Steals"
        verbose_name_plural = "Player Blocks Steals View"
        managed = False
        db_table = "odds_match_player_block_steals_view"
    uuid =models.UUIDField(primary_key=True, default=uuid.uuid4)
    match = models.ForeignKey(Match, verbose_name="Match/Event", on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE,null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    point = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    type = models.CharField(choices=TYPES, max_length=2,verbose_name="Type")
    def __str__(self):
        return f"Match {self.match}: Player Blocks Steals View for {self.player.name}: P:{self.price}/Po:{self.point}"

@admin.register(Match_Player_Block_Steals_View)
class Match_Player_Block_Steals_View_Admin(admin.ModelAdmin):
    list_filter = ["match","player","type"]

class Match_Player_Double_Double(models.Model):
    TYPES = (('o','Over'),('u','Under'))
    class Meta:
        unique_together = (('match', 'bookmaker', 'player'))
        verbose_name = "Player Double Double"
        verbose_name_plural = "Player Double Double"
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    match = models.ForeignKey(Match, verbose_name="Match/Event", on_delete=models.CASCADE)
    bookmaker = models.ForeignKey(Bookmaker, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE,null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    def __str__(self):
        return f"Match {self.match}: Player Double Double for {self.player.name}: P:{self.price}"

@admin.register(Match_Player_Double_Double)
class Match_Player_Double_Double_Admin(admin.ModelAdmin):
    list_filter = ["match","player","bookmaker"]

class Match_Player_Double_Double_View(models.Model):
    TYPES = (('o','Over'),('u','Under'))
    class Meta:

        verbose_name = "Player Double Double"
        verbose_name_plural = "Player Double Double View"
        managed = False
        db_table = "odds_match_player_double_double_view"
    uuid =models.UUIDField(primary_key=True, default=uuid.uuid4)
    match = models.ForeignKey(Match, verbose_name="Match/Event", on_delete=models.CASCADE)

    player = models.ForeignKey(Player, on_delete=models.CASCADE,null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    def __str__(self):
        return f"Match {self.match}: Player Double Double for {self.player.name}: P:{self.price}"

@admin.register(Match_Player_Double_Double_View)
class Match_Player_Double_Double_View_Admin(admin.ModelAdmin):
    list_filter = ["match","player"]

class Match_Player_First_Basket(models.Model):
    TYPES = (('o','Over'),('u','Under'))
    class Meta:
        unique_together = (('match', 'bookmaker', 'player'))
        verbose_name = "Player 1st Basket"
        verbose_name_plural = "Player 1st Basket"
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    match = models.ForeignKey(Match, verbose_name="Match/Event", on_delete=models.CASCADE)
    bookmaker = models.ForeignKey(Bookmaker, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE,null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    def __str__(self):
        return f"Match {self.match}: Player First Basket for {self.player.name}: P:{self.price}"

@admin.register(Match_Player_First_Basket)
class Match_Player_First_Basket_Admin(admin.ModelAdmin):
    list_filter = ["match","player","bookmaker"]

class Match_Player_First_Basket_View(models.Model):
    TYPES = (('o','Over'),('u','Under'))
    class Meta:

        verbose_name = "Player 1st Basket"
        verbose_name_plural = "Player 1st Basket View"
        managed = False
        db_table = "odds_match_player_first_basket_view"
    uuid =models.UUIDField(primary_key=True, default=uuid.uuid4)
    match = models.ForeignKey(Match, verbose_name="Match/Event", on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE,null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    def __str__(self):
        return f"Match {self.match}: Player First Basket for {self.player.name}: P:{self.price}"

@admin.register(Match_Player_First_Basket_View)
class Match_Player_First_Basket_View_Admin(admin.ModelAdmin):
    list_filter = ["match","player"]



class Match_Player_Points(models.Model):
    TYPES = (('o','Over'),('u','Under'))
    class Meta:
        unique_together = (('match', 'bookmaker', 'player','type'))
        verbose_name = "Player Points"
        verbose_name_plural = "Player Points"
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    match = models.ForeignKey(Match, verbose_name="Match/Event", on_delete=models.CASCADE)
    bookmaker = models.ForeignKey(Bookmaker, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE,null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    point = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    type = models.CharField(choices=TYPES, max_length=2, verbose_name="Type")
    def __str__(self):
        return f"Match {self.match}: Player Points for {self.player.name}[{self.type}]: P:{self.price}/Po:{self.point}"

@admin.register(Match_Player_Points)
class Match_Player_Points_Admin(admin.ModelAdmin):
    list_filter = ["match","player","bookmaker","type"]


class Match_Player_Points_View(models.Model):
    TYPES = (('o','Over'),('u','Under'))
    class Meta:

        verbose_name = "Player Points"
        verbose_name_plural = "Player Points View"
        managed = False
        db_table = "odds_match_player_points_view"
    uuid =models.UUIDField(primary_key=True, default=uuid.uuid4)
    match = models.ForeignKey(Match, verbose_name="Match/Event", on_delete=models.CASCADE)

    player = models.ForeignKey(Player, on_delete=models.CASCADE,null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    point = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    type = models.CharField(choices=TYPES, max_length=2, verbose_name="Type")
    def __str__(self):
        return f"Match {self.match}: Player Points for {self.player.name}[{self.type}]: P:{self.price}/Po:{self.point}"

@admin.register(Match_Player_Points_View)
class Match_Player_Points_View_Admin(admin.ModelAdmin):
    list_filter = ["match","player","type"]


class Match_Player_Points_Assists(models.Model):
    TYPES = (('o','Over'),('u','Under'))
    class Meta:
        unique_together = (('match', 'bookmaker', 'player','type'))
        verbose_name = "Player Points Assists"
        verbose_name_plural = "Player Points Assists"
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    match = models.ForeignKey(Match, verbose_name="Match/Event", on_delete=models.CASCADE)
    bookmaker = models.ForeignKey(Bookmaker, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE,null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    point = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    type = models.CharField(choices=TYPES, max_length=2, verbose_name="Type")
    def __str__(self):
        return f"Match {self.match}: Player Points Assists for {self.player.name}[{self.type}]: P:{self.price}/Po:{self.point}"

@admin.register(Match_Player_Points_Assists)
class Match_Player_Points_Assists_Admin(admin.ModelAdmin):
    list_filter = ["match","player","bookmaker"]


class Match_Player_Points_Assists_View(models.Model):
    TYPES = (('o','Over'),('u','Under'))
    class Meta:

        verbose_name = "Player Points Assists"
        verbose_name_plural = "Player Points Assists View"
        managed = False
        db_table = "odds_match_player_points_assists_view"
    uuid =models.UUIDField(primary_key=True, default=uuid.uuid4)
    match = models.ForeignKey(Match, verbose_name="Match/Event", on_delete=models.CASCADE)

    player = models.ForeignKey(Player, on_delete=models.CASCADE,null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    point = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    type = models.CharField(choices=TYPES, max_length=2, verbose_name="Type")
    def __str__(self):
        return f"Match {self.match}: Player Points Assists for {self.player.name}[{self.type}]: P:{self.price}/Po:{self.point}"

@admin.register(Match_Player_Points_Assists_View)
class Match_Player_Points_Assists_View_Admin(admin.ModelAdmin):
    list_filter = ["match","player"]

class Match_Player_Points_Rebounds(models.Model):
    TYPES = (('o', 'Over'), ('u', 'Under'))

    class Meta:
        unique_together = (('match', 'bookmaker', 'player', 'type'))
        verbose_name = "Player Points Rebounds"
        verbose_name_plural = "Player Points Rebounds"

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    match = models.ForeignKey(Match, verbose_name="Match/Event", on_delete=models.CASCADE)
    bookmaker = models.ForeignKey(Bookmaker, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    point = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    type = models.CharField(choices=TYPES, max_length=2, verbose_name="Type")
    def __str__(self):
        return f"Match {self.match}: Player Points Rebounds for {self.player.name}[{self.type}]: P:{self.price}/Po:{self.point}"


@admin.register(Match_Player_Points_Rebounds)
class Match_Player_Points_Rebounds_Admin(admin.ModelAdmin):
    list_filter = ["match", "player", "bookmaker"]

class Match_Player_Points_Rebounds_View(models.Model):
    TYPES = (('o', 'Over'), ('u', 'Under'))

    class Meta:

        verbose_name = "Player Points Rebounds"
        verbose_name_plural = "Player Points Rebounds View"
        managed = False
        db_table = "odds_match_player_points_rebounds_view"

    uuid =models.UUIDField(primary_key=True, default=uuid.uuid4)
    match = models.ForeignKey(Match, verbose_name="Match/Event", on_delete=models.CASCADE)

    player = models.ForeignKey(Player, on_delete=models.CASCADE, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    point = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    type = models.CharField(choices=TYPES, max_length=2, verbose_name="Type")
    def __str__(self):
        return f"Match {self.match}: Player Points Rebounds for {self.player.name}[{self.type}]: P:{self.price}/Po:{self.point}"


@admin.register(Match_Player_Points_Rebounds_View)
class Match_Player_Points_Rebounds_View_Admin(admin.ModelAdmin):
    list_filter = ["match", "player"]

class Match_Player_Points_Rebounds_Assists(models.Model):
    TYPES = (('o', 'Over'), ('u', 'Under'))

    class Meta:
        unique_together = (('match', 'bookmaker', 'player', 'type'))
        verbose_name = "Player Points Rebounds Assists"
        verbose_name_plural = "Player Points Rebounds Assists"

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    match = models.ForeignKey(Match, verbose_name="Match/Event", on_delete=models.CASCADE)
    bookmaker = models.ForeignKey(Bookmaker, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    point = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    type = models.CharField(choices=TYPES, max_length=2, verbose_name="Type")
    def __str__(self):
        return f"Match {self.match}: Player Points Rebounds Assists for {self.player.name}[{self.type}]: P:{self.price}/Po:{self.point}"


@admin.register(Match_Player_Points_Rebounds_Assists)
class Match_Player_Points_Rebounds_Assists_Admin(admin.ModelAdmin):
    list_filter = ["match", "player", "bookmaker"]


class Match_Player_Points_Rebounds_Assists_View(models.Model):
    TYPES = (('o', 'Over'), ('u', 'Under'))

    class Meta:

        verbose_name = "Player Points Rebounds Assists"
        verbose_name_plural = "Player Points Rebounds Assists View"
        managed = False
        db_table = "odds_match_player_points_rebounds_assists_view"

    uuid =models.UUIDField(primary_key=True, default=uuid.uuid4)
    match = models.ForeignKey(Match, verbose_name="Match/Event", on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    point = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    type = models.CharField(choices=TYPES, max_length=2, verbose_name="Type")
    def __str__(self):
        return f"Match {self.match}: Player Points Rebounds Assists for {self.player.name}[{self.type}]: P:{self.price}/Po:{self.point}"


@admin.register(Match_Player_Points_Rebounds_Assists_View)
class Match_Player_Points_Rebounds_Assists_View_Admin(admin.ModelAdmin):
    list_filter = ["match", "player"]


class Match_Player_Rebounds(models.Model):
    TYPES = (('o', 'Over'), ('u', 'Under'))

    class Meta:
        unique_together = (('match', 'bookmaker', 'player', 'type'))
        verbose_name = "Player Rebounds"
        verbose_name_plural = "Player Rebounds"

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    match = models.ForeignKey(Match, verbose_name="Match/Event", on_delete=models.CASCADE)
    bookmaker = models.ForeignKey(Bookmaker, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    point = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    type = models.CharField(choices=TYPES, max_length=2, verbose_name="Type")
    def __str__(self):
        return f"Match {self.match}: Player Rebounds for {self.player.name}[{self.type}]: P:{self.price}/Po:{self.point}"


@admin.register(Match_Player_Rebounds)
class Match_Player_Rebounds_Admin(admin.ModelAdmin):
    list_filter = ["match", "player", "bookmaker"]


class Match_Player_Rebounds_View(models.Model):
    TYPES = (('o', 'Over'), ('u', 'Under'))

    class Meta:

        verbose_name = "Player Rebounds"
        verbose_name_plural = "Player Rebounds View"
        db_table = "odds_match_player_rebounds_view"
        managed = False

    uuid =models.UUIDField(primary_key=True, default=uuid.uuid4)
    match = models.ForeignKey(Match, verbose_name="Match/Event", on_delete=models.CASCADE)

    player = models.ForeignKey(Player, on_delete=models.CASCADE, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    point = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    type = models.CharField(choices=TYPES, max_length=2, verbose_name="Type")
    def __str__(self):
        return f"Match {self.match}: Player Rebounds for {self.player.name}[{self.type}]: P:{self.price}/Po:{self.point}"


@admin.register(Match_Player_Rebounds_View)
class Match_Player_Rebounds_View_Admin(admin.ModelAdmin):
    list_filter = ["match", "player"]


class Match_Player_Rebounds_Assists(models.Model):
    TYPES = (('o', 'Over'), ('u', 'Under'))

    class Meta:
        unique_together = (('match', 'bookmaker', 'player', 'type'))
        verbose_name = "Player Rebounds Assists"
        verbose_name_plural = "Player Rebounds Assists"

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    match = models.ForeignKey(Match, verbose_name="Match/Event", on_delete=models.CASCADE)
    bookmaker = models.ForeignKey(Bookmaker, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    point = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    type = models.CharField(choices=TYPES, max_length=2, verbose_name="Type")
    def __str__(self):
        return f"Match {self.match}: Player Rebounds for {self.player.name}[{self.type}]: P:{self.price}/Po:{self.point}"


@admin.register(Match_Player_Rebounds_Assists)
class Match_Player_Rebounds_Assists_Admin(admin.ModelAdmin):
    list_filter = ["match", "player", "bookmaker"]




class Match_Player_Rebounds_Assists_View(models.Model):
    TYPES = (('o', 'Over'), ('u', 'Under'))

    class Meta:

        verbose_name = "Player Rebounds Assists"
        verbose_name_plural = "Player Rebounds Assists View"
        managed = False
        db_table = "odds_match_player_points_rebounds_assists_view"

    uuid =models.UUIDField(primary_key=True, default=uuid.uuid4)
    match = models.ForeignKey(Match, verbose_name="Match/Event", on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    point = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    type = models.CharField(choices=TYPES, max_length=2, verbose_name="Type")
    def __str__(self):
        return f"Match {self.match}: Player Rebounds for {self.player.name}[{self.type}]: P:{self.price}/Po:{self.point}"


@admin.register(Match_Player_Rebounds_Assists_View)
class Match_Player_Rebounds_Assists_View_Admin(admin.ModelAdmin):
    list_filter = ["match", "player"]


class Match_Player_Steals(models.Model):
    TYPES = (('o', 'Over'), ('u', 'Under'))

    class Meta:
        unique_together = (('match', 'bookmaker', 'player', 'type'))
        verbose_name = "Player Steals"
        verbose_name_plural = "Player Steals"

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    match = models.ForeignKey(Match, verbose_name="Match/Event", on_delete=models.CASCADE)
    bookmaker = models.ForeignKey(Bookmaker, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    point = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    type = models.CharField(choices=TYPES, max_length=2, verbose_name="Type")
    def __str__(self):
        return f"Match {self.match}: Player Rebounds for {self.player.name}[{self.type}]: P:{self.price}/Po:{self.point}"


@admin.register(Match_Player_Steals)
class Match_Player_Steals_Admin(admin.ModelAdmin):
    list_filter = ["match", "player", "bookmaker"]

class Match_Player_Steals_View(models.Model):
    TYPES = (('o', 'Over'), ('u', 'Under'))

    class Meta:

        verbose_name = "Player Steals"
        verbose_name_plural = "Player Steals"
        managed = False
        db_table = "odds_match_player_steals_view"

    uuid =models.UUIDField(primary_key=True, default=uuid.uuid4)
    match = models.ForeignKey(Match, verbose_name="Match/Event", on_delete=models.CASCADE)

    player = models.ForeignKey(Player, on_delete=models.CASCADE, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    point = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    type = models.CharField(choices=TYPES, max_length=2, verbose_name="Type")
    def __str__(self):
        return f"Match {self.match}: Player Rebounds for {self.player.name}[{self.type}]: P:{self.price}/Po:{self.point}"


@admin.register(Match_Player_Steals_View)
class Match_Player_Steals_View_Admin(admin.ModelAdmin):
    list_filter = ["match", "player"]



class Match_Player_Triple_Double(models.Model):
    TYPES = (('o','Over'),('u','Under'))
    class Meta:
        unique_together = (('match', 'bookmaker', 'player'))
        verbose_name = "Player Triple Double"
        verbose_name_plural = "Player Triple Double"
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    match = models.ForeignKey(Match, verbose_name="Match/Event", on_delete=models.CASCADE)
    bookmaker = models.ForeignKey(Bookmaker, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE,null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    def __str__(self):
        return f"Match {self.match}: Player Triple Double for {self.player.name}: P:{self.price}"

@admin.register(Match_Player_Triple_Double)
class Match_Player_Triple_Double_Admin(admin.ModelAdmin):
    list_filter = ["match","player","bookmaker"]



class Match_Player_Triple_Double_View(models.Model):
    TYPES = (('o','Over'),('u','Under'))
    class Meta:

        verbose_name = "Player Triple Double"
        verbose_name_plural = "Player Triple Double View"
        managed = False
        db_table = "odds_match_player_triple_double_view"
    uuid =models.UUIDField(primary_key=True, default=uuid.uuid4)
    match = models.ForeignKey(Match, verbose_name="Match/Event", on_delete=models.CASCADE)

    player = models.ForeignKey(Player, on_delete=models.CASCADE,null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    def __str__(self):
        return f"Match {self.match}: Player Triple Double for {self.player.name}: P:{self.price}"

@admin.register(Match_Player_Triple_Double_View)
class Match_Player_Triple_Double_View_Admin(admin.ModelAdmin):
    list_filter = ["match","player"]



class Match_Player_Turnovers(models.Model):
    TYPES = (('o', 'Over'), ('u', 'Under'))

    class Meta:
        unique_together = (('match', 'bookmaker', 'player', 'type'))
        verbose_name = "Player Turnovers"
        verbose_name_plural = "Player Turnovers"

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    match = models.ForeignKey(Match, verbose_name="Match/Event", on_delete=models.CASCADE)
    bookmaker = models.ForeignKey(Bookmaker, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    point = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    type = models.CharField(choices=TYPES, max_length=2, verbose_name="Type")
    def __str__(self):
        return f"Match {self.match}: Player Turnovers for {self.player.name}[{self.type}]: P:{self.price}/Po:{self.point}"


@admin.register(Match_Player_Turnovers)
class Match_Player_Turnovers_Admin(admin.ModelAdmin):
    list_filter = ["match", "player", "bookmaker"]

class Match_Player_Turnovers_View(models.Model):
    TYPES = (('o', 'Over'), ('u', 'Under'))

    class Meta:

        verbose_name = "Player Turnovers"
        verbose_name_plural = "Player Turnovers View"
        managed = False
        db_table = "odds_match_player_turnovers_view"
    uuid =models.UUIDField(primary_key=True, default=uuid.uuid4)
    match = models.ForeignKey(Match, verbose_name="Match/Event", on_delete=models.CASCADE)

    player = models.ForeignKey(Player, on_delete=models.CASCADE, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    point = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    type = models.CharField(choices=TYPES, max_length=2, verbose_name="Type")
    def __str__(self):
        return f"Match {self.match}: Player Turnovers for {self.player.name}[{self.type}]: P:{self.price}/Po:{self.point}"


@admin.register(Match_Player_Turnovers_View)
class Match_Player_Turnovers_View_Admin(admin.ModelAdmin):
    list_filter = ["match", "player"]


class Match_Player_Threes(models.Model):
    TYPES = (('o', 'Over'), ('u', 'Under'))

    class Meta:
        unique_together = (('match', 'bookmaker', 'player', 'type'))
        verbose_name = "Player Threes"
        verbose_name_plural = "Player Threes"


    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    match = models.ForeignKey(Match, verbose_name="Match/Event", on_delete=models.CASCADE)
    bookmaker = models.ForeignKey(Bookmaker, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    point = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    type = models.CharField(choices=TYPES, max_length=2, verbose_name="Type")
    def __str__(self):
        return f"Match {self.match}: Player Threes for {self.player.name}[{self.type}]: P:{self.price}/Po:{self.point}"


@admin.register(Match_Player_Threes)
class Match_Player_Threes_Admin(admin.ModelAdmin):
    list_filter = ["match", "player", "bookmaker"]


class Match_Player_Threes_View(models.Model):
    TYPES = (('o', 'Over'), ('u', 'Under'))

    class Meta:

        verbose_name = "Player Threes"
        verbose_name_plural = "Player Threes View"
        managed = False
        db_table = "odds_match_player_threes_view"

    uuid =models.UUIDField(primary_key=True, default=uuid.uuid4)
    match = models.ForeignKey(Match, verbose_name="Match/Event", on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    point = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    type = models.CharField(choices=TYPES, max_length=2, verbose_name="Type")

    def __str__(self):
        return f"Match {self.match}: Player Threes for {self.player.name}[{self.type}]: P:{self.price}/Po:{self.point}"


@admin.register(Match_Player_Threes_View)
class Match_Player_Threes_View_Admin(admin.ModelAdmin):
    list_filter = ["match", "player"]
