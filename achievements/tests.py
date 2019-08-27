import pyotp
from rest_framework.test import APITestCase
from rest_framework.test import APIClient
from login.tests import get_new_user
from achievements.models import Achievement
from achievements.models import OfferedAchievement
from helpers.test_helpers import create_body
from helpers.test_helpers import create_event
from roles.models import BodyRole

class AchievementTestCase(APITestCase):
    """Check if we can create and verify achievement requests."""

    def setUp(self):
        # Fake authenticate
        self.user = get_new_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

        # A different user
        self.user_2 = get_new_user()

        # Dummy bodies and events
        self.body_1 = create_body()
        self.body_2 = create_body()
        self.event_1 = create_event()

        # Body roles
        self.body_1_role = BodyRole.objects.create(
            name="Body1Role", body=self.body_1, permissions='VerA,AddE')

    def test_get_achievement(self):
        """Test retrieve method of achievement viewset."""

        achievement_1 = Achievement.objects.create(
            description="Test Achievement", body=self.body_1, user=self.user.profile)

        url = '/api/achievements/%s' % achievement_1.id
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['description'], achievement_1.description)

    def test_list_achievement(self):
        """Test listing method of achievement viewset."""

        # Create objects, one verified
        Achievement.objects.create(
            description="Test Achievement 1", body=self.body_1, user=self.user.profile)
        Achievement.objects.create(
            description="Test Achievement 2", body=self.body_1, user=self.user.profile, verified=True)
        Achievement.objects.create(
            description="Hidden Achievement", body=self.body_1, user=self.user.profile,
            verified=True, dismissed=True, hidden=True)
        Achievement.objects.create(
            description="Different User Ach 3", body=self.body_1, user=self.user_2.profile)
        Achievement.objects.create(
            description="Different User Body 4", body=self.body_2, user=self.user_2.profile)

        # Test listing endpoint
        url = '/api/achievements'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 3)

        # Test user me list (only verified and not hidden)
        url = '/api/user-me'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['achievements']), 1)

        # Test body list (without role)
        url = '/api/achievements-body/%s' % self.body_1.id
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

        # Test body list (with role)
        self.user.profile.roles.add(self.body_1_role)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 3)
        self.user.profile.roles.remove(self.body_1_role)

    def test_achievement_patch(self):
        """Test patching (hiding) achievements."""

        achievement_1 = Achievement.objects.create(
            description="Test Achievement", body=self.body_1, user=self.user.profile, hidden=False)
        achievement_2 = Achievement.objects.create(
            description="Test Achievement", body=self.body_1, user=self.user_2.profile)

        # Try to patch someone else's achievement
        data = {'hidden': True}
        url = '/api/achievements/%s' % achievement_2.id
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, 403)

        # Try to patch own achievement
        url = '/api/achievements/%s' % achievement_1.id
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, 204)
        achievement_1.refresh_from_db()
        self.assertEqual(achievement_1.hidden, True)

    def test_achievement_flow(self):
        """Test creation and verification flow of achievements."""

        # Try creating request without body
        data = {
            'title': 'My Big Achievement',
            'image_url': 'http://example.com/image2.png',
            'verified': True,
            'dismissed': True,
        }
        url = '/api/achievements'
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 403)

        # Create (malicious) request from user
        data['body'] = str(self.body_1.id)
        data['event'] = str(self.event_1.id)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['verified'], False)
        self.assertEqual(response.data['dismissed'], False)
        self.assertEqual(response.data['event_detail']['name'], self.event_1.name)

        # Get achievement id for further use
        achievement_id = response.data['id']

        # Try to verify without privileges
        url = '/api/achievements/%s' % achievement_id
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, 403)

        # Acquire privileges
        self.user.profile.roles.add(self.body_1_role)

        # Try to verify after changing body ID (with privilege)
        data['body'] = str(self.body_2.id)
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, 400)

        # Try to verify correctly
        data['body'] = str(self.body_1.id)
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, 200)

        # Invoke delete API
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)

        # Lose privileges
        self.user.profile.roles.remove(self.body_1_role)

        # Try deleting a new one
        achievement_1 = Achievement.objects.create(
            description="Test Achievement", body=self.body_1, user=self.user.profile)
        url = '/api/achievements/%s' % achievement_1.id
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 403)

    def test_achievement_offer(self):
        """Test offered achivements."""

        # Setup data
        data = {
            'title': 'My Big Achievement',
            'priority': 1,
            'body': str(self.body_1.id),
            'event': str(self.event_1.id),
        }
        url = '/api/achievements-offer'

        # Try create without privileges
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 403)

        # Acquire privileges and try
        self.user.profile.roles.add(self.body_1_role)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 201)
        self.user.profile.roles.remove(self.body_1_role)

        # Create two achievements, one hidden
        offer_id = response.data['id']
        a1 = Achievement.objects.create(
            title="Test", body=self.body_1,
            user=self.user.profile, offer_id=offer_id)
        Achievement.objects.create(
            title="Test", body=self.body_1, verified=True,
            user=self.user_2.profile, offer_id=offer_id, hidden=True)

        # Try update without privileges
        url = '/api/achievements-offer/%s' % offer_id
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, 403)

        # Test if no users are present without verification
        response = self.client.get(url, data, format='json')
        self.assertEqual(len(response.data['users']), 0)

        # Verify both achievements
        a1.verified = True
        a1.save()

        # Try getting secret without privileges
        # Check if only one user is present
        response = self.client.get(url, data, format='json')
        self.assertNotIn('secret', response.data)
        self.assertEqual(len(response.data['users']), 1)

        # Acquire privileges and try
        self.user.profile.roles.add(self.body_1_role)
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, 200)

        # Try getting secret
        # Assert both users are present
        response = self.client.get(url, data, format='json')
        self.assertIn('secret', response.data)
        self.assertEqual(len(response.data['users']), 2)
        self.user.profile.roles.remove(self.body_1_role)

        # Try delete without privileges
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 403)

        # Acquire privileges and try
        self.user.profile.roles.add(self.body_1_role)
        response = self.client.delete(url, data, format='json')
        self.assertEqual(response.status_code, 204)
        self.user.profile.roles.remove(self.body_1_role)

    def test_totp_claim(self):
        offer_1 = OfferedAchievement.objects.create(
            title="Test Achievement", body=self.body_1, event=self.event_1)
        offer_2 = OfferedAchievement.objects.create(
            title="Test Achievement", body=self.body_1, event=self.event_1)

        # Setup data
        data = {
            'secret': 'something'
        }
        url = '/api/achievements-offer/%s' % offer_1.id

        # Try with invalid secret
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 403)

        # Try with master secret
        data['secret'] = offer_1.secret
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 201)

        # Try to get again master secret
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 200)

        # Try with TOTP for offer 2
        url = '/api/achievements-offer/%s' % offer_2.id
        data['secret'] = pyotp.TOTP(offer_2.secret).now()
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 201)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 200)
