# import random
# from decimal import Decimal
#
# from django.contrib.auth.models import User
# from django.test import TestCase
#
# from account.models import Account
# from agent.models import Agent
# from cashier.engine import Cashier
# from cashier.models import AccountLevels, ParlayPayoutRuleset, HouseBalance, AccountDepositBonus
# from matches.models import Match
# from parameters.models import VHost, VHostDomain
# from sports.models import Group, Sport
# from teams.models import Team
# from toolkit.wagers.scoring_tools import calculate_straight_bet_wins
# from wager.models import Wager
#
#
# class CashierCoreWagerTests(TestCase):
#     @classmethod
#     def setUp(cls):
#         cls.user = User.objects.get_or_create(username="lilith")[0]
#         cls.user.save()
#         cls.agent = Agent.objects.get_or_create(user=cls.user)[0]
#         cls.agent.save()
#         cls.vhost = VHost.objects.get_or_create(name="vhost")[0]
#         cls.vhost.save()
#         cls.vdomain = VHostDomain.objects.get_or_create(domain_fqdn="vdomain",vhost=cls.vhost)[0]
#         cls.vdomain.save()
#         cls.rules = ParlayPayoutRuleset.objects.get_or_create(name="rule1")[0]
#
#         cls.rules.save()
#         cls.level = AccountLevels(max_deposit_cryp=10000,daily_deposit_lim_cryp=50000,weekly_deposit_lim_cryp=50000,monthly_deposit_lim_cryp=30000,yearly_deposit_lim_cryp=40000,vhost=cls.vhost,parlay_ruleset=cls.rules,deposit_fee_pct_cryp=5,max_play_amount_cryp=10000)
#         cls.level.save()
#         actnum = random.randint(100200, 101000)
#         cls.account = Account.objects.get_or_create(acctnum=actnum, agent=cls.agent,account_level=cls.level,vhost=cls.vhost)[0]
#         cls.account.save()
#         cls.team_1 = Team.objects.get_or_create(key="test_team_1", name="Test Team 1")[0]
#         cls.team_2 = Team.objects.get_or_create(key="test_team_2", name="Test Team 2")[0]
#         cls.group = Group.objects.get_or_create(slug="test", icon="test_icon", name="test sport", generic_icon="test_genicon")[0]
#         cls.sport = Sport.objects.get_or_create(key="test_sport", group=cls.group, title="sport_title", wager_limit=100000)[0]
#         cls.match = Match.objects.get_or_create(sport=cls.sport,home_team=cls.team_1,away_team=cls.team_2)[0]
#
#
#     def test_risk_balance_wagers(self):
#         cashier = Cashier(self.account)
#         status, tx = cashier._deposit_to_account(2000)
#         self.assertTrue(status)
#         curr_balance = cashier.get_available_balance()
#         withdraw = curr_balance - 1000
#         total_risk = 0
#         wagers = []
#         for i in range(1,10):
#             risk = random.randint(10, 100)
#             if i%2 == 0:
#                 team = self.team_1
#             else:
#                 team = self.team_2
#             wager = Wager(account=self.account, team_1=team, type="ST", risk=risk,
#                           win=calculate_straight_bet_wins(risk, 110), base_spread=110, match=self.match)
#             wager.save()
#             wagers.append(str(wager.uuid))
#             curr_balance -= risk
#             total_risk += risk
#         status, tx, bonusObjs = cashier.risk_balance(total_risk,relations=wagers)
#         self.assertTrue(status)
#
#         self.assertTrue(status)
#         self.assertAlmostEqual(curr_balance, cashier.get_available_balance())
