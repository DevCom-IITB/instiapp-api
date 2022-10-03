"""Unit tests for Events."""
from django.utils import timezone
from django.test import TransactionTestCase
from rest_framework.test import APIClient
from community.models import Community, CommunityPost
from roles.models import BodyRole
from login.tests import get_new_user
from helpers.test_helpers import create_body
from helpers.test_helpers import create_community
from helpers.test_helpers import create_event
from helpers.test_helpers import create_usertag
from helpers.test_helpers import create_usertagcategory

# pylint: disable=R0902

class CommunityTestCase(TransactionTestCase):
    """Check if we can create communities and link communityposts."""

    def setUp(self):
        # Fake authenticate
        self.user = get_new_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

        self.test_body_1 = create_body()
        self.test_body_2 = create_body()

        self.body_1_role = BodyRole.objects.create(
            name="Body1Role", body=self.test_body_1, permissions='AppP,ModC')
        self.user.profile.roles.add(self.body_1_role)

        self.test_community_1 = create_community(body=self.test_body_1)
        self.test_community_2 = create_community(body=self.test_body_2)

    def test_community_list(self):
        """Test if communities can be listed."""
        url = '/api/events'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.data), 0)

    def test_community_get(self):
        """Test getting the community with id or str_id."""
        community = Community.objects.create(name="Test #Community 123!", body=create_body())

        url = '/api/communities/' + str(community.id)
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['name'], community.name)

        url = '/api/communities/test-community-123-' + str(community.id)[:8]
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['name'], community.name)
