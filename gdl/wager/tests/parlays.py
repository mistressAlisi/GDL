# from decimal import Decimal
# from random import randint,choices
#
# from django.contrib.auth.models import User
# from django.test import TestCase
#
# from account.models import Account
# from agent.models import Agent
# from cashier.models import ParlayPayoutRuleset, ParlayPayoutRulesetEntry
# from qualifier.toolkit.parlays import  parlay_decimal_odds
# from matches.models import Match, MatchScore
# from odds.models import Bookmaker, MatchOddsSummary
# from parameters.models import  VHost
# from sports.models import Group, Sport
# # Create your tests here.
# from teams.models import Team
# from toolkit import string
# from toolkit.wagers.scoring_tools import calculate_decimal_payout, calculate_parlay_total_wins
# from toolkit.wagers.thequalifier import TheQualifier
# from wager.models import Wager
#
# qualifier = TheQualifier()
#
# class ParlayWagerTests(TestCase):
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
#         cls.vhost = VHost.objects.get_or_create(name="testdomain")[0]
#         actnum = randint(100200,101000)
#         cls.account = Account.objects.get_or_create(acctnum=actnum,agent=cls.agent)[0]
#
#     def test_dynamic_three_leg_parlays_win(self):
#         # Setup: Create matches.
#         matches = []
#         for home, away, hscore, ascore in [
#             ["76ers", "49ers", 30, 20],
#             ["49ers", "phillies", 28, 48],
#             ["phillies", "flyers", 60, 50]
#         ]:
#             home_team = Team.objects.get_or_create(key=home, name=home)[0]
#             home_team.save()
#             away_team = Team.objects.get_or_create(key=away, name=away)[0]
#             away_team.save()
#             match_id = string.random_string(32)
#             match = Match.objects.get_or_create(home_team=home_team, away_team=away_team, sport=self.sport, id=match_id)[0]
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
#             match.score_closed = True
#             match.save()
#             match_score_2.save()
#             match_score_1.save()
#             matches.append(match)
#         # Setup a rules object:
#         rlst1 = ParlayPayoutRuleset(name="Rule Test 1")
#         self.agent.save()
#         self.vhost.save()
#         rlst1.save()
#         rlst1.agents.set([self.agent])
#         rlst1.vhosts.set([self.vhost])
#         pprs = ParlayPayoutRulesetEntry.objects.get_or_create(ruleset=rlst1,parlay_legs=3,max_losses=0)[0]
#         pprs.save()
#         # print(pprs)
#         # Now, create three parlay wagers:
#         nodes = []
#         wagers = []
#         # Root wager first:
#         bet_data = {"final_odds": 3.1415, "risk": 1008, "root_wager": True, "nodes": [], "type": "straight-home-team",
#                     "points": 3,"dynamic":True}
#         home_team = Team.objects.get(key="76ers", name="76ers")
#         root_wager = Wager(account=self.account, team_1=home_team, type="PA", risk=1000,
#                            win=calculate_parlay_total_wins(bet_data["risk"], bet_data["final_odds"]),
#                            match=matches[0], bet_data=bet_data,parlay_ruleset=rlst1)
#         root_wager.save()
#         # Now, two more legs:
#         bet_data = {"points": 5, "risk": 1000, "parent": str(root_wager.uuid),
#                     "type": "straight-away-team","dynamic":True}
#         away_team = Team.objects.get(key="phillies", name="phillies")
#         wager = Wager(account=self.account, team_1=away_team, type="PA",
#                       match=matches[1], bet_data=bet_data,parlay_ruleset=rlst1)
#         wager.save()
#         wagers.append(wager)
#         nodes.append(str(wager.uuid))
#
#         bet_data = {"points": 2, "risk": 1000, "parent": str(root_wager.uuid),
#                     "type": "spread-away-team"}
#         home_team = Team.objects.get(key="phillies", name="phillies")
#         wager = Wager(account=self.account, team_1=home_team, type="PA",
#                       match=matches[2], bet_data=bet_data,parlay_ruleset=rlst1)
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
#             self.assertEqual(wager.bet_data["parent"], str(root_wager.uuid))
#         # Amount to win: Hydrogen times Pi, Carl. :)
#         self.assertAlmostEqual(Decimal(root_wager.win), Decimal(1008 * 3.1415), 10)
#
#         # Setup complete
#         # Win all:
#         root_wager.match.finished = True
#         root_wager.match.scores_closed = True
#         root_wager.save()
#         self.assertTrue(qualifier._qual_parlay_bet_dynamic(wager))
#
#     def test_dynamic_three_leg_parlays_loose(self):
#         # Setup: Create matches.
#         matches = []
#         for home, away, hscore, ascore in [
#             ["76ers", "49ers", 30, 20],
#             ["49ers", "phillies", 28, 48],
#             ["phillies", "flyers", 60, 50]
#         ]:
#             home_team = Team.objects.get_or_create(key=home, name=home)[0]
#             home_team.save()
#             away_team = Team.objects.get_or_create(key=away, name=away)[0]
#             away_team.save()
#             match_id = string.random_string(32)
#             match = \
#             Match.objects.get_or_create(home_team=home_team, away_team=away_team, sport=self.sport, id=match_id)[0]
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
#             match.score_closed = True
#             match.save()
#             match_score_2.save()
#             match_score_1.save()
#             matches.append(match)
#         # Setup a rules object:
#         rlst1 = ParlayPayoutRuleset(name="Rule Test 1")
#         self.agent.save()
#         self.vhost.save()
#         rlst1.save()
#         rlst1.agents.set([self.agent])
#         rlst1.vhosts.set([self.vhost])
#         pprs = ParlayPayoutRulesetEntry.objects.get_or_create(ruleset=rlst1, parlay_legs=3, max_losses=0)[0]
#         pprs.save()
#         # print(pprs)
#         # Now, create three parlay wagers:
#         nodes = []
#         wagers = []
#         # Root wager first:
#         bet_data = {"final_odds": 3.1415, "risk": 1008, "root_wager": True, "nodes": [], "type": "straight-home-team",
#                     "points": 3, "dynamic": True}
#         home_team = Team.objects.get(key="49ers", name="49ers")
#         root_wager = Wager(account=self.account, team_1=home_team, type="PA", risk=1000,
#                            win=calculate_parlay_total_wins(bet_data["risk"], bet_data["final_odds"]),
#                            match=matches[0], bet_data=bet_data, parlay_ruleset=rlst1)
#         root_wager.save()
#         # Now, two more legs:
#         bet_data = {"points": 5, "risk": 1000, "parent": str(root_wager.uuid),
#                     "type": "straight-away-team", "dynamic": True}
#         away_team = Team.objects.get(key="phillies", name="phillies")
#         wager = Wager(account=self.account, team_1=away_team, type="PA",
#                       match=matches[1], bet_data=bet_data, parlay_ruleset=rlst1)
#         wager.save()
#         wagers.append(wager)
#         nodes.append(str(wager.uuid))
#
#         bet_data = {"points": 2, "risk": 1000, "parent": str(root_wager.uuid),
#                     "type": "spread-away-team"}
#         home_team = Team.objects.get(key="phillies", name="phillies")
#         wager = Wager(account=self.account, team_1=home_team, type="PA",
#                       match=matches[2], bet_data=bet_data, parlay_ruleset=rlst1)
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
#             self.assertEqual(wager.bet_data["parent"], str(root_wager.uuid))
#         # Amount to win: Hydrogen times Pi, Carl. :)
#         self.assertAlmostEqual(Decimal(root_wager.win), Decimal(1008 * 3.1415), 10)
#
#         # Setup complete
#         # Win all:
#         root_wager.match.finished = True
#         root_wager.match.scores_closed = True
#         root_wager.save()
#         self.assertFalse(qualifier._qual_parlay_bet_dynamic(wager))
#
#     def test_dynamic_five_leg_parlays_not_ready(self):
#         # Setup: Create matches.
#         matches = []
#         i = 0
#         for home, away, hscore, ascore in [
#             ["76ers", "49ers", 30, 20],
#             ["49ers", "phillies", 28, 48],
#             ["phillies", "flyers", 60, 50],
#             ["dodgers","giants",10,10],
#             ["warriors","knicks",108,120],
#         ]:
#             home_team = Team.objects.get_or_create(key=home, name=home)[0]
#             home_team.save()
#             away_team = Team.objects.get_or_create(key=away, name=away)[0]
#             away_team.save()
#             match_id = string.random_string(32)
#             match = \
#             Match.objects.get_or_create(home_team=home_team, away_team=away_team, sport=self.sport, id=match_id)[0]
#             match.save()
#             match_score_1 = MatchScore(match=match, team=home_team, score=hscore)
#             match_score_2 = MatchScore(match=match, team=away_team, score=ascore)
#             if hscore > ascore:
#                 match_score_1.winner = True
#                 match.winner = home_team
#             else:
#                 match_score_2.winner = True
#                 match.winner = away_team
#             if i%2 == 0:
#                 match.finished = True
#                 match.score_closed = True
#             match.save()
#             match_score_2.save()
#             match_score_1.save()
#             matches.append(match)
#             i += 1
#         # Setup a rules object:
#         rlst1 = ParlayPayoutRuleset(name="Rule Test 1")
#         self.agent.save()
#         self.vhost.save()
#         rlst1.save()
#         rlst1.agents.set([self.agent])
#         rlst1.vhosts.set([self.vhost])
#         pprs = ParlayPayoutRulesetEntry.objects.get_or_create(ruleset=rlst1, parlay_legs=5, max_losses=0)[0]
#         pprs.save()
#         # print(pprs)
#         # Now, create three parlay wagers:
#         nodes = []
#         wagers = []
#         # Root wager first:
#         bet_data = {"final_odds": 3.1415, "risk": 1008, "root_wager": True, "nodes": [], "type": "straight-home-team",
#                     "points": 3, "dynamic": True}
#         home_team = Team.objects.get(key="76ers", name="76ers")
#         root_wager = Wager(account=self.account, team_1=away_team, type="PA", risk=1000,
#                            win=calculate_parlay_total_wins(bet_data["risk"], bet_data["final_odds"]),
#                            match=matches[0], bet_data=bet_data, parlay_ruleset=rlst1)
#         root_wager.save()
#         # Now, two more legs:
#         bet_data = {"points": 5, "risk": 1000, "parent": str(root_wager.uuid),
#                     "type": "straight-away-team", "dynamic": True}
#         away_team = Team.objects.get(key="phillies", name="phillies")
#         wager = Wager(account=self.account, team_1=away_team, type="PA",
#                       match=matches[1], bet_data=bet_data, parlay_ruleset=rlst1)
#         wager.save()
#         wagers.append(wager)
#         nodes.append(str(wager.uuid))
#
#         bet_data = {"points": 2, "risk": 1000, "parent": str(root_wager.uuid),
#                     "type": "spread-away-team"}
#         home_team = Team.objects.get(key="phillies", name="phillies")
#         wager = Wager(account=self.account, team_1=home_team, type="PA",
#                       match=matches[2], bet_data=bet_data, parlay_ruleset=rlst1)
#         wager.save()
#         wagers.append(wager)
#         nodes.append(str(wager.uuid))
#
#         bet_data = {"points": 2, "risk": 1000, "parent": str(root_wager.uuid),
#                     "type": "spread-away-team"}
#         home_team = Team.objects.get(key="dodgers", name="dodgers")
#         wager = Wager(account=self.account, team_1=home_team, type="PA",
#                       match=matches[3], bet_data=bet_data, parlay_ruleset=rlst1)
#         wager.save()
#         wagers.append(wager)
#         nodes.append(str(wager.uuid))
#
#         bet_data = {"points": 2, "risk": 1000, "parent": str(root_wager.uuid),
#                     "type": "spread-away-team"}
#         home_team = Team.objects.get(key="knicks", name="knicks")
#         wager = Wager(account=self.account, team_1=home_team, type="PA",
#                       match=matches[4], bet_data=bet_data, parlay_ruleset=rlst1)
#         wager.save()
#         wagers.append(wager)
#         nodes.append(str(wager.uuid))
#
#         # Save root nodes:
#         root_wager.bet_data["nodes"] = nodes
#         # Now, save everything and assert correct creation:
#         root_wager.save()
#         # Links and relations:
#         self.assertEqual(root_wager.bet_data["nodes"], nodes)
#         for wager in wagers:
#             self.assertEqual(wager.bet_data["parent"], str(root_wager.uuid))
#         # Amount to win: Hydrogen times Pi, Carl. :)
#         self.assertAlmostEqual(Decimal(root_wager.win), Decimal(1008 * 3.1415), 10)
#
#         # Setup complete
#         # Win all:
#         root_wager.match.finished = True
#         root_wager.match.scores_closed = True
#         root_wager.save()
#         self.assertIsNone(qualifier._qual_parlay_bet_dynamic(wager))
#
#     def test_dynamic_nine_leg_parlays_2_loss_eap(self):
#         # Setup: Create matches.
#         matches = []
#         i = 0
#         for home, away, hscore, ascore in [
#             ["76ers", "49ers", 30, 20],
#             ["49ers", "phillies", 28, 48],
#             ["phillies", "flyers", 60, 50],
#             ["dodgers","giants",11,10],
#             ["warriors","knicks",108,120],
#             ["packers", "steelers", 28, 48],
#             ["cowboys", "ravens", 60, 50],
#             ["america", "pumas", 11, 10],
#             ["nexaca", "toluca", 108, 120],
#         ]:
#             home_team = Team.objects.get_or_create(key=home, name=home)[0]
#             home_team.save()
#             away_team = Team.objects.get_or_create(key=away, name=away)[0]
#             away_team.save()
#             match_id = string.random_string(32)
#             match = \
#             Match.objects.get_or_create(home_team=home_team, away_team=away_team, sport=self.sport, id=match_id)[0]
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
#             match.score_closed = True
#             match.save()
#             match_score_2.save()
#             match_score_1.save()
#             matches.append(match)
#             i += 1
#         # Setup a rules object:
#         rlst1 = ParlayPayoutRuleset(name="Rule Test 1")
#         self.agent.save()
#         self.vhost.save()
#         rlst1.save()
#         rlst1.agents.set([self.agent])
#         rlst1.vhosts.set([self.vhost])
#         pprs1 = ParlayPayoutRulesetEntry.objects.get_or_create(ruleset=rlst1, parlay_legs=9, max_losses=2,juice_percentage=5,neg_limit=-6000,eap_percentage=50)[0]
#         pprs1.save()
#         pprs2 = ParlayPayoutRulesetEntry.objects.get_or_create(ruleset=rlst1, parlay_legs=9, max_losses=1,juice_percentage=5,neg_limit=-6000,eap_percentage=50)[0]
#         pprs2.save()
#         bmk = Bookmaker.objects.get_or_create(name="BMK")[0]
#         bmk.save()
#
#         # print(pprs)
#         # Now, create three parlay wagers:
#         nodes = []
#         wagers = []
#         prices_list = list(range(-200, -89)) + list(range(90, 301))
#         total_prices = len(prices_list)
#         odds_prices = []
#         winning_odds = []
#         # Root wager first:
#         mos = MatchOddsSummary(match=matches[0],bookmaker=bmk, home_team=home_team, away_team=away_team,
#                                home_price=prices_list[randint(0,total_prices-1)],
#                                away_price=prices_list[randint(0,total_prices-1)],
#                                draw_price = prices_list[randint(0, total_prices - 1)])
#         mos.save()
#
#         bet_data = {"root_wager": True, "nodes": [], "type": "straight-home-team",
#                     "points": 3, "dynamic": True,"hierarchy":str(mos.uuid)}
#         odds_prices.append(mos.home_price)
#         winning_odds.append(mos.home_price)
#         home_team = Team.objects.get(key="76ers", name="76ers")
#         root_wager = Wager(account=self.account, team_1=home_team, type="PA", risk=1,
#                            win=0,match=matches[0], bet_data=bet_data, parlay_ruleset=rlst1)
#         root_wager.save()
#         # Now, eight more legs:
#         for i in range(1,9):
#             mos = MatchOddsSummary(match=matches[i], bookmaker=bmk, home_team=home_team, away_team=away_team,
#                                    home_price=prices_list[randint(0, total_prices - 1)],
#                                    away_price=prices_list[randint(0, total_prices - 1)],
#                                    draw_price=prices_list[randint(0, total_prices - 1)])
#             mos.save()
#             if (matches[i].winner == matches[i].home_team):
#                 if i%4 != 0:
#                     # Home Wins
#                     team = matches[i].home_team
#                     type = "straight-home-team"
#                     odds_prices.append(mos.home_price)
#                     winning_odds.append(mos.home_price)
#                 else:
#                     # Away Wins (LOOSES)
#                     team = matches[i].away_team
#                     type = "straight-away-team"
#                     odds_prices.append(mos.away_price)
#             else:
#                 if i%4 == 0:
#                     # Home Looses (LOOSES):
#                     team = matches[i].home_team
#                     type = "straight-home-team"
#                     odds_prices.append(mos.home_price)
#
#                 else:
#                     # Away Wins:
#                     team = matches[i].away_team
#                     type = "straight-away-team"
#                     odds_prices.append(mos.away_price)
#                     winning_odds.append(mos.away_price)
#             bet_data = {"parent": str(root_wager.uuid),"type": type,
#                         "dynamic": True,"hierarchy":str(mos.uuid)}
#             wager = Wager(account=self.account, team_1=team, type="PA",
#                           match=matches[i], bet_data=bet_data, parlay_ruleset=rlst1)
#             wager.save()
#             wagers.append(wager)
#             nodes.append(str(wager.uuid))
#
#         # Save root nodes:
#         root_wager.bet_data["nodes"] = nodes
#         # Calculate final winnings:
#         root_wager.win = parlay_decimal_odds(odds_prices)
#
#         # Now, save everything and assert correct creation:
#         root_wager.save()
#         # Links and relations:
#         self.assertEqual(root_wager.bet_data["nodes"], nodes)
#         for wager in wagers:
#             self.assertEqual(wager.bet_data["parent"], str(root_wager.uuid))
#
#
#         # Setup complete
#         # Win all:
#         root_wager.match.finished = True
#         root_wager.match.scores_closed = True
#         root_wager.save()
#         # print(odds_prices)
#         # print(winning_odds)
#         # print(parlay_decimal_odds(odds_prices))
#         self.assertTrue(qualifier._qual_parlay_bet_dynamic(root_wager))
#         self.assertLess(float(root_wager.win),float(root_wager.qualifier_history["original_win"]))