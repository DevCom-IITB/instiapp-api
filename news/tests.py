"""Unit tests for news feed."""
from rest_framework.test import APITestCase
from news.models import NewsEntry
from bodies.models import Body

class NewsTestCase(APITestCase):
    """Test news endpoints."""

    entry1 = None
    source1 = None

    def setUp(self):
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
        url = '/api/news'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 5)
