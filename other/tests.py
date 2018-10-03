"""Unit tests for news feed."""
from datetime import timedelta
import xml.etree.ElementTree as ET
from freezegun import freeze_time

from rest_framework.test import APITestCase
from django.utils import timezone
from notifications.signals import notify

from login.tests import get_new_user
from bodies.models import Body
from events.models import Event
from events.serializers import EventSerializer
from users.models import UserProfile
from news.models import NewsEntry
from placements.models import BlogEntry

from helpers.test_helpers import create_usertag
from helpers.test_helpers import create_usertagcategory

class OtherTestCase(APITestCase):
    """Test other endpoints."""

    def setUp(self):
        # Create bodies
        body1 = Body.objects.create(name="Test Body1")
        body2 = Body.objects.create(name="Test Body2")

        # Create dummy events
        event1 = Event.objects.create(name="Test Event1", start_time=timezone.now(), end_time=timezone.now())
        event2 = Event.objects.create(name="Test Event2 Body1", start_time=timezone.now(), end_time=timezone.now())
        event3 = Event.objects.create(name="Test Event21", start_time=timezone.now(), end_time=timezone.now())

        # Create dummy users for search
        UserProfile.objects.create(name="Test User1")
        UserProfile.objects.create(name="Test User2")

        # Associate events with bodies
        event1.bodies.add(body1)
        event2.bodies.add(body1)
        event3.bodies.add(body2)

        # Fake authenticate
        self.user = get_new_user()
        self.profile = self.user.profile
        self.client.force_authenticate(self.user) # pylint: disable=E1101


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
        profile = self.profile

        # Add two bodies, with the user following #1
        body1 = Body.objects.create(name="TestBody1")
        body2 = Body.objects.create(name="TestBody2")
        profile.followed_bodies.add(body1)

        now = timezone.now()

        # Add four events to followed body and one to other.
        # Event 5 has notifications turned off
        event1 = Event.objects.create(name="TestEvent1", start_time=now, end_time=now)
        event2 = Event.objects.create(name="TestEvent2", start_time=now, end_time=now)
        event3 = Event.objects.create(name="TestEvent3", start_time=now, end_time=now)
        event4 = Event.objects.create(name="TestEvent4", start_time=now, end_time=now)
        event5 = Event.objects.create(name="TestEvent5", start_time=now, end_time=now, notify=False)

        # Notifications older than a week shouldn't show up
        with freeze_time(timezone.now() - timedelta(days=10)):
            event6 = Event.objects.create(name="TestEvent6", start_time=now, end_time=now)
            event6.bodies.add(body1)

        # Add bodies to all events
        event1.bodies.add(body1)
        event2.bodies.add(body1)
        event3.bodies.add(body1)
        event4.bodies.add(body2)
        event5.bodies.add(body1)

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

        # Follow event 5
        uesurl = '/api/user-me/ues/' + str(event5.id) + '?status=1'
        response = self.client.get(uesurl, format='json')
        self.assertEqual(response.status_code, 204)

        # Update event 5
        event5.name = 'UpdatedEvent5'
        event5.save()

        # Check no notification is added for event 5
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 3)

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

    def test_news_notifications(self):
        """Test news notifications."""

        # Add two bodies, with the user following #1
        body1 = Body.objects.create(name="TestBody1", blog_url="http://body.com")
        body2 = Body.objects.create(name="TestBody2", blog_url="http://body2.com")
        self.profile.followed_bodies.add(body1)

        # Add one news for each
        ne1 = NewsEntry.objects.create(
            body=body1, title="NewsEntry1", blog_url=body1.blog_url, published=timezone.now())
        NewsEntry.objects.create(
            body=body2, title="NewsEntry2", blog_url=body2.blog_url, published=timezone.now())

        # Get notifications
        url = '/api/notifications'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['actor']['title'], ne1.title)

    def test_pt_notifications(self):
        """Test notifications for placement blog (Incomplete - only serializer)"""
        # Create dummy
        entry = BlogEntry.objects.create(
            title="BlogEntry1", blog_url='https://test.com', published=timezone.now())

        # Notify
        notify.send(entry, recipient=self.user, verb="TEST")

        # Get notifications
        url = '/api/notifications'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['actor']['title'], entry.title)

    def test_sitemap(self):
        """Test dynamic sitemap."""

        # Get the sitemap
        url = '/sitemap.xml'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Render the sitemap
        urlset = ET.fromstring(response.rendered_content)

        # Test each URL in the sitemap
        for urlobj in urlset:
            for loc in [l for l in urlobj if 'loc' in l.tag]:
                response = self.client.get(loc.text)
                self.assertEqual(response.status_code, 200)

    def test_get_user_tags(self):
        """Test getting list of tags."""

        cat1 = create_usertagcategory()
        cat2 = create_usertagcategory()

        create_usertag(cat1, '1')
        create_usertag(cat1, '2')
        create_usertag(cat2, 'ME', target='department')

        url = '/api/user-tags'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(len(response.data[0]['tags']), 2)
