# from django.contrib.auth.models import User
# from django.test import TestCase
#
# from account.models import Account
# from agent.models import Agent
# from matches.models import Match, MatchScore
# from sports.models import Group, Sport
# # Create your tests here.
# from teams.models import Team
# from toolkit.wagers.scoring_tools import calculate_decimal_payout
# from toolkit.wagers.thequalifier import TheQualifier
# from wager.models import Wager
#
# qualifier = TheQualifier()
#
# class DynamicWagerTests(TestCase):
#     @classmethod
#     def setUp(cls):
#         cls.team_1 = Team.objects.get_or_create(key="test_team_1", name="Test Team 1")[0]
#         cls.team_2 = Team.objects.get_or_create(key="test_team_2", name="Test Team 2")[0]
#         cls.group = Group.objects.get_or_create(slug="test", icon="test_icon", name="test sport", generic_icon="test_genicon")[0]
#         cls.sport = Sport.objects.get_or_create(key="test_sport", group=cls.group, title="sport_title", wager_limit=100000)[0]
#         cls.match = Match.objects.get_or_create(sport=cls.sport,home_team=cls.team_1,away_team=cls.team_2,status_short="Q1")[0]
#         cls.match.save()
#         cls.user = User.objects.get_or_create(username="lilith")[0]
#         cls.user.save()
#         cls.agent = Agent.objects.get_or_create(user=cls.user)[0]
#         cls.account = Account.objects.get_or_create(acctnum=10166,agent=cls.agent)[0]
#
#     def test_dynamic_spreads_h1_test1(self):
#         match_score_1 = MatchScore(match=self.match, team=self.team_2, score=46, winner=True,score_data={"quarter_1":15,"quarter_2":16,"quarter_3":0,"quarter_4":15})
#         match_score_1.save()
#         match_score_2 = MatchScore(match=self.match, team=self.team_1, score=20,score_data={"quarter_1":5,"quarter_2":5,"quarter_3":5,"quarter_4":5})
#         match_score_2.save()
#         risk = 1000
#         win = 1800
#         base = 110
#         wager = Wager(account=self.account,team_1=self.team_1,type="DY",
#                       risk=risk,win=win,base_spread=base,match=self.match,bet_data={"base": base, "risk": risk, "type": "dynamic", "points": 3.5, "price": 2.0,"period":"H1",
#                      "tuuid": str(self.team_1.uuid), "to_win": win, "dynamic": "spreads_h1"})
#         self.assertEqual(wager.risk,risk)
#         self.assertEqual(round(wager.win,2),win)
#         wager.save()
#         self.assertEqual(qualifier.qualify_bet(wager),False)
#         self.assertEqual(wager.status,"L")
#         wager.delete()
#         wager = Wager(account=self.account, team_1=self.team_2, type="DY",
#                       risk=risk, win=win, base_spread=base, match=self.match,
#                       bet_data={"base": base, "risk": risk, "type": "dynamic", "points": 3.5, "price": 2.0,"period":"H1",
#                                 "tuuid": str(self.team_2.uuid), "to_win": win, "dynamic": "spreads_h1"})
#         self.assertEqual(wager.risk, risk)
#         self.assertEqual(round(wager.win, 2), win)
#         wager.save()
#         self.assertEqual(qualifier.qualify_bet(wager), True)
#         self.assertEqual(wager.status, "W")
#         match_score_1.score = 35
#         match_score_1.save()
#         wager = Wager(account=self.account,team_1=self.team_2,type="DY",
#                       risk=risk,win=win,base_spread=base,match=self.match,bet_data={"base": base, "risk": risk, "type": "dynamic", "points": 3.5, "price": 2.0,"period":"H2",
#                      "tuuid": str(self.team_1.uuid), "to_win": win, "dynamic": "spreads_h1"})
#         wager.save()
#         self.assertEqual(qualifier.qualify_bet(wager), True)
#         self.assertEqual(wager.status, "W")
#
#
#
#     def test_dynamic_spreads_qs_test1(self):
#         match_score_1 = MatchScore(match=self.match, team=self.team_1, score=30, winner=True,score_data={"quarter_1":7,"quarter_2":7,"quarter_3":7,"quarter_4":9})
#         match_score_1.save()
#         match_score_2 = MatchScore(match=self.match, team=self.team_2, score=20,score_data={"quarter_1":5,"quarter_2":5,"quarter_3":5,"quarter_4":5})
#         match_score_2.save()
#         risk = 1000
#         win = 1800
#         base = 110
#         wager = Wager(account=self.account,team_1=self.team_1,type="DY",
#                       risk=risk,win=win,base_spread=base,match=self.match,bet_data={"base": base, "risk": risk, "type": "dynamic", "points": 2.5, "price": 2.0, "period":"Q1",
#                      "tuuid": str(self.team_1.uuid), "to_win": win, "dynamic": "spreads_q1"})
#         self.assertEqual(wager.risk,risk)
#         self.assertEqual(round(wager.win,2),win)
#         wager.save()
#         self.assertEqual(qualifier.qualify_bet(wager),False)
#         self.assertEqual(wager.status,"L")
#         wager.delete()
#         wager = Wager(account=self.account, team_1=self.team_1, type="DY",
#                       risk=risk, win=win, base_spread=base, match=self.match,
#                       bet_data={"base": base, "risk": risk, "type": "dynamic", "points": 5.5, "price": 2.0, "period":"Q2",
#                                 "tuuid": str(self.team_1.uuid), "to_win": win, "dynamic": "spreads_q2"})
#         self.assertEqual(wager.risk, risk)
#         self.assertEqual(round(wager.win, 2), win)
#         wager.save()
#         self.assertEqual(qualifier.qualify_bet(wager), False)
#         self.assertEqual(wager.status, "L")
#         wager.delete()
#         match_score_1.score = 36
#         match_score_1.save()
#         wager = Wager(account=self.account,team_1=self.team_2,type="DY",
#                       risk=risk,win=win,base_spread=base,match=self.match,bet_data={"base": base, "risk": risk, "type": "dynamic", "points": 8.5, "price": 2.0,"period":"Q3",
#                      "tuuid": str(self.team_2.uuid), "to_win": win, "dynamic": "spreads_q3"})
#         wager.save()
#         self.assertEqual(qualifier.qualify_bet(wager), True)
#         self.assertEqual(wager.status, "W")
#         wager.delete()
#         match_score_1.score = 8
#         match_score_1.save()
#         wager = Wager(account=self.account,team_1=self.team_2,type="DY",
#                       risk=risk,win=win,base_spread=base,match=self.match,bet_data={"base": base, "risk": risk, "type": "dynamic", "points": 8.5, "price": 2.0,"period":"Q4",
#                      "tuuid": str(self.team_2.uuid), "to_win": win, "dynamic": "spreads_q4"})
#         wager.save()
#         self.assertEqual(qualifier.qualify_bet(wager), True)
#         self.assertEqual(wager.status, "W")
#
#     def test_dynamic_totals_test1(self):
#         match_score_1 = MatchScore(match=self.match, team=self.team_1, score=28, winner=True,score_data={"quarter_1":7,"quarter_2":7,"quarter_3":7,"quarter_4":7})
#         match_score_1.save()
#         match_score_2 = MatchScore(match=self.match, team=self.team_2, score=36,score_data={"quarter_1":9,"quarter_2":9,"quarter_3":9,"quarter_4":9})
#         match_score_2.save()
#         risk = 1000
#         win = calculate_decimal_payout(risk,2.0)
#         base = 110
#         wager = Wager(account=self.account,team_1=self.team_2,type="DY",
#                       risk=risk,win=win,base_spread=base,match=self.match,bet_data={"base": base, "risk": risk, "type": "dynamic", "totals":"under", "points": 8.5, "price": 2.0,"period":"H1",
#                      "tuuid": str(self.team_2.uuid), "to_win": win, "dynamic": "totals_h1"})
#         wager.save()
#         self.assertEqual(qualifier.qualify_bet(wager), False)
#         self.assertEqual(wager.status, "L")
#         self.assertEqual(wager.win,2000)
#         wager.delete()
#
#         wager = Wager(account=self.account,team_1=self.team_2,type="DY",
#                       risk=risk,win=win,base_spread=base,match=self.match,bet_data={"base": base, "risk": risk, "type": "dynamic", "totals":"over", "points": 17.5, "price": 2.0,"period":"H2",
#                      "tuuid": str(self.team_2.uuid), "to_win": win, "dynamic": "totals_h2"})
#         wager.save()
#         self.assertEqual(qualifier.qualify_bet(wager), True)
#         self.assertEqual(wager.status, "W")
#         wager.delete()
#         wager = Wager(account=self.account,team_1=self.team_2,type="DY",
#                       risk=risk,win=win,base_spread=base,match=self.match,bet_data={"base": base, "risk": risk, "type": "dynamic", "totals":"under", "points": 8.5, "price": 2.0,"period":"Q1",
#                      "tuuid": str(self.team_2.uuid), "to_win": win, "dynamic": "totals_q1"})
#         wager.save()
#         self.assertEqual(qualifier.qualify_bet(wager), False)
#         self.assertEqual(wager.status, "L")
#         wager.delete()
#
#         wager = Wager(account=self.account,team_1=self.team_1,type="DY",
#                       risk=risk,win=win,base_spread=base,match=self.match,bet_data={"base": base, "risk": risk, "type": "dynamic", "totals":"over", "points": 17.5, "price": 2.0,"period":"Q2",
#                      "tuuid": str(self.team_2.uuid), "to_win": win, "dynamic": "totals_q2"})
#         wager.save()
#         self.assertEqual(qualifier.qualify_bet(wager), False)
#         self.assertEqual(wager.status, "L")
#         wager.delete()
#         wager = Wager(account=self.account, team_1=self.team_2, type="DY",
#                       risk=risk, win=win, base_spread=base, match=self.match, bet_data={"base": base, "risk": risk, "type": "dynamic", "totals": "under", "points": 8.5, "price": 2.0,"period":"Q3",
#                                                                                         "tuuid": str(self.team_2.uuid), "to_win": win, "dynamic": "totals_q3"})
#         wager.save()
#         self.assertEqual(qualifier.qualify_bet(wager), False)
#         self.assertEqual(wager.status, "L")
#         wager.delete()
#
#         wager = Wager(account=self.account, team_1=self.team_1, type="DY",
#                       risk=risk, win=win, base_spread=base, match=self.match, bet_data={"base": base, "risk": risk, "type": "dynamic", "totals": "over", "points": 17.5, "price": 2.0,"period":"Q4",
#                                                                                         "tuuid": str(self.team_2.uuid), "to_win": win, "dynamic": "totals_q4"})
#         wager.save()
#         self.assertEqual(qualifier.qualify_bet(wager), False)
#         self.assertEqual(wager.status, "L")
#         wager.delete()
#
#     def test_dynamic_h2h_test1(self):
#         match_score_1 = MatchScore(match=self.match, team=self.team_1, score=12,score_data={"quarter_1":3,"quarter_2":3,"quarter_3":3,"quarter_4":3})
#         match_score_1.save()
#         match_score_2 = MatchScore(match=self.match, team=self.team_2, score=24,winner=True,score_data={"quarter_1":6,"quarter_2":6,"quarter_3":6,"quarter_4":6})
#         match_score_2.save()
#         risk = 1000
#         base=110
#         price=3.5
#         win = calculate_decimal_payout(1000,price)
#         wager = Wager(account=self.account, team_1=self.team_2, type="DY",
#                       risk=risk, win=win, base_spread=base, match=self.match, bet_data={"base": base, "risk": risk, "type": "dynamic", "price": 2.0,"period":"Q4",
#                                                                                         "tuuid": str(self.team_2.uuid), "to_win": win, "dynamic": "totals_q4"})
#         wager.save()