import uuid

from django.contrib import admin
from django.db import models
from django.utils import timezone
from django.utils.timezone import now


from sports.models import Sport, Season
from teams.models import Team


# Create your models here.
class Match(models.Model):
    STAGE_CHOICES = (('','--all--'),(0,'Stage 0'),(1,'Stage 1'),(2,'Stage 2'),(3,'Stage 3'),(4,'Stage 4'),(5,'Stage 5'))
    class Meta:
        ordering = ["sport","commence_time"]
        unique_together = (("sport","home_team","away_team","commence_time","id","vhost"))
    uuid = models.UUIDField(primary_key=True,default= uuid.uuid4)
    id = models.CharField(verbose_name="Match ID from Source  APIs")
    routing_key = models.CharField(verbose_name="Match Routing Key",null=True)
    apiid = models.CharField(verbose_name="API ID",null=True,blank=True)
    vhost = models.ForeignKey("parameters.VHost",on_delete=models.CASCADE,null=True,blank=True)
    name = models.TextField(verbose_name="Match Name",null=True,blank=True)
    sport = models.ForeignKey(Sport,verbose_name="Sport/League",on_delete=models.RESTRICT,null=True)
    season = models.ForeignKey(Season, verbose_name="Sport/League Season", on_delete=models.RESTRICT, null=True)
    stage = models.TextField(null=True,blank=True)
    week = models.TextField(null=True,blank=True)
    city = models.TextField(null=True)
    venue = models.TextField(null=True)
    status_short = models.TextField(null=True,blank=True)
    status_long = models.TextField(null=True,blank=True)
    clock = models.TextField(null=True,blank=True)
    commence_time = models.DateTimeField(verbose_name="Match Start Time",null=True,blank=True)
    match_stage = models.IntegerField(verbose_name="Match Stage",choices=STAGE_CHOICES,default=0)
    updated = models.DateTimeField(verbose_name="Match Data Update at", auto_now=True)
    is_outrights = models.BooleanField(verbose_name="Match is an Outrights Match",default=False,help_text="Set to true if this match is used to track outright market bets.")
    home_team = models.ForeignKey(Team,verbose_name="Home Team",related_name="+",on_delete=models.RESTRICT,null=True,blank=True)
    away_team = models.ForeignKey(Team, verbose_name="Away Team", related_name="+",on_delete=models.RESTRICT,null=True,blank=True)
    finished = models.BooleanField(verbose_name="Match Finished",default=False)
    finished_at = models.DateTimeField(verbose_name="Match Finish Time",null=True,blank=True)
    open = models.BooleanField(verbose_name="Match Open for Bets", default=True)
    active = models.BooleanField(verbose_name="Match Active for Backend", default=True)
    winner = models.ForeignKey(Team,verbose_name="Winner",related_name="+",on_delete=models.RESTRICT,null=True,blank=True)
    base_line = models.IntegerField(verbose_name="Base Line",help_text="Base Line Number (default 110) for this match",default=110)
    point_purchase_spread = models.DecimalField(verbose_name="Point Purchase Spread",help_text="The number of points +/- a player may purchase.",default=4.5,decimal_places=2,max_digits=10)
    draw = models.BooleanField(verbose_name="Match is a Draw",default=False)
    final_score = models.CharField(verbose_name="Final Score",null=True,blank=True)
    final_score_consensus = models.BooleanField(default=False)
    scoring_data = models.JSONField(verbose_name="Final Scoring Data",default=dict,null=True,blank=True)
    being_updated = models.BooleanField(default=False)
    last_update = models.DateTimeField(blank=True,null=True,default=now)
    live_events = models.BooleanField(default=False)
    score_closed = models.BooleanField(default=False)
    events_fetched = models.BooleanField(default=False)
    stats_fetched = models.BooleanField(default=False)
    wagers_graded = models.BooleanField(default=False)
    wagers_paid = models.BooleanField(default=False)
    in_play = models.BooleanField(default=False)
    manual_data = models.BooleanField(default=False)

    
    # Tournament-related fields (added for bracket system)
    is_tournament_match = models.BooleanField(default=False, verbose_name="Is Tournament Match")
    tournament_round = models.CharField(max_length=50, null=True, blank=True, verbose_name="Tournament Round", 
                                       help_text="e.g., 'Round of 32', 'Quarterfinals', 'Final'")
    bracket_position = models.CharField(max_length=20, null=True, blank=True, verbose_name="Bracket Position",
                                       help_text="Position in bracket for display purposes")
    next_match_winner = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True,
                                         related_name='previous_matches_winner', verbose_name="Winner Advances To")
    next_match_loser = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, 
                                        related_name='previous_matches_loser', verbose_name="Loser Advances To")

    def set_status(self,short,long):
        if short == self.status_short:
            return False
        self.status_short = short
        self.status_long = long
        # NOTE: We're using KIBL Fixture States for the Match lifestyle status calculation here.
        # In the future, if necessary this could be done more flexibly to support multiple data providers.
        # Upcoming (UPC or Blank):
        from matches.signals import states as state_signals
        if self.status_short == "UPC" or self.status_short == "":
            self.active = True
            self.open = True
            self.finished = False
            self.in_play = False
        # Match has begun! No more bets allowed (in_play is now True):
        elif self.status_short == "START":
            self.active = True
            self.open = True
            self.finished = False
            self.in_play = True
            state_signals.signal_match_started.send(sender=self.__class__, match=self)
        # Halftime event processing;
        elif self.status_short == "HT":
            self.in_play = True
            state_signals.signal_match_halftime.send(sender=self.__class__, match=self)
        elif self.status_short == "2H":
            self.in_play = True
            state_signals.signal_match_secondhalf.send(sender=self.__class__, match=self)
        # Finally, the match is concluded:
        elif self.status_short == "FINAL":
            self.open = False
            self.finished = True
            if not self.finished_at:
                self.finished_at = now()
            state_signals.signal_match_final.send(sender=self.__class__, match=self)
        state_signals.signal_match_state_changed.send(sender=self.__class__, match=self, status=self.status_short,
                                                      vhost=self.vhost)

    def close_match(self,short="FT",long="Finished"):
        if self.open:
            self.status_short = short
            self.status_long = long
            self.in_play = False
            self.finished = True
            self.open = False
            self.finished_at = now()
            self.save()

    def get_match_name(self):
        return f"{self.away_team.get_name()} vs {self.home_team.get_name()}"

    def get_logos_and_match_name(self,img_class="img-fluid img-responsive  rounded team-logo-main-card"):
        lstr = ""
        if self.away_team.card_logo:
            lstr += f"<img src='{self.away_team.card_logo.url}' alt='{self.away_team.get_name()} Logo' class='{img_class}'/>"
        lstr += f"{self.away_team.get_name()} at: {self.home_team.get_name()}"
        if self.home_team.card_logo:
            lstr += f"<img src='{self.home_team.card_logo.url}' alt='{self.home_team.get_name()} logo' class='{img_class}'/>"
        return lstr
    def get_match_fullname(self):
        return f"{self.id}/{self.uuid}: {self.away_team.get_name()} at {self.home_team.get_name()}"

    def __str__(self):
        ctz = timezone.localtime(self.commence_time)
        if self.is_outrights:
            retstr =  f"Match: Outrights for Sport [{self.sport}]: Commences at: {ctz.strftime("%Y-%m-%d %H:%M:%S")}"
        else:
            retstr =  f"Match: Sport [{self.sport}]: Commences at: {ctz.strftime("%Y-%m-%d %H:%M:%S")} -> {self.away_team.name} at: {self.home_team.name}"
        if self.finished:
            return "[Finished] "+retstr
        else:
            return retstr

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    search_fields = ["uuid", "id"]
    list_filter = ["home_team","away_team","commence_time","sport","status_short","open","active"]


class MatchScore(models.Model):
    class Meta:
        unique_together = ['match','team']
        ordering = ["match","created_at"]
    uuid = models.UUIDField(primary_key=True,default=uuid.uuid4)
    match = models.ForeignKey(Match,verbose_name="Parent Match",on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    team = models.ForeignKey(Team,verbose_name="Team",on_delete=models.CASCADE)
    winner = models.BooleanField(default=False)
    score = models.IntegerField(default=0)
    score_data = models.JSONField(default=dict,null=True,blank=True)
    def score2int(self):
        return int(self.score)
    def __str__(self):
        return f"{self.match} - {self.team}: {self.score}"

@admin.register(MatchScore)
class MatchScoreAdmin(admin.ModelAdmin):
    list_filter = ['match', 'team']



class MatchScoreHistory(models.Model):
    class Meta:
        ordering = ["match","created_at"]
    uuid = models.UUIDField(primary_key=True,default=uuid.uuid4)
    match = models.ForeignKey(Match,verbose_name="Parent Match",on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    team = models.ForeignKey(Team,verbose_name="Team",on_delete=models.CASCADE)
    winner = models.BooleanField(default=False)
    score = models.IntegerField(default=0)
    score_data = models.JSONField(default=dict,null=True,blank=True)
    def __str__(self):
        return f"ScoreHistory {self.created_at}: {self.match} - {self.team}: {self.score}"

@admin.register(MatchScoreHistory)
class MatchScoreHistoryAdmin(admin.ModelAdmin):
    list_filter = ['match', 'team']


class MatchEvent(models.Model):
    # class Meta:
    #     ordering = ["match","minute"]
    uuid = models.UUIDField(primary_key=True,default=uuid.uuid4)
    match = models.ForeignKey(Match,verbose_name="Parent Match",on_delete=models.CASCADE)
    quarter = models.CharField(verbose_name="Quarter")
    minute = models.CharField(verbose_name="Minute")
    team = models.ForeignKey(Team, on_delete=models.RESTRICT)
    player = models.ForeignKey('players.Player', on_delete=models.RESTRICT)
    season = models.ForeignKey(Season, on_delete=models.RESTRICT)
    type = models.CharField(verbose_name="Type",max_length=100)
    comment = models.TextField(verbose_name="Comment")
    score  = models.JSONField(verbose_name="Score Data",default=dict)
    def __str__(self):
        return f"{self.match}: {self.team.name}->{self.player.name}: {self.type} @ {self.minute}: {self.comment}"



@admin.register(MatchEvent)
class MatchEventAdmin(admin.ModelAdmin):
    list_filter = ["match", "quarter","minute","team"]

class MatchPerGroupSportView(models.Model):
    class Meta:
        db_table = "sport_group_match_view"
        managed = False
    group = models.ForeignKey('sports.Group',verbose_name="Group",on_delete=models.DO_NOTHING)
    sport = models.ForeignKey('sports.Sport',verbose_name="Sport",on_delete=models.DO_NOTHING)
    match = models.ForeignKey('matches.Match',verbose_name="Match",on_delete=models.DO_NOTHING)


class MatchOutcomeTeamScoresView(models.Model):
    class Meta:
        db_table = "matches_outcome_team_scores_view"
        managed = False
    uuid = models.UUIDField(primary_key=True)
    team = models.ForeignKey('teams.Team',verbose_name="Team",on_delete=models.DO_NOTHING,related_name="+")
    sport = models.ForeignKey('sports.Sport',on_delete=models.DO_NOTHING,related_name="+")
    season = models.ForeignKey('sports.Season',on_delete=models.DO_NOTHING,related_name="+")
    home_team = models.ForeignKey('teams.Team',on_delete=models.DO_NOTHING,related_name="+")
    away_team = models.ForeignKey('teams.Team',on_delete=models.DO_NOTHING,related_name="+")
    segment = models.ForeignKey('outcomes.Segment', verbose_name="Segment", on_delete=models.DO_NOTHING,related_name="+")
    match = models.ForeignKey('matches.Match', on_delete=models.DO_NOTHING, related_name="+")
    # state = models.ForeignKey(State)
    outcome_id = models.TextField(verbose_name="Outcome ID")
    team_routing_key = models.TextField(verbose_name="Team Routing Key")
    team_key = models.TextField(verbose_name="Team Key")
    team_name = models.TextField(verbose_name="Team Name")
    match_name = models.TextField(verbose_name="Match Name")
    match_routing_key = models.TextField(verbose_name="Match Routing Key")
    score = models.IntegerField(default=0)
    clock = models.TextField(verbose_name="Clock")
    is_current = models.BooleanField(default=False)
    is_start_game = models.BooleanField(default=False)
    is_start_segment = models.BooleanField(default=False)
    is_end_segment = models.BooleanField(default=False)
    draw = models.BooleanField(default=False)
    final_score = models.TextField(verbose_name="Final Score")
    segment_name = models.TextField(verbose_name="Segment Name")
    segment_abrv = models.TextField(verbose_name="Segment ABRV")


@admin.register(MatchOutcomeTeamScoresView)
class MatchOutcomeTeamScoresViewAdmin(admin.ModelAdmin):
    pass