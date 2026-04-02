import uuid
from decimal import Decimal
from uuid import uuid4 as defuuid

from django.contrib import admin
from django.db import models
from django.template.defaultfilters import title

from account.models import Account
from cashier.engine import Cashier
from cashier.models import ParlayPayoutRuleset
# from cashier.toolkit import account_credit_wager_win, account_debit_wager_loss
from licensemanager.models import AvailableApplication
from matches.models import Match, MatchScore
from parameters.models import VHost
from teams.models import Team

from toolkit.wagers.scoring_tools import calculate_parlay_total_wins, calculate_straight_bet_wins, \
    calculate_moneyline_payout, calculate_outright_payout
from django.utils.translation import gettext as _

# Create your models here.
class Wager(models.Model):
    class Meta:
        permissions = [("cancel_wager", "Can cancel wager"),("phone_wager", "Can place phone wager"),("qualify_wager","Can Qualify/Close Wager"),("view_reports","Can View Wager Reports")]
        ordering = ['created']
        indexes = [
            models.Index(
                fields=["account", "vhost", "grade_outcome", "graded_at"],
                name="wager_winner_lookup_idx",
            )
        ]
    TYPES = (('','-all-'),('ST','Straight'),('PA','Parlay'),('TO','Totals'),('ML','Moneyline'),('SP','Spreads'),('HA','Head-to-Head'),('OH','Outright'),('LI','Live Wager'),('DY','Dynamic Props Bets'),('TE','Teaser Bet'),('LE','Lottery Exact'))
    STATUS = (('','-all-'),('P','Open'),('M','Event(s) in Progress'),('W','Won'),('L','Lost'),('C','Cancelled'),('X','Withdrawn'),('E','Errored out'),('D','DRAW! Cancelled'),('I','L(i)ve wager'),('E','Early Payout Taken'),('F','Forfeit'))
    GRADE_OUTCOMES = (('W',_('Won')),('L',_('Lost')),('C',_('Cancelled')))
    uuid = models.UUIDField(primary_key=True,default=uuid.uuid4,verbose_name="ID")
    created = models.DateTimeField(auto_now_add=True,verbose_name=_("Created At"))
    account = models.ForeignKey(Account,on_delete=models.RESTRICT)
    vhost = models.ForeignKey(VHost,on_delete=models.RESTRICT,null=True,blank=True)
    type = models.CharField(max_length=120,verbose_name=_("Wager Type"),choices=TYPES,default='ST')
    status = models.CharField(max_length=120,verbose_name=_("Status"),choices=STATUS,default='P')
    grade_outcome = models.CharField(max_length=120,verbose_name=_("Grade Outcome"),null=True,blank=True,choices=GRADE_OUTCOMES)
    application_type = models.ForeignKey(AvailableApplication, on_delete=models.SET_NULL, null=True, blank=True,verbose_name="Game/Application")
    match = models.ForeignKey(Match,on_delete=models.RESTRICT,verbose_name=_("Match/Event"),null=True,blank=True)
    team_1 = models.ForeignKey(Team,on_delete=models.RESTRICT,related_name="wager_team_1",verbose_name=_("Team"),null=True,blank=True)
    team_2 = models.ForeignKey(Team, on_delete=models.RESTRICT, related_name="wager_team_2",null=True,blank=True,verbose_name=_("Team 2"))
    for_draw = models.BooleanField(default=False,help_text=_("Is this wager for a DRAW (ie, no team wins?)"),verbose_name=_("Wager on DRAW"))
    current_ip = models.GenericIPAddressField(blank=True, null=True, verbose_name=_("Current IP"))
    risk = models.DecimalField(max_digits=10,decimal_places=2,default=0,verbose_name=_("At Risk"))
    win = models.DecimalField(max_digits=10,decimal_places=2,default=0,verbose_name=_("To Win"))
    partial_payout = models.BooleanField(default=False)
    eap_payout = models.DecimalField(max_digits=10,decimal_places=2,default=0)
    base_spread = models.IntegerField(default=110)
    bet_data = models.JSONField(default=dict)
    pricing_reference = models.UUIDField(default=defuuid)
    pricing_reference_model = models.CharField(max_length=120)
    closed = models.BooleanField(default=False)
    cancelled = models.BooleanField(default=False)
    graded = models.BooleanField(default=False)
    executed = models.BooleanField(default=False)
    parlay_closed =  models.BooleanField(default=False)
    early_payout = models.BooleanField(default=False)
    live = models.BooleanField(default=False)
    gdl_ticket = models.BooleanField(default=False)
    phone_wager = models.BooleanField(default=False)
    # agent = models.ForeignKey(Agent,on_delete=models.SET_NULL,null=True,blank=True)
    parlay_ruleset = models.ForeignKey(ParlayPayoutRuleset, on_delete=models.SET_NULL, null=True, blank=True)
    grader_history = models.JSONField(default=dict)
    graded_at = models.DateTimeField(null=True, blank=True)
    use_bonus = models.BooleanField(default=False)
    hide_in_reports = models.BooleanField(default=False,help_text="Only will hide in User reports - will still show in all Agent reports")
    paid_at = models.DateTimeField(null=True, blank = True, verbose_name="Paid At")

    def save(self,*args,**kwargs):
        super(Wager, self).save(*args, **kwargs)
        if self.status == "L":
            from wager.signals.core import signal_wager_lost
            signal_wager_lost.send(sender=self.__class__,signal=self,wager=self,account=self.account,vhost=self.vhost)
        elif self.status == "W":
            from wager.signals.core import signal_wager_won
            signal_wager_won.send(sender=self.__class__,signal=self,wager=self,account=self.account,vhost=self.vhost)
        elif self.status == "D":
            from wager.signals.core import signal_wager_draw
            signal_wager_draw.send(sender=self.__class__,signal=self,wager=self,account=self.account,vhost=self.vhost)

    def is_straight(self):
        return self.type in ['ST','SP','TO','ML','HA','OH']

    def get_wager_type(self):
        if "dynamic" in self.bet_data:
            return title(self.bet_data["dynamic"]).replace("_"," ")
        else:
            return self.get_type_display()




    def execute_close(self,cashier,notifications=True):
        wac = False
        lac = False
        ltx = False
        if self.grade_outcome == "W" and not self.executed:

            wac,ltx = cashier.credit_wager_win(self)
        elif self.grade_outcome == "L" and not self.executed:

            if self.risk == 0:
                return False
            lac,ltx = cashier.debit_wager_loss(self)
        from matches.signals import signal_match_wagers_paid
        signal_match_wagers_paid.send(self, wagerObj=self,account=self.account,vhost=self.vhost)
        self.executed = True
        self.closed = True
        self.save()
        if "nodes" in self.bet_data:
            from wager.toolkit import close_nodes
            close_nodes(self)
        if wac or lac:
            return True
        else:
            print("Unable to Close/Execute wagers!!!",wac,ltx,self.grade_outcome,self.executed)
            return False


    def __str__(self):
        if "period" in self.bet_data:
            period = f" [Period: {self.bet_data['period']}]"
        else:
            period = ""
        if self.type == "PA":
            if "root_wager" in self.bet_data:
                return f"Root Parlay Wager for A#{self.account.acctnum}: ${self.risk} on: {self.match}"
            else:
                return f"Node Parlay Wager for A#{self.account.acctnum} on {self.match}: {self.team_1}"
        else:
            return f"{self.get_type_display()} Wager for A#{self.account.acctnum}: ${self.risk} on: {self.match} - Team 1:{self.team_1} Team 2: {self.team_2} {period}"


@admin.register(Wager)
class WagerAdmin(admin.ModelAdmin):
    list_filter = ["vhost","account","type","status"]
    search_fields = ["uuid"]

# @receiver(signals.post_save, sender=MatchScore)
# def send_wager_holders_score_update(sender, instance, created, **kwargs):
#     wagers = Wager.objects.filter(match=instance.match,status__in=["P","M"])
#     home_score = MatchScore.objects.get(match=instance.match,team=instance.match.home_team)
#     away_score = MatchScore.objects.get(match=instance.match,team=instance.match.away_team)
#     message = f"{instance.match.away_team} at: {instance.match.home_team}: Score is now A:{away_score} H: {home_score}!"
#


class MatchWagers(models.Model):
    class Meta:
        unique_together = ['match','wager']
    uuid = models.UUIDField(primary_key=True,default=uuid.uuid4)
    created = models.DateTimeField(auto_now_add=True)
    wager = models.ForeignKey(Wager,on_delete=models.CASCADE)
    match = models.ForeignKey(Match,on_delete=models.RESTRICT)
    def __str__(self):
        return f"Match Wager Link: Wager {self.wager.uuid} on Match {self.match.uuid}"


class LottoWagerPicks(models.Model):
    """
    Stores indexed lottery number picks for a wager.
    Stored in MAIN database alongside Wager.
    Uses indexed integer fields for efficient duplicate detection.
    """

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)

    # Link to Wager
    wager = models.OneToOneField(
        Wager,
        on_delete=models.CASCADE,
        related_name='lotto_picks'
    )

    # Reference to LottoMatch (stored as UUID, not FK across databases)
    lotto_match_uuid = models.UUIDField(
        db_index=True,
        help_text="UUID of LottoMatch in lotto database"
    )

    # Indexed main number picks (up to 10 numbers for various lotteries)
    pick_1 = models.IntegerField(null=True, blank=True, db_index=True)
    pick_2 = models.IntegerField(null=True, blank=True, db_index=True)
    pick_3 = models.IntegerField(null=True, blank=True, db_index=True)
    pick_4 = models.IntegerField(null=True, blank=True, db_index=True)
    pick_5 = models.IntegerField(null=True, blank=True, db_index=True)
    pick_6 = models.IntegerField(null=True, blank=True, db_index=True)
    pick_7 = models.IntegerField(null=True, blank=True, db_index=True)
    pick_8 = models.IntegerField(null=True, blank=True, db_index=True)
    pick_9 = models.IntegerField(null=True, blank=True, db_index=True)
    pick_10 = models.IntegerField(null=True, blank=True, db_index=True)

    # Bonus number picks (up to 2 for games like Mega Millions)
    bonus_1 = models.IntegerField(null=True, blank=True, db_index=True)
    bonus_2 = models.IntegerField(null=True, blank=True, db_index=True)

    # Quick pick flag
    is_quick_pick = models.BooleanField(default=False)

    # Grading result cache
    matched_main = models.IntegerField(default=0)
    matched_bonus = models.IntegerField(default=0)
    is_exact_match = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Lotto Wager Picks"
        verbose_name_plural = "Lotto Wager Picks"
        indexes = [
            models.Index(
                fields=['lotto_match_uuid', 'pick_1', 'pick_2', 'pick_3'],
                name='lotto_picks_lookup_idx'
            ),
        ]

    def __str__(self):
        picks = self.get_picks_list()
        return f"LottoPicks: {picks}"

    def get_picks_list(self):
        """Return main picks as sorted list."""
        picks = [
            getattr(self, f'pick_{i}')
            for i in range(1, 11)
            if getattr(self, f'pick_{i}') is not None
        ]
        return sorted(picks)

    def get_bonus_list(self):
        """Return bonus picks as list."""
        bonus = [
            getattr(self, f'bonus_{i}')
            for i in range(1, 3)
            if getattr(self, f'bonus_{i}') is not None
        ]
        return bonus

    def set_picks(self, main_numbers, bonus_numbers=None):
        """
        Set picks from lists.

        Args:
            main_numbers: List of main number picks (will be sorted)
            bonus_numbers: Optional list of bonus number picks
        """
        sorted_main = sorted(main_numbers)
        for i, num in enumerate(sorted_main[:10], 1):
            setattr(self, f'pick_{i}', num)

        if bonus_numbers:
            for i, num in enumerate(bonus_numbers[:2], 1):
                setattr(self, f'bonus_{i}', num)

    def check_duplicate(self):
        """
        Check if a duplicate wager with same numbers exists for the same user on same match.

        Returns:
            tuple: (exists, existing_wager_uuid or None)
        """
        existing = LottoWagerPicks.objects.filter(
            lotto_match_uuid=self.lotto_match_uuid,
            pick_1=self.pick_1,
            pick_2=self.pick_2,
            pick_3=self.pick_3,
            pick_4=self.pick_4,
            pick_5=self.pick_5,
            pick_6=self.pick_6,
            pick_7=self.pick_7,
            pick_8=self.pick_8,
            pick_9=self.pick_9,
            pick_10=self.pick_10,
            bonus_1=self.bonus_1,
            bonus_2=self.bonus_2,
            wager__account=self.wager.account,
        ).exclude(wager_id=self.wager_id).first()

        if existing:
            return True, existing.wager_id
        return False, None
