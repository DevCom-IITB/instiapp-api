from rest_framework.test import APITestCase
from rest_framework.test import APIClient
from login.tests import get_new_user
from achievements.models import Achievement
from helpers.test_helpers import create_body

class AchievementTestCae(APITestCase):
    """Check if we can create and verify achievement requests."""

    def setUp(self):
        # Fake authenticate
        self.user = get_new_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

        # A different user
        self.user_2 = get_new_user()

        # Dummy bodiews
        self.body_1 = create_body()
        self.body_2 = create_body()

    def test_get_achievement(self):
        """Test retrieve method of achievement viewset."""

        achievement_1 = Achievement.objects.create(
            description="TEST ACHIEVEMENT", body=self.body_1, user=self.user.profile)

        url = '/api/achievements/%s' % achievement_1.id
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['description'], achievement_1.description)
