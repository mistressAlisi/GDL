# from django.test import TestCase
#
# # Create your tests here.
# from .models import Team
#
#
# class TeamTests(TestCase):
#     @classmethod
#     def setUp(cls):
#         cls.team_1 = Team.objects.get_or_create(key="test_team_1", name="Test Team 1")[0]
#         cls.team_2 = Team.objects.get_or_create(key="test_team_2", name="Test Team 2")[0]
#
#     def test_team_1(self):
#         self.assertEqual(self.team_1.key, "test_team_1")
#         self.assertEqual(self.team_1.total_games,0)
#         self.assertEqual(self.team_1.total_wins,0)
#         self.assertEqual(self.team_1.total_losses,0)
#         self.assertEqual(self.team_1.total_draws,0)
#
#     def test_team_2(self):
#         self.assertEqual(self.team_2.key, "test_team_2")
#         self.assertEqual(self.team_2.total_games, 0)
#         self.assertEqual(self.team_2.total_wins, 0)
#         self.assertEqual(self.team_2.total_losses, 0)
#         self.assertEqual(self.team_2.total_draws, 0)