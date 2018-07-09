"""Unit tests for news feed."""
from rest_framework.test import APITestCase
from django.utils import timezone

from login.tests import get_new_user
from bodies.models import Body
from events.models import Event
from events.serializers import EventSerializer
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

    def test_notifications(self):
        """Test notifications API."""
        # Fake authenticate
        user = get_new_user()
        profile = user.profile
        self.client.force_authenticate(user) # pylint: disable=E1101

        # Add two bodies, with the user following #1
        body1 = Body.objects.create(name="TestBody1")
        body2 = Body.objects.create(name="TestBody2")
        profile.followed_bodies.add(body1)

        now = timezone.now()

        # Add three events to followed body and one to other
        event1 = Event.objects.create(name="TestEvent1", start_time=now, end_time=now)
        event2 = Event.objects.create(name="TestEvent2", start_time=now, end_time=now)
        event3 = Event.objects.create(name="TestEvent3", start_time=now, end_time=now)
        event4 = Event.objects.create(name="TestEvent4", start_time=now, end_time=now)

        event1.bodies.add(body1)
        event2.bodies.add(body1)
        event3.bodies.add(body1)
        event4.bodies.add(body2)

        # Get notifications
        url = '/api/notifications'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Check if notifications are correct three
        self.assertEqual(len(response.data), 3)
        actors = [n['actor'] for n in response.data]
        self.assertIn(EventSerializer(event1).data, actors)
        self.assertIn(EventSerializer(event2).data, actors)
        self.assertIn(EventSerializer(event3).data, actors)

        # Mark event2 as read
        e2n = [n for n in response.data if n['actor'] == EventSerializer(event2).data][0]
        response = self.client.get(url + '/read/' + str(e2n['id']))
        self.assertEqual(response.status_code, 204)

        # Check if notifications are correct remaining two
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)
        actors = [n['actor'] for n in response.data]
        self.assertIn(EventSerializer(event1).data, actors)
        self.assertIn(EventSerializer(event3).data, actors)

        # Follow event 4
        uesurl = '/api/user-me/ues/' + str(event4.id) + '?status=1'
        response = self.client.get(uesurl, format='json')
        self.assertEqual(response.status_code, 204)

        # Update event 4
        event4.name = 'UpdatedEvent4'
        event4.save()

        # Check if notification is added for event 4
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 3)
        actors = [n['actor'] for n in response.data]
        self.assertIn(EventSerializer(event1).data, actors)
        self.assertIn(EventSerializer(event3).data, actors)
        self.assertIn(EventSerializer(event4).data, actors)

        # Check no notification after unfollowing event - unfollow 4 and update again
        uesurl = '/api/user-me/ues/' + str(event4.id) + '?status=0'
        response = self.client.get(uesurl, format='json')
        self.assertEqual(response.status_code, 204)
        event4.name = 'AUpdatedEvent4'
        event4.save()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 3)

        # Mark all notifications as read and check
        response = self.client.get(url + '/read')
        self.assertEqual(response.status_code, 204)

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)
