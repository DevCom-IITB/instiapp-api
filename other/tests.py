"""Unit tests for news feed."""
import time
import json

import xml.etree.ElementTree as ET

from rest_framework.test import APIClient
from django.conf import settings
from django.core.management import call_command
from django.test import TransactionTestCase
from django.utils import timezone
from notifications.signals import notify
from notifications.models import Notification

from login.tests import get_new_user
from bodies.models import Body
from events.serializers import EventSerializer
from users.models import UserProfile
from news.models import NewsEntry
from placements.models import BlogEntry
from venter.models import Complaint

from helpers.test_helpers import create_usertag
from helpers.test_helpers import create_usertagcategory
from helpers.test_helpers import create_event
from helpers.test_helpers import create_body

def celery_delay(delay=2):
    """Wait for Celery."""
    if not settings.NO_CELERY:
        time.sleep(delay)

class OtherTestCase(TransactionTestCase):
    """Test other endpoints."""

    def setUp(self):
        # Create bodies
        body1 = create_body(
            name="Test WnCC", description="<script> var js = 'XSS'; </script>")
        body2 = create_body(name="Test MoodI")

        # Create dummy events
        event1 = create_event(name="Test Scratch")
        event2 = create_event(name="Test Scratch Wncc")
        event3 = create_event(name="Test Aaveg")

        # Create dummy users for search
        UserProfile.objects.create(name="Test User1")
        UserProfile.objects.create(name="Test User2")
        UserProfile.objects.create(name="Test User3", active=False)

        # Associate events with bodies
        event1.bodies.add(body1)
        event2.bodies.add(body1)
        event3.bodies.add(body2)

        # Fake authenticate
        self.user = get_new_user()
        self.profile = self.user.profile
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_search(self):
        """Test the search endpoint."""
        url = '/api/search?query='

        # Consolidate
        call_command('reconstruct-search')

        response = self.client.get(url + 'bo')
        self.assertEqual(response.status_code, 400)

        def assert_len(response, bodies, events, users):
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.data['bodies']), bodies)
            self.assertEqual(len(response.data['events']), events)
            self.assertEqual(len(response.data['users']), users)

        response = self.client.get(url + 'wncc')
        assert_len(response, 1, 1, 0)

        response = self.client.get(url + 'moodi')
        assert_len(response, 1, 0, 0)

        response = self.client.get(url + 'moo')
        assert_len(response, 1, 0, 0)

        response = self.client.get(url + 'test user')
        assert_len(response, 0, 0, 2)

        # Test partial fields
        response = self.client.get(url + 'wncc&types=bodies')
        assert_len(response, 1, 0, 0)

        # Test sanitization with sonic
        if settings.USE_SONIC:
            response = self.client.get(url + 'script')
            assert_len(response, 0, 0, 0)

    def test_search_misc(self):
        """Try to index an invalid object."""

        if not settings.USE_SONIC:  # pragma: no cover
            return

        from other.asyncio_run import run_sync
        from other.search import push, index_pair, run_query_sync, push_obj_sync

        # Test invalid sync doesn't panic
        run_sync(push((None, None)))
        self.assertEqual(True, True)

        # Test indexing of PT blog
        ent = BlogEntry(title='strategy comp', blog_url=settings.PLACEMENTS_URL)
        self.assertEqual(index_pair(ent)[0], 'placement')
        ent = BlogEntry(title='ecomm comp', blog_url=settings.TRAINING_BLOG_URL)
        self.assertEqual(index_pair(ent)[0], 'training')
        ent = BlogEntry(title='why this', blog_url='https://google.com')
        self.assertEqual(index_pair(ent)[0], 'blogs')

        # Test indexing of news
        ent = NewsEntry(id='bigid', title='insightiitb', blog_url='https://google.com')
        self.assertEqual(index_pair(ent)[0], 'news')
        push_obj_sync(ent)
        self.assertIn('bigid', run_query_sync('news', 'insightiitb'))

    def test_notifications(self):  # pylint: disable=R0914,R0915
        """Test notifications API."""
        # Fake authenticate
        profile = self.profile
        profile.user.notifications.all().delete()

        # Add two bodies, with the user following #1
        body1 = create_body()
        body2 = create_body()
        profile.followed_bodies.add(body1)

        # Add four events to followed body and one to other.
        # Event 5 has notifications turned off
        event1 = create_event()
        event2 = create_event()
        event3 = create_event()
        event4 = create_event()
        event5 = create_event()
        event5.notify = False
        event5.save()

        # Add bodies to all events
        event1.bodies.add(body1)
        event2.bodies.add(body1)
        event3.bodies.add(body1)
        event4.bodies.add(body2)
        event5.bodies.add(body1)

        celery_delay()

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
        e2notif = lambda: Notification.objects.get(pk=e2n['id'])
        self.assertEqual(e2notif().unread, True)
        self.assertEqual(e2notif().deleted, False)
        response = self.client.get(url + '/read/' + str(e2n['id']))
        self.assertEqual(response.status_code, 204)
        self.assertEqual(e2notif().unread, False)
        self.assertEqual(e2notif().deleted, False)

        # Mark event2 as deleted
        response = self.client.get(url + '/read/' + str(e2n['id']) + '?delete=1')
        self.assertEqual(response.status_code, 204)
        self.assertEqual(e2notif().unread, False)
        self.assertEqual(e2notif().deleted, True)

        celery_delay()

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

        celery_delay()

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

        celery_delay()
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

        # Test that notifications are not created if notify=False
        NewsEntry.objects.create(
            body=body1, title="NewsEntry3", blog_url=body1.blog_url,
            published=timezone.now(), notify=False)

        # Get notifications
        url = '/api/notifications'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['actor']['title'], ne1.title)

    def test_comment_notifications(self):
        """Test notifications for complaint subscribers when comments are made"""
        # Creating dummy complaint with one subscriber (the creator)
        test_creator = get_new_user()
        complaint = Complaint.objects.create(created_by=test_creator.profile)
        complaint.subscriptions.add(test_creator.profile)

        # Comments url
        url = '/api/venter/complaints/' + str(complaint.id) + '/comments'

        # First comment on the new complaint, should generate 1 new notification (Total = 1)
        test_commenter_1 = get_new_user()
        self.client.force_authenticate(user=test_commenter_1)

        data = {'text': 'test'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 201)

        # Get notifications for test_creator.
        # There should be one notification from the first comment made by test_commenter_1
        url = '/api/notifications'
        self.client.force_authenticate(user=test_creator)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['actor']['commented_by']['id'], str(test_commenter_1.profile.id))

        # Comment url
        url = '/api/venter/complaints/' + str(complaint.id) + '/comments'

        # Second comment on the complaint, should generate 2 new notifications.
        # One new notification each will be made for test_creator and test_commenter_1.
        # Both will be tested independently.
        test_commenter_2 = get_new_user()
        self.client.force_authenticate(user=test_commenter_2)

        data = {'text': 'test'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 201)

        # Get notifications for test_creator.
        # A total of two notifications should exist, one for each comment.
        # The most recent notification should be by the person who made the corresponding comment
        url = '/api/notifications'
        self.client.force_authenticate(user=test_creator)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['actor']['commented_by']['id'], str(test_commenter_2.profile.id))

        # Get notifications for test_commenter_1.
        # 1 notification should exist due to the comment made by test_commenter_2
        url = '/api/notifications'
        self.client.force_authenticate(user=test_commenter_1)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['actor']['commented_by']['id'], str(test_commenter_2.profile.id))

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

        # Create test users for matching
        profiles = [get_new_user().profile for x in range(6)]
        for profile in profiles:
            profile.department = 'ME'
        profiles[0].hostel = '1'
        profiles[1].hostel = ''
        profiles[1].roll_no = '2'
        profiles[2].hostel = '3'
        profiles[3].hostel = '1'
        profiles[3].department = 'EP'
        profiles[4].hostel = '2'
        profiles[4].roll_no = '2'
        profiles[5].hostel = '1'
        profiles[5].active = False
        for profile in profiles:
            profile.save()

        # Create tags in 2 categories
        t1 = create_usertag(cat1, '1')
        t2 = create_usertag(cat1, '1', target='hostel', secondary_target='roll_no', secondary_regex='2')
        t3 = create_usertag(cat2, 'ME', target='department')

        url = '/api/user-tags'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(len(response.data[0]['tags']), 2)

        url = '/api/user-tags/reach'
        response = self.client.post(url, json.dumps([]), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(response.data['count'], 4)

        data = [t1.id, t2.id, t3.id]
        response = self.client.post(url, json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 2)
