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
# from parameters.models import VHost, VHostDomain
#
#
# class CashierCoreBalanceTests(TestCase):
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
#         cls.level = AccountLevels(max_deposit_cryp=1000,daily_deposit_lim_cryp=500,weekly_deposit_lim_cryp=500,monthly_deposit_lim_cryp=3000,yearly_deposit_lim_cryp=4000,vhost=cls.vhost,parlay_ruleset=cls.rules,deposit_fee_pct_cryp=5,max_play_amount_cryp=1000)
#         cls.level.save()
#         actnum = random.randint(100200, 101000)
#         cls.account = Account.objects.get_or_create(acctnum=actnum, agent=cls.agent,account_level=cls.level,vhost=cls.vhost)[0]
#         cls.account.save()
#
#
#     def test_deposit_limits(self):
#         cashier = Cashier(self.account)
#         depamn = random.randint(10, 99)
#         status,tx = cashier._deposit_to_account(depamn)
#         fees = Decimal(depamn*(self.level.deposit_fee_pct_cryp/100))
#         eff = Decimal(depamn-fees)
#         houseBal = HouseBalance.objects.get(vhost=self.vhost)
#         self.assertTrue(status)
#         self.assertAlmostEqual(fees,tx.fees_change)
#         self.assertAlmostEqual(houseBal.fees,fees)
#         self.assertAlmostEqual(houseBal.withdrawable, fees)
#         self.assertAlmostEqual(Decimal(tx.avail_change), eff)
#         self.assertAlmostEqual(Decimal(tx.withdrawable_change), eff)
#
#
#     def test_deposit_bonuses(self):
#         depBonus = AccountDepositBonus(level=self.level,min_deposit=200,deposit_multiplier=2,rollover=5)
#         depBonus.save()
#         cashier = Cashier(self.account)
#         status,tx = cashier._deposit_to_account(110)
#         self.assertTrue(status)
#         self.assertAlmostEqual(110*(1-(self.level.deposit_fee_pct_cryp/100)),tx.avail_change)
#         self.assertAlmostEqual(110 * (self.level.deposit_fee_pct_cryp / 100), tx.fees_change)
#         status,tx = cashier._deposit_to_account(110)
#         self.assertTrue(status)
#         total_avail = Decimal(220*(1-(self.level.deposit_fee_pct_cryp/100))*2)+Decimal(220*(1-(self.level.deposit_fee_pct_cryp/100)))
#         self.assertAlmostEqual(total_avail, Decimal(cashier.get_available_balance()))
#         rollover_bal = Decimal(220*5)*Decimal(.95)
#         bonus = cashier.get_bonus_balance()
#         # print(bonus)
#         self.assertAlmostEqual(Decimal(220*(1-(self.level.deposit_fee_pct_cryp/100))*2),bonus)
#         self.assertAlmostEqual(rollover_bal,cashier.get_pending_rollovers())
#
#
#     def test_risk_balance(self):
#         cashier = Cashier(self.account)
#         status,tx = cashier._deposit_to_account(500)
#         self.assertTrue(status)
#         curr_balance = cashier.get_available_balance()
#         for i in range(1,10):
#             withdraw = random.randint(1,20)
#             status, tx, bonusObjs = cashier.risk_balance(withdraw)
#             self.assertTrue(status)
#             curr_balance -= withdraw
#             self.assertAlmostEqual(curr_balance, cashier.get_available_balance())
#
#     def test_risk_balance_wagers(self):
#         cashier = Cashier(self.account)
#         status, tx = cashier._deposit_to_account(500)
#         self.assertTrue(status)
#         curr_balance = cashier.get_available_balance()
#
#         withdraw = random.randint(1, 20)
#         status, tx, bonusObjs = cashier.risk_balance(withdraw)
#         self.assertTrue(status)
#         curr_balance -= withdraw
#         self.assertAlmostEqual(curr_balance, cashier.get_available_balance())
