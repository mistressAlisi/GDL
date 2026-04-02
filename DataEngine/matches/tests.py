# from django.core.management import call_command
# from django.test import TestCase
#
# from matches.models import Match
# from sports.models import Group, Sport
# from teams.models import Team
#
#
# # Create your tests here.
# class MatchTests(TestCase):
#     @classmethod
#     def setUp(cls):
#         call_command('install_sql_files', '__all__')
#         cls.team_1 = Team.objects.get_or_create(key="test_team_1", name="Test Team 1")[0]
#         cls.team_2 = Team.objects.get_or_create(key="test_team_2", name="Test Team 2")[0]
#         cls.group = Group.objects.get_or_create(slug="test", icon="test_icon", name="test sport", generic_icon="test_genicon")[0]
#         cls.sport = Sport.objects.get_or_create(key="test_sport", group=cls.group, title="sport_title", wager_limit=100000)[0]
#         cls.match = Match.objects.get_or_create(sport=cls.sport,home_team=cls.team_1,away_team=cls.team_2)[0]
#
#
#     def test_match_open(self):
#         self.assertEqual(self.match.open, True)
#         self.assertEqual(self.match.active, True)
#         self.assertEqual(self.match.base_line,110)