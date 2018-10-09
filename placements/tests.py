"""Unit tests for Placements."""
from django.conf import settings
from rest_framework.test import APITestCase
from placements.models import BlogEntry
from login.tests import get_new_user

def test_blog(obj, url, count):
    """Helper for testing authenticated blog endpoints."""
    # Try without authentication
    response = obj.client.get(url)
    obj.assertEqual(response.status_code, 401)

    # Try after authentication
    user = get_new_user()
    obj.client.force_authenticate(user)  # pylint: disable=E1101
    response = obj.client.get(url)
    obj.assertEqual(response.status_code, 200)
    obj.assertEqual(len(response.data), count)

class PlacementsTestCase(APITestCase):
    """Test placements endpoints."""

    def setUp(self):
        # Create dummies
        self.entry1 = BlogEntry.objects.create(title="PEntry1", blog_url=settings.PLACEMENTS_URL)
        BlogEntry.objects.create(title="PEntry2", blog_url=settings.PLACEMENTS_URL)
        BlogEntry.objects.create(title="TEntry1", blog_url=settings.TRAINING_BLOG_URL)
        BlogEntry.objects.create(title="TEntry2", blog_url=settings.TRAINING_BLOG_URL)
        BlogEntry.objects.create(title="TEntry3", blog_url=settings.TRAINING_BLOG_URL)

    def test_placement_other(self):
        """Check misc parameters of Placement."""
        self.assertEqual(str(self.entry1), self.entry1.title)

    def test_placement_get(self):
        """Check auth before getting placements."""
        test_blog(self, '/api/placement-blog', 2)

    def test_training_get(self):
        """Check auth before getting training blog."""
        test_blog(self, '/api/training-blog', 3)
