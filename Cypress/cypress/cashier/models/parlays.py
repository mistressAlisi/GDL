import uuid
from uuid import uuid4

from django.contrib import admin
from django.db import models
from django.db.models import CheckConstraint, Q

from parameters.models import VHost
from sports.models import Sport, Group

class ParlayPayoutRuleset(models.Model):
    uuid = models.UUIDField(primary_key=True,default=uuid4)
    vhosts = models.ManyToManyField(VHost, verbose_name="Virtual Hosts")
    agents = models.ManyToManyField('management.Manager', verbose_name="Agents")
    name = models.TextField(verbose_name="Parlay Payout Ruleset Name",unique=True)
    created = models.DateTimeField(verbose_name="Parlay Payout Ruleset Created", auto_now_add=True)
    updated = models.DateTimeField(verbose_name="Parlay Payout Ruleset Updated", auto_now=True)
    def __str__(self):
        return f"Ruleset for {self.vhosts.all()}: {self.name}"

@admin.register(ParlayPayoutRuleset)
class ParlayPayoutRulesetAdmin(admin.ModelAdmin):
    list_filter = ["vhosts","name"]

class ParlayPayoutRulesetEntry(models.Model):
    class Meta:
        unique_together = (( "ruleset","parlay_legs","max_losses"),)
        ordering = ("ruleset","parlay_legs","max_losses")
    uuid = models.UUIDField(primary_key=True,default=uuid4)
    ruleset = models.ForeignKey(ParlayPayoutRuleset, on_delete=models.CASCADE, verbose_name="Parlay Payout Ruleset", null=True, blank=True)
    parlay_legs = models.IntegerField(verbose_name="Parlay Legs", default=0,help_text="How many legs will be in parlay")
    max_losses = models.IntegerField(verbose_name="Max Losses", default=0,help_text="Maximum number of losses that can be incurred before Parlay is considered to be lost or a partial payout winner. Qualification happens at max_losses-1 legs.")
    min_bet = models.IntegerField(verbose_name="Minimum Bet for this Level",default=1)
    max_bet = models.IntegerField(verbose_name="Maximum Bet for this Level",default=10)
    players_percentage = models.IntegerField(verbose_name="Payout Percentage",help_text="Winner payout percentage (for player): 0 to 100", default=100)
    juice_percentage = models.IntegerField(verbose_name="Juice Percentage",help_text="Juice to adjust the lines by for this particular parlay (0~100) PCT",default=5)
    neg_limit = models.IntegerField(verbose_name="Negative Odds Limit",help_text='Lower limit of negative odds to include in calculations',default=-150)
    max_payout = models.IntegerField(verbose_name="Max Payout",default=0)
    def __str__(self):
        return f"Parlay Payout {self.ruleset.name}: Legs: {self.parlay_legs} Losses: {self.max_losses} PPCT: {self.players_percentage}%"

@admin.register(ParlayPayoutRulesetEntry)
class ParlayPayoutRulesetAdmin(admin.ModelAdmin):
    list_filter = ["ruleset","parlay_legs"]
