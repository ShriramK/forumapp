"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from forum.models import *#UserProfile, User
import unittest

class SimpleTest(TestCase):
	def test_basic_addition(self):
		"""
		Tests that 1 + 1 always equals 2.
		"""
		self.assertEqual(1 + 1, 2)

	def setUp(self):
		f = Forum.objects.create(title="forum")
		u = User.objects.create_user("djangouser", "djangouser@djangouser.com", "pwd")
		Site.objects.create(domain="localhost:8000", name="test.org")
		t = Thread.objects.create(title="thread", creator=u, forum=f)
		p = Post.objects.create(title="post", body="body", creator=u, thread=t)


	def content_test(self, url, values):
		"""Get content of url and test that each of items in 'values' list is present."""
		r = self.c.get(url)
		self.assertEquals(r.status_code, 200)
		for v in values:
			self.assertTrue(v in r.content)

	def test(self):
		self.c = Client()
		self.c.login(username="djangouser", password="pwd")

		self.content_test("/forum/", ['<a href="/forum/1/">forum</a>'])
		self.content_test("/forum/1/", ['<a href="/thread/1/">thread</a>', "djangouser - post"])
		self.content_test("/thread/1/", ['<div class="ttitle">thread</div>', 
				'<span class="title">post</span>', 'body<br />', 'by djangouser |'])
		r = self.c.post("/new_thread/1/", {"subject": "thread2", "body": "body2"})
		r = self.c.post("/reply/2/", {"subject": "post2", "body": "body3"})
		self.content_test("/thread/2/", ['<div class="ttitle">thread2</div>', 
				'<span class="title">post2</span>', 'body2<br />', 'body3<br />'])

		'''
	# http://www.agmweb.ca/2008-01-05-using-profiles-with-django/

		usrProfileObj = UserProfile.objects.create(user_id=user.id)
		usrProfileObj.avatar = 'tmp.jpg'
		usrProfileObj.posts = 1
		usrProfileObj.save()

	def testProfile(self):
		user = User.objects.get(username="djangouser")
		assert UserProfile.objects.get(user_id=user.id).avatar == 'tmp.jpg'
		assert UserProfile.objects.get(user_id=user.id).posts == 1
		'''