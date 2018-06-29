"""Unit tests for news feed."""
from rest_framework.test import APITestCase
from django.utils import timezone

from bodies.models import Body
from events.models import Event
from users.models import UserProfile

class OtherTestCase(APITestCase):
    """Test other endpoints."""

    def setUp(self):
        # Create bodies
        Body.objects.create(name="Test Body1")
        Body.objects.create(name="Test Body2")

        Event.objects.create(name="Test Event1", start_time=timezone.now(), end_time=timezone.now())
        Event.objects.create(name="Test Event2 Body1", start_time=timezone.now(), end_time=timezone.now())
        Event.objects.create(name="Test Event21", start_time=timezone.now(), end_time=timezone.now())

        UserProfile.objects.create(name="Test User1")
        UserProfile.objects.create(name="Test User2")


    def test_search(self):
        """Test the search endpoint."""
        url = '/api/search?query='

        response = self.client.get(url + 'bo')
        self.assertEqual(response.status_code, 400)

        response = self.client.get(url + 'body1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['bodies']), 1)
        self.assertEqual(len(response.data['events']), 1)
        self.assertEqual(len(response.data['users']), 0)

        response = self.client.get(url + 'body2')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['bodies']), 1)
        self.assertEqual(len(response.data['events']), 0)
        self.assertEqual(len(response.data['users']), 0)

        response = self.client.get(url + 'test user')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['bodies']), 0)
        self.assertEqual(len(response.data['events']), 0)
        self.assertEqual(len(response.data['users']), 2)
