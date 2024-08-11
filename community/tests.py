"""Unit tests for Events."""
from django.test import TransactionTestCase
from rest_framework.test import APIClient
from community.models import Community, CommunityPost
from roles.models import BodyRole
from login.tests import get_new_user
from helpers.test_helpers import create_body
from helpers.test_helpers import create_community
from helpers.test_helpers import create_communitypost

# pylint: disable=R0902


class CommunityTestCase(TransactionTestCase):
    """Check if we can create communities and link communityposts."""

    def setUp(self):
        # Fake authenticate
        self.user1 = get_new_user()
        self.client1 = APIClient()
        self.client1.force_authenticate(self.user1)

        self.user2 = get_new_user()
        self.client2 = APIClient()
        self.client2.force_authenticate(self.user2)

        self.test_body_1 = create_body()
        self.test_body_2 = create_body()

        self.body_1_role = BodyRole.objects.create(
            name="Body1Role", body=self.test_body_1, permissions="AppP,ModC"
        )
        self.user1.profile.roles.add(self.body_1_role)

        self.test_community_1 = create_community(body=self.test_body_1)
        self.test_community_2 = create_community(body=self.test_body_2)

        self.test_communitypost_11 = create_communitypost(
            community=self.test_community_1, posted_by=self.user1.profile, status=1
        )
        self.test_communitypost_12 = create_communitypost(
            community=self.test_community_1, posted_by=self.user2.profile, status=1
        )

        self.test_communitypost_21 = create_communitypost(
            community=self.test_community_2, posted_by=self.user1.profile, status=1
        )

    def test_community_list(self):
        """Test if communities can be listed."""
        url = "/api/communities"
        response = self.client1.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.data), 0)

    def test_community_get(self):
        """Test getting the community with id or str_id."""
        community = Community.objects.create(
            name="Test #Community 123!", body=create_body()
        )

        url = "/api/communities/" + str(community.id)
        response = self.client1.get(url, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], community.name)

        url = "/api/communities/test-community-123-" + str(community.id)[:8]
        response = self.client1.get(url, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], community.name)

    def test_communitypost_alllist(self):
        """Test if communityposts can be listed."""
        url = "/api/communityposts?status=1&community=" + str(self.test_community_1.id)
        response = self.client1.get(url, format="json")
        data = response.data["data"]
        self.assertEqual(response.status_code, 200)
        self.assertGreater(response.data["count"], 0)
        self.assertListEqual(
            list(map(lambda x: (x["status"], x["deleted"], x["thread_rank"]), data)),
            [(1, False, 1)] * response.data["count"],
        )

    def test_communitypost_yourlist(self):
        url = "/api/communityposts?community=" + str(self.test_community_1.id)
        response = self.client1.get(url, format="json")
        data = response.data["data"]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data["count"],
            CommunityPost.objects.filter(
                thread_rank=1,
                posted_by=self.user1.profile,
                community=self.test_community_1,
            ).count(),
        )
        self.assertListEqual(
            list(map(lambda x: x["posted_by"]["name"], data)),
            [self.user1.profile.name] * response.data["count"],
        )

    def test_communitypost_pendinglist(self):
        url = "/api/communityposts?status=0&community=" + str(self.test_community_1.id)
        response = self.client1.get(url, format="json")
        data = response.data["data"]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data["count"],
            CommunityPost.objects.filter(thread_rank=1, status=0).count(),
        )
        self.assertListEqual(
            list(map(lambda x: (x["status"], x["thread_rank"], x["deleted"]), data)),
            [(0, 1, False)] * response.data["count"],
        )

    def test_communitypost_reportedlist(self):
        pass

    def test_communitypost_create(self):
        """Test if communityposts can be created."""
        url = "/api/communityposts"
        data = {
            "content": "Test content 1",
            "community": {
                "id": self.test_community_1.id,
            },
        }
        response = self.client1.post(url, data, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["posted_by"]["name"], self.user1.profile.name)

        url = "/api/communityposts"
        data = {
            "content": "Test content 2",
            "community": {
                "id": self.test_community_1.id,
            },
        }
        response = self.client2.post(url, data, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["posted_by"]["name"], self.user2.profile.name)

    def test_communitypost_get(self):
        """Test getting the community with id or str_id."""
        communitypost = CommunityPost.objects.create(
            content="Test #CommunityPost 123!",
            community=self.test_community_1,
            posted_by=self.user1.profile,
        )

        url = "/api/communityposts/" + str(communitypost.id)
        response = self.client1.get(url, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["content"], communitypost.content)

        url = "/api/communityposts/" + str(communitypost.str_id)
        response = self.client1.get(url, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["content"], communitypost.content)

    def test_communitypost_edit(self):
        url = "/api/communityposts/" + str(self.test_communitypost_11.id)
        data = {
            "content": "Test content 1 edited",
        }
        response = self.client2.put(url, data, format="json")
        self.assertEqual(response.status_code, 403)

        url = "/api/communityposts/" + str(self.test_communitypost_11.id)
        data = {
            "content": "Test content 1 edited",
        }
        response = self.client1.put(url, data, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["content"], data["content"])

    def test_communitypost_moderation(self):
        post1 = create_communitypost(
            community=self.test_community_1, posted_by=self.user1.profile
        )

        # Reject
        url = "/api/communityposts/moderator/" + str(post1.id)
        data = {
            "status": 2,
        }
        response = self.client2.put(url, data, format="json")
        self.assertEqual(response.status_code, 403)

        url = "/api/communityposts/moderator/" + str(post1.id)
        data = {
            "status": 2,
        }
        response = self.client1.put(url, data, format="json")
        self.assertEqual(response.status_code, 200)

        # Accept
        url = "/api/communityposts/moderator/" + str(post1.id)
        data = {
            "status": 1,
        }
        response = self.client2.put(url, data, format="json")
        self.assertEqual(response.status_code, 403)

        url = "/api/communityposts/moderator/" + str(post1.id)
        data = {
            "status": 1,
        }
        response = self.client1.put(url, data, format="json")
        self.assertEqual(response.status_code, 200)

    def test_communitypost_feature(self):
        url = "/api/communityposts/feature/" + str(self.test_communitypost_11.id)
        data = {
            "is_featured": True,
        }
        response = self.client2.put(url, data, format="json")
        self.assertEqual(response.status_code, 403)

        url = "/api/communityposts/feature/" + str(self.test_communitypost_11.id)
        data = {
            "is_featured": True,
        }
        response = self.client1.put(url, data, format="json")
        self.assertEqual(response.status_code, 200)

    def test_communitypost_delete(self):
        url = "/api/communityposts/delete/" + str(self.test_communitypost_11.id)
        response = self.client2.put(url, format="json")
        self.assertEqual(response.status_code, 403)

        url = "/api/communityposts/delete/" + str(self.test_communitypost_12.id)
        response = self.client2.put(url, format="json")
        self.assertEqual(response.status_code, 200)

        url = "/api/communityposts/delete/" + str(self.test_communitypost_12.id)
        response = self.client1.put(url, format="json")
        self.assertEqual(response.status_code, 200)

    def test_communitypost_report(self):
        url = "/api/communityposts/report/" + str(self.test_communitypost_12.id)
        response = self.client1.put(url, format="json")
        self.assertEqual(response.status_code, 200)

        url = "/api/communityposts/report/" + str(self.test_communitypost_12.id)
        response = self.client1.put(url, format="json")
        self.assertEqual(response.status_code, 200)
