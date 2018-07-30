"""Test cases for users app."""
from django.utils import timezone
from rest_framework.test import APITestCase
from events.models import Event
from bodies.models import Body
from users.models import UserProfile
from login.tests import get_new_user

class UserTestCase(APITestCase):
    """Unit tests for users."""

    def setUp(self):
        # Fake authenticate
        self.user = get_new_user()
        self.client.force_authenticate(self.user) # pylint: disable=E1101
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

        self.user.profile.fcm_id = 'TESTINIT'

        # Check GET
        url = '/api/user-me'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['id'], str(self.user.profile.id))
        self.assertEqual(self.user.profile.fcm_id, 'TESTINIT')

        # Check PATCH
        url = '/api/user-me'
        data = {
            "followed_bodies_id": [str(self.test_body.id)]
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.user.profile.followed_bodies.all()[0], self.test_body)

        # Check validation
        data = {
            "followed_bodies_id": [str(self.test_body.id), "my-invalid-uid"]
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.data)

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

        # Check updating FCM Id
        url = '/api/user-me?fcm_id=TESTCHANGE'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(UserProfile.objects.get(id=self.user.profile.id).fcm_id, 'TESTCHANGE')

    def test_get_noauth(self):
        """Test privacy with no auth."""
        self.client.logout()
        profile = UserProfile.objects.create(name="TestUser", email="user@user.com")
        url = '/api/users/' + str(profile.id)
        response = self.client.get(url, format='json')
        self.assertNotEqual(response.data['email'], profile.email)

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
