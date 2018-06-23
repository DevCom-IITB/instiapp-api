"""Unit tests for news feed."""
from rest_framework.test import APITestCase
from news.models import NewsEntry
from news.models import UserNewsReaction
from bodies.models import Body
from login.tests import get_new_user

class NewsTestCase(APITestCase):
    """Test news endpoints."""

    def setUp(self):
        # Fake authenticate
        self.user = get_new_user()
        self.client.force_authenticate(self.user) # pylint: disable=E1101

        # Create bodies
        body1 = Body.objects.create(name="Body1")
        body2 = Body.objects.create(name="Body2")

        # Create dummies
        self.entry1 = NewsEntry.objects.create(title="PEntry1", blog_url="B1URL", body=body1)
        NewsEntry.objects.create(title="PEntry2", blog_url="B1URL", body=body1)
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


        # Check reacting validation
        url = '/api/user-me/unr/' + str(news.id)
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 400)
