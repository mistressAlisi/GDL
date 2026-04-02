# from django.contrib.auth.models import User
# from django.test import TestCase
#
# from agent.models import Agent
#
#
# # Create your tests here.
#
# class AccountTests(TestCase):
#     @classmethod
#     def setUp(cls):
#         cls.user = User.objects.get_or_create(username="lilith")[0]
#         cls.user.save()
#         cls.agent = Agent.objects.get_or_create(user=cls.user)[0]
#         cls.agent.save()
#
#     def test_agent(self):
#         self.assertEqual(self.user,self.agent.user)
