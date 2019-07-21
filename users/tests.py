"""Test cases for users app."""
from datetime import timedelta
from django.core.management import call_command
from django.utils import timezone
from rest_framework.test import APITestCase
from events.models import Event
from bodies.models import Body
from users.models import UserTag
from users.models import UserTagCategory
from users.models import UserProfile
from other.models import Device
from login.tests import get_new_user

# pylint: disable=R0915

class UserTestCase(APITestCase):
    """Unit tests for users."""

    def setUp(self):
        # Fake authenticate
        self.user = get_new_user()
        self.client.force_login(self.user)
        self.test_body = Body.objects.create(name="test")

    def test_get_user(self):
        """Check the /api/users/<pk> API."""

        contact = '9876543210'
        profile = UserProfile.objects.create(
            name="TestUser", ldap_id="tu", contact_no=contact)

        # Check __str__
        self.assertEqual(str(profile), profile.name)

        # Test GET with UUID
        url = '/api/users/' + str(profile.id)
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['name'], profile.name)
        self.assertEqual(response.data['contact_no'], contact)

        # Test privacy features
        profile.show_contact_no = False
        profile.save()
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(response.data['contact_no'], contact)

        # Test GET with LDAP ID
        url = '/api/users/' + profile.ldap_id
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['name'], profile.name)

    def test_user_me(self):
        """Check the /api/user-me API."""

        # Function to get latest user from database
        usr = lambda: UserProfile.objects.get(id=self.user.profile.id)

        # Initialize
        self.user.profile.fcm_id = 'TESTINIT'

        # Check GET
        url = '/api/user-me'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['id'], str(self.user.profile.id))
        self.assertEqual(self.user.profile.fcm_id, 'TESTINIT')

        event = Event.objects.create(
            start_time=timezone.now(), end_time=timezone.now(), created_by=self.user.profile)

        # Check marking interested
        url = '/api/user-me/ues/' + str(event.id) + '?status=1'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 204)
        self.assertEqual(event.followers.all()[0], self.user.profile)
        url = '/api/user-me'
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['events_interested'][0]['id'], str(event.id))

        # Check marking going
        url = '/api/user-me/ues/' + str(event.id) + '?status=2'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 204)
        url = '/api/user-me'
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['events_going'][0]['id'], str(event.id))

        # Check marking validation
        url = '/api/user-me/ues/' + str(event.id)
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 400)

        # Check self events
        url = '/api/user-me/events'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data[0]['id'], str(event.id))

        # Set and assert ping date to past
        profile = usr()
        profile.last_ping = "1970-01-02 00:00Z"
        profile.save()
        self.assertLess(usr().last_ping.timestamp(), 300000)

        # Check updating device, profile and ping
        data = {'fcm_id': 'TEST1', 'show_contact_no': False}
        url = '/api/user-me'
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(usr().fcm_id, '')
        self.assertEqual(usr().devices.first().fcm_id, 'TEST1')
        self.assertEqual(usr().show_contact_no, False)
        self.assertGreater(usr().last_ping.timestamp(), 300000)

        # Check patch validation
        data = {'android_version': 'long' * 200}
        url = '/api/user-me'
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, 400)

        # Check patch cannot update illegally
        data = {'hostel': 'H7'}
        url = '/api/user-me'
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, 403)

        # Check updating FCM Id with the deprecated API
        url = '/api/user-me?fcm_id=TESTCHANGE'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(usr().fcm_id, '')
        self.assertEqual(usr().devices.first().fcm_id, 'TESTCHANGE')
        self.assertEqual(usr().devices.count(), 1)

        # Check deletion of multiple devices
        dev = usr().devices.first()
        Device.objects.create(session=dev.session, user=usr(), last_ping=timezone.now())
        url = '/api/user-me?fcm_id=TESTCHANGE'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(usr().devices.count(), 1)

        # Test device model
        dev.application = 'app.insti'
        self.assertEqual(str(dev), usr().name)
        self.assertTrue(dev.needs_refresh())
        dev.last_refresh = timezone.now() - timedelta(days=2)
        self.assertTrue(dev.needs_refresh())
        dev.last_refresh = timezone.now() - timedelta(hours=2)
        self.assertFalse(dev.needs_refresh())

        # Test device rich support
        data = {'title': 'arbit'}
        self.assertEqual(dev.supports_rich(), False)
        dev.app_version = '5'
        self.assertEqual(dev.supports_rich(), False)
        dev.app_version = '20'
        self.assertEqual(dev.supports_rich(), True)
        self.assertFalse('click_action' in dev.process_rich(data))
        dev.application = 'app.insti.flutter'
        self.assertEqual(dev.supports_rich(), False)
        self.assertNotEqual(dev.process_rich(data)['click_action'], None)
        dev.application = 'app.insti.ios'
        self.assertEqual(dev.supports_rich(), False)

    def test_get_noauth(self):
        """Test privacy with no auth."""
        self.client.logout()
        profile = UserProfile.objects.create(name="TestUser", email="user@user.com", contact_no="9876543210")
        url = '/api/users/' + str(profile.id)
        response = self.client.get(url, format='json')
        self.assertNotEqual(response.data['email'], profile.email)
        self.assertNotEqual(response.data['contact_no'], profile.contact_no)

    def test_notifications(self):
        """Test push notification models."""

        url = '/api/user-me/subscribe-wp'
        data = {
            "endpoint": "http://endpoint",
            "keys": {
                "p256dh": "sdfdsf",
                "auth": "TESTAUTH"
            }
        }

        # Create a new subscription
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 204)

        # Check the subscription
        wpn = self.user.profile.web_push_subscriptions.first()
        self.assertEqual(str(wpn), self.user.profile.name)
        self.assertEqual(wpn.auth, 'TESTAUTH')

        # Update subscription and check that a new one is not created
        data['keys']['auth'] = 'TESTAUTH2'
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 204)
        wpn.refresh_from_db()
        self.assertEqual(wpn.auth, 'TESTAUTH2')

    def test_tag_str(self):
        """Check __str__ methods for UserTag and UserTagCategory."""
        category = UserTagCategory.objects.create(name='Category1')
        tag = UserTag.objects.create(category=category, regex='abc', target='hostel')
        self.assertEqual(str(category), 'Category1')
        self.assertEqual(str(tag), 'hostel abc')

    def test_inactive_chore(self):
        """Test the chore for marking users inactive."""

        def refresh(objs):
            _ = [obj.refresh_from_db() for obj in objs]
            return objs

        users = [get_new_user().profile for _ in range(10)]

        # Check if nothing is affected
        call_command('mark-users-inactive')
        self.assertEqual(len([user for user in refresh(users) if user.active]), 10)

        # Mark two users inactive, one almost inactive
        users[0].last_ping = users[1].last_ping = timezone.now() - timedelta(days=370)
        users[2].last_ping = users[3].last_ping = timezone.now() - timedelta(days=360)
        _ = [user.save() for user in users]

        # Check if two are inactive now
        call_command('mark-users-inactive')
        self.assertEqual(len([user for user in refresh(users) if user.active]), 8)
