# from django.core.management import call_command
# from django.test import TestCase
#
# # Create your tests here.
# from .models import Group, Sport, SportsGroupView
#
#
# class TeamTests(TestCase):
#     @classmethod
#     def setUp(cls):
#         call_command('install_sql_files', 'sports')
#         cls.group = Group.objects.get_or_create(slug="test",icon="test_icon",name="test sport",generic_icon="test_genicon")[0]
#         cls.sport = Sport.objects.get_or_create(key="test_sport",group=cls.group,title="sport_title",wager_limit=100000)[0]
#         cls.sport.save()
#         cls.group.save()
#
#
#     def test_groups(self):
#         self.assertEqual(self.group.slug,"test")
#         self.assertEqual(self.group.active,True)
#
#     def test_sport(self):
#         self.assertEqual(self.sport.key,"test_sport")
#         self.assertIs(self.sport.group,self.group)
#         self.assertEqual(self.sport.title,"sport_title")
#
#     def test_view(self):
#         sport_view = SportsGroupView.objects.get(group_slug=self.group.slug)
#         self.assertEqual(sport_view.sport_key,self.sport.key)
#         self.assertEqual(sport_view.group_slug,self.group.slug)
#         self.assertEqual(sport_view.sport_title,self.sport.title)
#         self.assertEqual(sport_view.group_icon,self.group.icon)
