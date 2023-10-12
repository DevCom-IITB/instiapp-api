"""Unit tests for Placements."""
import time
from subprocess import Popen

from django.conf import settings
from django.core.management import call_command
from freezegun import freeze_time
from rest_framework.test import APITestCase
from helpers.test_helpers import create_body
from placements.models import BlogEntry
from login.tests import get_new_user


def test_blog(obj, url, count):
    """Helper for testing authenticated blog endpoints."""
    # Try without authentication
    response = obj.client.get(url)
    obj.assertEqual(response.status_code, 401)

    # Try after authentication
    user = get_new_user()
    obj.client.force_authenticate(user)  # pylint: disable=E1101
    response = obj.client.get(url)
    obj.assertEqual(response.status_code, 200)
    obj.assertEqual(len(response.data), count)


class PlacementsTestCase(APITestCase):
    """Test placements endpoints."""

    def setUp(self):
        # Start mock server
        self.mock_server = Popen(["python", "news/test/test_server.py"])

        # Create dummies
        self.entry1 = BlogEntry.objects.create(
            title="PEntry1", blog_url=settings.PLACEMENTS_URL_VAL
        )
        BlogEntry.objects.create(title="PEntry2", blog_url=settings.PLACEMENTS_URL_VAL)
        BlogEntry.objects.create(
            title="TEntry1", blog_url=settings.TRAINING_BLOG_URL_VAL
        )
        BlogEntry.objects.create(
            title="TEntry2", blog_url=settings.TRAINING_BLOG_URL_VAL
        )
        BlogEntry.objects.create(
            title="TEntry3", blog_url=settings.TRAINING_BLOG_URL_VAL
        )

    def test_placement_other(self):
        """Check misc parameters of Placement."""
        self.assertEqual(str(self.entry1), self.entry1.title)

    def test_placement_get(self):
        """Check auth before getting placements."""
        test_blog(self, "/api/placement-blog", 2)

    def test_training_get(self):
        """Check auth before getting training blog."""
        test_blog(self, "/api/training-blog", 3)

    # Adding test for pin_unpin feature

    # def test_blog_order(self):
    #     """Test ordering of the pinned blogs"""
    #     BlogEntry.objects.create(title="UnpinnedEntry2", blog_url=settings.PLACEMENTS_URL_VAL,)
    # pinnedEntry1 = BlogEntry.objects.create(title="PinnedEntry1",
    #                                         blog_url=settings.PLACEMENTS_URL_VAL, pinned=True)

    #     BlogEntry.objects.create(title="UnpinnedEntry3", blog_url=settings.PLACEMENTS_URL_VAL,)
    #     BlogEntry.objects.create(title="UnpinnedEntry4", blog_url=settings.PLACEMENTS_URL_VAL,)

    #     user = get_new_user()
    #     self.client.force_authenticate(user)  # pylint: disable=E1101

    #     url = '/api/placement-blog'
    #     response = self.client.get(url)

    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(response.data[0]['id'], str(pinnedEntry1.id))
    #     self.assertEqual(response.data[0]['pinned'], True)
    #     # to test that the latest blog appears just below the pinned one

    def test_blog_order_without_pin(self):
        """Test ordering of blog with no blog is pinned"""

        # deleting all the previously created posts
        BlogEntry.objects.all().delete()

        # creating new posts with no pinned post
        first_entry = BlogEntry.objects.create(
            title="PEntry1", blog_url=settings.PLACEMENTS_URL_VAL
        )
        BlogEntry.objects.create(title="PEntry2", blog_url=settings.PLACEMENTS_URL_VAL)
        BlogEntry.objects.create(title="PEntry3", blog_url=settings.PLACEMENTS_URL_VAL)
        BlogEntry.objects.create(title="PEntry4", blog_url=settings.PLACEMENTS_URL_VAL)
        latest_entry = BlogEntry.objects.create(
            title="PEntry5", blog_url=settings.PLACEMENTS_URL_VAL
        )

        user = get_new_user()
        self.client.force_authenticate(user)  # pylint: disable=E1101

        url = "/api/placement-blog"
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data[0]["id"], str(latest_entry.id))
        self.assertEqual(response.data[4]["id"], str(first_entry.id))

    @freeze_time("2019-01-02")
    def test_placements_chore(self):
        """Test the placement blog chore."""

        # Clear table
        BlogEntry.objects.all().delete()

        # Create blog bodies
        placement_body = create_body(name=settings.PLACEMENTS_BLOG_BODY)
        training_body = create_body(name=settings.TRAINING_BLOG_BODY)

        # Create users to follow blogs
        second_year = get_new_user()
        final_year = get_new_user()
        mentioned_user = get_new_user()
        mentioned_dual = get_new_user()
        second_year.profile.followed_bodies.add(training_body)
        final_year.profile.followed_bodies.add(placement_body)
        mentioned_user.profile.roll_no = "160010005"
        mentioned_user.profile.save()
        mentioned_dual.profile.roll_no = "150040010"
        mentioned_dual.profile.save()

        # Give mock server time
        time.sleep(1)

        # Run the placement chore
        call_command("placement_blog_chore")

        # Check if posts were collected
        def placements():
            return BlogEntry.objects.all().filter(blog_url=settings.PLACEMENTS_URL_VAL)

        def trainings():
            return BlogEntry.objects.all().filter(
                blog_url=settings.TRAINING_BLOG_URL_VAL
            )

        self.assertEqual(placements().count(), 3)
        self.assertEqual(trainings().count(), 5)
        self.assertEqual(
            set(x.guid for x in placements()),
            set("sample:p:%i" % i for i in range(1, 4)),
        )
        self.assertEqual(
            set(x.title for x in placements()),
            set("Placement Item %i" % i for i in range(1, 4)),
        )

        # Check if following blogs works
        self.assertEqual(second_year.notifications.count(), 5)
        self.assertEqual(final_year.notifications.count(), 3)

        # Check if mentioned users got a notification
        self.assertEqual(mentioned_user.notifications.count(), 1)
        self.assertEqual(
            mentioned_user.notifications.first().actor.title, "Mentioning Item"
        )
        self.assertEqual(mentioned_dual.notifications.count(), 1)
        self.assertEqual(
            mentioned_dual.notifications.first().actor.title, "Placement Item 1"
        )

        # Update placement blog URL
        call_command("placement_blog_chore")

        # Check if new placement blog posts are got
        self.assertEqual(trainings().all().count(), 5)
        self.assertEqual(placements().all().count(), 4)
        self.assertEqual(
            set(x.guid for x in placements()),
            set("sample:p:%i" % i for i in range(1, 5)),
        )
        self.assertEqual(
            set(x.title for x in placements()),
            set("Placement Item %i" % i for i in range(1, 5)),
        )

        # Check if existing ones are updated
        self.assertEqual(BlogEntry.objects.get(guid="sample:p:1").content, "Updated")

        # Check if notification counts are updated
        self.assertEqual(second_year.notifications.count(), 5)
        self.assertEqual(final_year.notifications.count(), 4)
        self.assertEqual(mentioned_user.notifications.count(), 2)
        self.assertEqual(mentioned_dual.notifications.count(), 2)

    def tearDown(self):
        # Stop server
        self.mock_server.terminate()
