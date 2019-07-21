"""Unit tests for news feed."""
import time
from subprocess import Popen

from freezegun import freeze_time
from rest_framework.test import APITestCase
from django.core.management import call_command
from news.models import NewsEntry
from news.models import UserNewsReaction
from bodies.models import Body
from login.tests import get_new_user
from helpers.fcm import get_news_image

class NewsTestCase(APITestCase):
    """Test news endpoints."""

    def setUp(self):
        # Start mock server
        self.mock_server = Popen(['python', 'news/test/test_server.py'])

        # Fake authenticate
        self.user = get_new_user()
        self.client.force_authenticate(self.user)  # pylint: disable=E1101

        # Create bodies
        self.body1 = Body.objects.create(name="Body1")
        body2 = Body.objects.create(name="Body2")

        # Create dummies
        self.entry1 = NewsEntry.objects.create(title="PEntry1", blog_url="B1URL", body=self.body1)
        NewsEntry.objects.create(title="PEntry2", blog_url="B1URL", body=self.body1)
        NewsEntry.objects.create(title="TEntry1", blog_url="B2URL", body=body2)
        NewsEntry.objects.create(title="TEntry2", blog_url="B2URL", body=body2)
        NewsEntry.objects.create(title="TEntry3", blog_url="B2URL", body=body2)

    def test_news_other(self):
        """Check misc parameters of news models."""
        self.assertEqual(str(self.entry1), self.entry1.title)

    def test_news_get(self):
        """Test news feed API."""
        # Check without query params
        url = '/api/news'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 5)

        # Check with query params
        url = '/api/news?from=1&num=2'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

        # Check for body
        url = '/api/news?body=' + str(self.body1.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

    def test_news_reaction(self):
        """Test News Reaction API."""
        # Make dummy news entry
        news = self.entry1

        # Check reacting Like
        url = '/api/user-me/unr/' + str(news.id) + '?reaction=0'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 204)
        unr = UserNewsReaction.objects.get(news__id=news.id, user=self.user.profile)
        self.assertEqual(unr.reaction, 0)

        # Check reacting Angry
        url = '/api/user-me/unr/' + str(news.id) + '?reaction=5'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 204)
        unr = UserNewsReaction.objects.get(news__id=news.id, user=self.user.profile)
        self.assertEqual(unr.reaction, 5)

        # Check /api/news reactions
        url = '/api/news'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 200)
        e1_i = next((index for (index, d) in enumerate(response.data) if d['title'] == self.entry1.title), None)
        self.assertEqual(response.data[e1_i]['reactions_count'][5], 1)
        self.assertEqual(response.data[e1_i]['user_reaction'], 5)

        # Check un-react
        url = '/api/user-me/unr/' + str(news.id) + '?reaction=-1'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 204)
        unr = UserNewsReaction.objects.get(news__id=news.id, user=self.user.profile)
        self.assertEqual(unr.reaction, -1)

        # Check /api/news after un-reacting
        url = '/api/news'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 200)
        e1_i = next((index for (index, d) in enumerate(response.data) if d['title'] == self.entry1.title), None)
        self.assertEqual(response.data[e1_i]['reactions_count'][5], 0)
        self.assertEqual(response.data[e1_i]['user_reaction'], -1)

        # Check reacting validation
        url = '/api/user-me/unr/' + str(news.id)
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 400)

    @freeze_time('2019-01-02')
    def test_news_chore(self):
        """Test the news chore."""
        # Give server time to start up
        time.sleep(1)

        # Clear notifications
        self.user.notifications.all().delete()

        # Create bodies with(out) blogs
        body0 = Body.objects.create(name='testbody0')
        body1 = Body.objects.create(name='testbody1', blog_url='http://localhost:33000/body1blog')
        body2 = Body.objects.create(name='testbody2', blog_url='http://localhost:33000/body2blog')

        # Follow all bodies
        self.user.profile.followed_bodies.add(body0, body1, body2)

        # Run the news chore
        call_command('news_chore')

        # Assert if news was fetched
        self.assertEqual(NewsEntry.objects.filter(body=body1).count(), 2)
        self.assertEqual(NewsEntry.objects.filter(body=body2).count(), 2)

        # Assert fetching fields
        entry = NewsEntry.objects.filter(body=body1)[0]
        self.assertIn("RSS 1", entry.title)
        self.assertIn("RSS 1 Item", entry.content)
        self.assertIn("https://localhost", entry.link)
        self.assertIn("sample:", entry.guid)

        # Assert notifications were created
        # RSS 2 Item 2 is more than 2 days old, so it should not count
        self.assertEqual(self.user.notifications.count(), 3)

        # Add third body
        body3 = Body.objects.create(name='testbody3', blog_url='http://localhost:33000/body3blog')
        self.user.profile.followed_bodies.add(body3)

        # Run the news chore again
        call_command('news_chore')

        # Assert old news is not recreated and new news is
        self.assertEqual(NewsEntry.objects.filter(body=body1).count(), 2)
        self.assertEqual(NewsEntry.objects.filter(body=body2).count(), 2)
        self.assertEqual(NewsEntry.objects.filter(body=body3).count(), 5)

        # Assert notifications were created
        # Body 3 has 5 articles, only 3 notifications should be created (maximum)
        self.assertEqual(self.user.notifications.count(), 6)

    def test_extra(self):
        """Extra tests for helpers of News"""
        news = self.entry1
        news.guid = 'yt:video:VIDEOID'
        self.assertEqual(get_news_image(news), 'https://img.youtube.com/vi/VIDEOID/mqdefault.jpg')

    def tearDown(self):
        # Terminate server
        self.mock_server.terminate()
