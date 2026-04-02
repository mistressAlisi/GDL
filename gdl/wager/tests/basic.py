# import random
# import string
# from decimal import Decimal
#
# from django.contrib.auth.models import User
# from django.test import TestCase
#
# from account.models import Account
# from agent.models import Agent
# from matches.models import Match, MatchScore
# from sports.models import Group, Sport
# # Create your tests here.
# from teams.models import Team
# from toolkit.wagers.scoring_tools import calculate_straight_bet_wins, calculate_moneyline_payout, \
#     calculate_spread_total_wins, calculate_parlay_total_wins
# from toolkit.wagers.thequalifier import TheQualifier
# from wager.models import Wager
#
# qualifier = TheQualifier()
#
# class WagerTests(TestCase):
#     @classmethod
#     def setUp(cls):
#         cls.team_1 = Team.objects.get_or_create(key="test_team_1", name="Test Team 1")[0]
#         cls.team_2 = Team.objects.get_or_create(key="test_team_2", name="Test Team 2")[0]
#         cls.group = Group.objects.get_or_create(slug="test", icon="test_icon", name="test sport", generic_icon="test_genicon")[0]
#         cls.sport = Sport.objects.get_or_create(key="test_sport", group=cls.group, title="sport_title", wager_limit=100000)[0]
#         cls.match = Match.objects.get_or_create(sport=cls.sport,home_team=cls.team_1,away_team=cls.team_2)[0]
#         cls.user = User.objects.get_or_create(username="lilith")[0]
#         cls.user.save()
#         cls.agent = Agent.objects.get_or_create(user=cls.user)[0]
#         actnum = random.randint(100200,101000)
#         cls.account = Account.objects.get_or_create(acctnum=actnum,agent=cls.agent)[0]
#
#     def test_straight_wager_plus_110_won(self):
#         wager = Wager(account=self.account,team_1=self.team_1,type="ST",risk=1000,win=calculate_straight_bet_wins(1000,110),base_spread=110,match=self.match)
#         self.assertEqual(wager.risk,1000)
#         self.assertEqual(round(wager.win,2),2100)
#         wager.save()
#         match_score_1 = MatchScore(match=self.match,team=self.team_1,score=30,winner=True)
#         match_score_1.save()
#         match_score_2 = MatchScore(match=self.match,team=self.team_2,score=24)
#         match_score_2.save()
#         self.match.winner = self.team_1
#         self.match.finished = True
#         self.match.save()
#         self.assertEqual(qualifier._qual_straight_bet(wager),True)
#         self.assertEqual(wager.status,"W")
#
#     def test_straight_wager_plus_110_lost(self):
#         wager = Wager(account=self.account,team_1=self.team_1,type="ST",risk=1000,win=calculate_straight_bet_wins(1000,110),base_spread=110,match=self.match)
#         wager.save()
#         match_score_1 = MatchScore(match=self.match,team=self.team_1,score=20)
#         match_score_1.save()
#         match_score_2 = MatchScore(match=self.match,team=self.team_2,score=34,winner=True)
#         match_score_2.save()
#         self.match.winner = self.team_2
#         self.match.finished = True
#         self.match.save()
#         self.assertEqual(qualifier._qual_straight_bet(wager),False)
#         self.assertEqual(wager.status,"L")
#
#     def test_straight_wager_minus_110(self):
#         wager = Wager(account=self.account, team_1=self.team_1, type="ST", risk=1000,
#                       win=calculate_straight_bet_wins(1000, -110), base_spread=-110,match=self.match)
#         self.assertEqual(wager.risk, 1000)
#         self.assertEqual(round(wager.win, 2), 1909)
#         wager.save()
#         match_score_1 = MatchScore(match=self.match,team=self.team_1,score=30,winner=True)
#         match_score_1.save()
#         match_score_2 = MatchScore(match=self.match,team=self.team_2,score=24)
#         match_score_2.save()
#         self.match.winner = self.team_1
#         self.match.finished = True
#         self.match.save()
#         self.assertEqual(qualifier._qual_straight_bet(wager),True)
#         self.assertEqual(wager.status,"W")
#
#     def test_moneyline_wager_plus_110_win(self):
#         bet_data = {"risk": 1000, "ml": 150}
#         wager = Wager(account=self.account, team_1=self.team_1, type="ML", risk=1000,
#                       win=calculate_moneyline_payout(1000, 110), base_spread=110,match=self.match,bet_data=bet_data)
#         self.assertEqual(wager.risk, 1000)
#         self.assertEqual(round(wager.win, 2), 2100)
#         wager.save()
#         match_score_1 = MatchScore(match=self.match,team=self.team_1,score=30,winner=True)
#         match_score_1.save()
#         match_score_2 = MatchScore(match=self.match,team=self.team_2,score=24)
#         match_score_2.save()
#         self.match.winner = self.team_1
#         self.match.finished = True
#         self.match.save()
#         self.assertEqual(qualifier._qualify_moneyline(wager),True)
#         self.assertEqual(wager.status,"W")
#
#
#
#     def test_moneyline_wager_minus_110_win(self):
#         bet_data = {"risk":1000,"ml":150}
#         wager = Wager(account=self.account, team_1=self.team_1, type="ML", risk=1000,
#                       win=calculate_moneyline_payout(1000, -110), base_spread=-110,match=self.match,bet_data=bet_data)
#         self.assertEqual(wager.risk, 1000)
#         self.assertEqual(round(wager.win, 2), 1909)
#         wager.save()
#         match_score_1 = MatchScore(match=self.match,team=self.team_1,score=30,winner=True)
#         match_score_1.save()
#         match_score_2 = MatchScore(match=self.match,team=self.team_2,score=24)
#         match_score_2.save()
#         self.match.winner = self.team_1
#         self.match.finished = True
#         self.match.save()
#         self.assertEqual(qualifier._qualify_moneyline(wager),True)
#         self.assertEqual(wager.status,"W")
#
#     def test_moneyline_wager_plus_110_loss(self):
#         bet_data = {"risk": 1000, "ml": 150}
#         wager = Wager(account=self.account, team_1=self.team_2, type="ML", risk=1000,
#                       win=calculate_moneyline_payout(1000, 110), base_spread=110, match=self.match, bet_data=bet_data)
#         self.assertEqual(wager.risk, 1000)
#         self.assertEqual(round(wager.win, 2), 2100)
#         wager.save()
#         match_score_1 = MatchScore(match=self.match, team=self.team_1, score=30, winner=True)
#         match_score_1.save()
#         match_score_2 = MatchScore(match=self.match, team=self.team_2, score=24)
#         match_score_2.save()
#         self.match.winner = self.team_1
#         self.match.finished = True
#         self.match.save()
#         self.assertEqual(qualifier._qualify_moneyline(wager), False)
#         self.assertEqual(wager.status, "L")
#
#     def test_moneyline_wager_minus_110_loss(self):
#         bet_data = {"risk": 1000, "ml": 150}
#         wager = Wager(account=self.account, team_1=self.team_2, type="ML", risk=1000,
#                       win=calculate_moneyline_payout(1000, -110), base_spread=-110, match=self.match, bet_data=bet_data)
#         self.assertEqual(wager.risk, 1000)
#         self.assertEqual(round(wager.win, 2), 1909)
#         wager.save()
#         match_score_1 = MatchScore(match=self.match, team=self.team_1, score=30, winner=True)
#         match_score_1.save()
#         match_score_2 = MatchScore(match=self.match, team=self.team_2, score=24)
#         match_score_2.save()
#         self.match.winner = self.team_1
#         self.match.finished = True
#         self.match.save()
#         self.assertEqual(qualifier._qualify_moneyline(wager), False)
#         self.assertEqual(wager.status, "L")
#
#     def test_spread_wager_home_team_win_p5_30_24(self):
#         bet_data = {"points":5,"spread":10}
#         wager = Wager(account=self.account, team_1=self.team_1, type="SP", risk=1000,win=calculate_spread_total_wins(1000,110,100),match=self.match,bet_data=bet_data)
#         self.assertEqual(round(wager.win, 2), 1909)
#         wager.save()
#         match_score_1 = MatchScore(match=self.match,team=self.team_1,score=30,winner=True)
#         match_score_1.save()
#         match_score_2 = MatchScore(match=self.match,team=self.team_2,score=24)
#         match_score_2.save()
#         self.match.winner = self.team_1
#         self.match.finished = True
#         self.match.save()
#         qualifier = TheQualifier()
#         qual_spb_res = qualifier._qual_spread_bet(wager)
#         self.assertEqual(qual_spb_res,True)
#         # This should be a won wager:
#         self.assertEqual(wager.status,"W")
#
#     def test_spread_wager_home_team_loss_p5_20_30(self):
#         bet_data = {"points":5,"spread":10}
#         wager = Wager(account=self.account, team_1=self.team_1, type="SP", risk=1000,win=calculate_spread_total_wins(1000,110,100),match=self.match,bet_data=bet_data)
#         self.assertEqual(round(wager.win, 2), 1909)
#         wager.save()
#         match_score_1 = MatchScore(match=self.match,team=self.team_1,score=20)
#         match_score_1.save()
#         match_score_2 = MatchScore(match=self.match,team=self.team_2,score=30,winner=True)
#         match_score_2.save()
#         self.match.winner = self.team_2
#         self.match.finished = True
#         self.match.save()
#
#         qual_spb_res = qualifier._qual_spread_bet(wager)
#         self.assertEqual(qual_spb_res,False)
#         # This should be a Lost wager:
#         self.assertEqual(wager.status,"L")
#
#     def test_spread_wager_away_team_win_p3_24_28(self):
#         bet_data = {"points":3,"spread":6}
#         wager = Wager(account=self.account, team_1=self.team_2, type="SP", risk=1000,win=calculate_spread_total_wins(1000,110,100),match=self.match,bet_data=bet_data)
#         self.assertEqual(round(wager.win, 2), 1909)
#         wager.save()
#         match_score_1 = MatchScore(match=self.match,team=self.team_1,score=24)
#         match_score_1.save()
#         match_score_2 = MatchScore(match=self.match,team=self.team_2,score=28,winner=True)
#         match_score_2.save()
#         self.match.winner = self.team_2
#         self.match.finished = True
#         self.match.save()
#
#         qual_spb_res = qualifier._qual_spread_bet(wager)
#         self.assertEqual(qual_spb_res,True)
#         # This should be a won wager:
#         self.assertEqual(wager.status,"W")
#
#
#     def test_spread_wager_away_team_loss_p3_30_26(self):
#         bet_data = {"points":3,"spread":6}
#         wager = Wager(account=self.account, team_1=self.team_2, type="SP", risk=1000,win=calculate_spread_total_wins(1000,110,100),match=self.match,bet_data=bet_data)
#         self.assertEqual(round(wager.win, 2), 1909)
#         wager.save()
#         match_score_1 = MatchScore(match=self.match,team=self.team_1,score=30,winner=True)
#         match_score_1.save()
#         match_score_2 = MatchScore(match=self.match,team=self.team_2,score=26)
#         match_score_2.save()
#         self.match.winner = self.team_1
#         self.match.finished = True
#         self.match.save()
#
#         qual_spb_res = qualifier._qual_spread_bet(wager)
#         self.assertEqual(qual_spb_res,False)
#         # This should be a lost wager:
#         self.assertEqual(wager.status,"L")
#
#     def test_totals_wager_away_team_o51_24_28_win(self):
#         bet_data = {"points":51,"spread":6,"type":"totals-over"}
#         wager = Wager(account=self.account, team_1=self.team_2, type="TO", risk=1000,win=calculate_spread_total_wins(1000,110,100),match=self.match,bet_data=bet_data)
#         self.assertEqual(round(wager.win, 2), 1909)
#         wager.save()
#         match_score_1 = MatchScore(match=self.match,team=self.team_1,score=24)
#         match_score_1.save()
#         match_score_2 = MatchScore(match=self.match,team=self.team_2,score=28,winner=True)
#         match_score_2.save()
#         self.match.winner = self.team_2
#         self.match.finished = True
#         self.match.save()
#
#         qual_spb_res = qualifier._qual_totals_bet(wager)
#         self.assertEqual(qual_spb_res,True)
#         # This should be a won wager:
#         self.assertEqual(wager.status,"W")
#
#
#     def test_totals_wager_away_team_o51_24_21_loss(self):
#         bet_data = {"points":51,"spread":6,"type":"totals-over"}
#         wager = Wager(account=self.account, team_1=self.team_2, type="TO", risk=1000,win=calculate_spread_total_wins(1000,110,100),match=self.match,bet_data=bet_data)
#         self.assertEqual(round(wager.win, 2), 1909)
#         wager.save()
#         match_score_1 = MatchScore(match=self.match,team=self.team_1,score=21)
#         match_score_1.save()
#         match_score_2 = MatchScore(match=self.match,team=self.team_2,score=24,winner=True)
#         match_score_2.save()
#         self.match.winner = self.team_2
#         self.match.finished = True
#         self.match.save()
#
#         qual_spb_res = qualifier._qual_totals_bet(wager)
#         self.assertEqual(qual_spb_res,False)
#         # This should be a lost wager:
#         self.assertEqual(wager.status,"L")
#
#
#     def test_totals_wager_away_team_u51_24_28_loss(self):
#         bet_data = {"points":51,"spread":6,"type":"totals-under"}
#         wager = Wager(account=self.account, team_1=self.team_2, type="TO", risk=1000,win=calculate_spread_total_wins(1000,110,100),match=self.match,bet_data=bet_data)
#         self.assertEqual(round(wager.win, 2), 1909)
#         wager.save()
#         match_score_1 = MatchScore(match=self.match,team=self.team_1,score=24)
#         match_score_1.save()
#         match_score_2 = MatchScore(match=self.match,team=self.team_2,score=28,winner=True)
#         match_score_2.save()
#         self.match.winner = self.team_2
#         self.match.finished = True
#         self.match.save()
#
#         qual_spb_res = qualifier._qual_totals_bet(wager)
#         self.assertEqual(qual_spb_res,False)
#         # This should be a lost wager:
#         self.assertEqual(wager.status,"L")
#
#
#     def test_totals_wager_away_team_u51_24_21_win(self):
#         bet_data = {"points":51,"spread":6,"type":"totals-under"}
#         wager = Wager(account=self.account, team_1=self.team_2, type="TO", risk=1000,win=calculate_spread_total_wins(1000,110,100),match=self.match,bet_data=bet_data)
#         self.assertEqual(round(wager.win, 2), 1909)
#         wager.save()
#         match_score_1 = MatchScore(match=self.match,team=self.team_1,score=21)
#         match_score_1.save()
#         match_score_2 = MatchScore(match=self.match,team=self.team_2,score=24,winner=True)
#         match_score_2.save()
#         self.match.winner = self.team_2
#         self.match.finished = True
#         self.match.save()
#
#         qual_spb_res = qualifier._qual_totals_bet(wager)
#         self.assertEqual(qual_spb_res,True)
#         # This should be a won wager:
#         self.assertEqual(wager.status,"W")
#
#
#
#     def test_three_leg_parlay_win(self):
#         # Setup: Create matches.
#         matches = []
#         for home,away,hscore,ascore in [
#             ["76ers","49ers",30,20],
#             ["49ers","phillies",28,48],
#             ["phillies","flyers",60,50]
#         ]:
#             home_team  = Team.objects.get_or_create(key=home,name=home)[0]
#             home_team.save()
#             away_team = Team.objects.get_or_create(key=away,name=away)[0]
#             away_team.save()
#             match_id =  ''.join(random.choices(string.ascii_letters,k=10))
#             match = Match.objects.get_or_create(home_team=home_team,away_team=away_team,sport=self.sport,id=match_id)[0]
#             match.save()
#             match_score_1 = MatchScore(match=match, team=home_team, score=hscore)
#             match_score_2 = MatchScore(match=match, team=away_team, score=ascore)
#             if hscore > ascore:
#                 match_score_1.winner = True
#                 match.winner = home_team
#             else:
#                 match_score_2.winner = True
#                 match.winner = away_team
#             match.finished = True
#             match.save()
#             match_score_2.save()
#             match_score_1.save()
#             matches.append(match)
#
#         # Now, create three parlay wagers:
#         nodes = []
#         wagers = []
#         # Root wager first:
#         bet_data = {"final_odds":3.1415,"risk":1008,"root_wager":True,"nodes":[],"type":"spread-home-team","points":3}
#         home_team = Team.objects.get(key="76ers", name="76ers")
#         root_wager = Wager(account=self.account, team_1=home_team, type="PA", risk=1000,
#                            win=calculate_parlay_total_wins(bet_data["risk"],bet_data["final_odds"]),
#                            match=matches[0], bet_data=bet_data)
#         root_wager.save()
#         # Now, two more legs:
#         bet_data = {"points": 5, "risk": 1000, "parent": str(root_wager.uuid),
#                     "type": "spread-away-team"}
#         away_team = Team.objects.get(key="phillies", name="phillies")
#         wager = Wager(account=self.account, team_1=away_team, type="PA",
#                        match=matches[1], bet_data=bet_data)
#         wager.save()
#         wagers.append(wager)
#         nodes.append(str(wager.uuid))
#
#         bet_data = {"points": 2, "risk": 1000, "parent": str(root_wager.uuid),
#                     "type": "spread-away-team"}
#         home_team = Team.objects.get(key="phillies", name="phillies")
#         wager = Wager(account=self.account, team_1=home_team, type="PA",
#                        match=matches[2], bet_data=bet_data)
#         wager.save()
#         wagers.append(wager)
#         nodes.append(str(wager.uuid))
#         # Save root nodes:
#         root_wager.bet_data["nodes"] = nodes
#         # Now, save everything and assert correct creation:
#         root_wager.save()
#         # Links and relations:
#         self.assertEqual(root_wager.bet_data["nodes"], nodes)
#         for wager in wagers:
#             self.assertEqual(wager.bet_data["parent"],str(root_wager.uuid))
#         # Amount to win: Hydrogen times Pi, Carl. :)
#         self.assertAlmostEqual(Decimal(root_wager.win),Decimal(1008*3.1415),10)
#
#         # Now, let's qualify some wagers:
#         qRw = qualifier.qualify_bet(root_wager)
#         self.assertEqual(qRw,True)
#         for wager in wagers:
#             qualifier._parlay_node_qualify(wager)
#             self.assertEqual(wager.status,"W",f"Wager {wager.uuid} not won!")
#
#
#
#
#
#
#
#
#
#
#     def test_three_leg_parlay_loose(self):
#         # Setup: Create matches.
#         matches = []
#         for home,away,hscore,ascore in [
#             ["76ers","49ers",30,20],
#             ["49ers","phillies",28,29],
#             ["phillies","flyers",60,50]
#         ]:
#             home_team  = Team.objects.get_or_create(key=home,name=home)[0]
#             home_team.save()
#             away_team = Team.objects.get_or_create(key=away,name=away)[0]
#             away_team.save()
#             match_id =  ''.join(random.choices(string.ascii_letters,k=10))
#             match = Match.objects.get_or_create(home_team=home_team,away_team=away_team,sport=self.sport,id=match_id)[0]
#             match.save()
#             match_score_1 = MatchScore(match=match, team=home_team, score=hscore)
#             match_score_2 = MatchScore(match=match, team=away_team, score=ascore)
#             if hscore > ascore:
#                 match_score_1.winner = True
#                 match.winner = home_team
#             else:
#                 match_score_2.winner = True
#                 match.winner = away_team
#             match.finished = True
#             match.save()
#             match_score_2.save()
#             match_score_1.save()
#             matches.append(match)
#
#         # Now, create three parlay wagers:
#         nodes = []
#         wagers = []
#         # Root wager first:
#         bet_data = {"final_odds":3.1415,"risk":1008,"root_wager":True,"nodes":[],"type":"spread-home-team","points":11}
#         home_team = Team.objects.get(key="76ers", name="76ers")
#         root_wager = Wager(account=self.account, team_1=home_team, type="PA", risk=1000,
#                            win=calculate_parlay_total_wins(bet_data["risk"],bet_data["final_odds"]),
#                            match=matches[0], bet_data=bet_data)
#         root_wager.save()
#         # Now, two more legs:
#         bet_data = {"points": 3, "risk": 1000, "parent": str(root_wager.uuid),
#                     "type": "spread-away-team"}
#         away_team = Team.objects.get(key="phillies", name="phillies")
#         wager = Wager(account=self.account, team_1=away_team, type="PA",
#                        match=matches[1], bet_data=bet_data)
#         wager.save()
#         wagers.append(wager)
#         nodes.append(str(wager.uuid))
#
#         bet_data = {"points": 2, "risk": 1000, "parent": str(root_wager.uuid),
#                     "type": "spread-away-team"}
#         home_team = Team.objects.get(key="phillies", name="phillies")
#         wager = Wager(account=self.account, team_1=home_team, type="PA",
#                        match=matches[2], bet_data=bet_data)
#         wager.save()
#         wagers.append(wager)
#         nodes.append(str(wager.uuid))
#         # Save root nodes:
#         root_wager.bet_data["nodes"] = nodes
#         # Now, save everything and assert correct creation:
#         root_wager.save()
#         # Links and relations:
#         self.assertEqual(root_wager.bet_data["nodes"], nodes)
#         for wager in wagers:
#             self.assertEqual(wager.bet_data["parent"],str(root_wager.uuid))
#         # Amount to win: Hydrogen times Pi, Carl. :)
#         self.assertAlmostEqual(Decimal(root_wager.win),Decimal(1008*3.1415),10)
#
#         # Now, let's qualify some wagers:
#         qRw = qualifier.qualify_bet(root_wager)
#         self.assertEqual(qRw,False)
#
#
#
#
#
#
#
#
#
#
