"""Test cases for users app."""
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

        profile = UserProfile.objects.create(name="TestUser", ldap_id="tu")

        # Check __str__
        self.assertEqual(str(profile), profile.name)

        # Test GET with UUID
        url = '/api/users/' + str(profile.id)
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['name'], profile.name)

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

        # Check updating device
        data = {'fcm_id': 'TEST1'}
        url = '/api/user-me'
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(usr().fcm_id, '')
        self.assertEqual(usr().devices.first().fcm_id, 'TEST1')

        # Check patch validation
        data = {'android_version': 'long' * 200}
        url = '/api/user-me'
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, 400)

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
        self.assertEqual(dev.supports_rich(), True)

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
                "auth": "skjfhlsjkf"
            }
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 204)

        wpn = self.user.profile.web_push_subscriptions.all()[0]
        self.assertEqual(str(wpn), self.user.profile.name)

    def test_tag_str(self):
        """Check __str__ methods for UserTag and UserTagCategory."""
        category = UserTagCategory.objects.create(name='Category1')
        tag = UserTag.objects.create(category=category, regex='abc', target='hostel')
        self.assertEqual(str(category), 'Category1')
        self.assertEqual(str(tag), 'hostel abc')
