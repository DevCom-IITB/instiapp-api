from subprocess import Popen

from django.core.management import call_command
from freezegun import freeze_time
from rest_framework.test import APITestCase
from external.models import ExternalBlogEntry
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


class ExternalTestCase(APITestCase):
    """Test external blog endpoints."""

    def setUp(self):
        # Start mock server
        self.mock_server = Popen(["python", "news/test/test_server.py"])

        # Create dummies
        self.entry1 = ExternalBlogEntry.objects.create(title="PEntry1")
        ExternalBlogEntry.objects.create(title="PEntry2")
        ExternalBlogEntry.objects.create(title="TEntry1")
        ExternalBlogEntry.objects.create(title="TEntry2")
        ExternalBlogEntry.objects.create(title="TEntry3")

    def test_external_other(self):
        """Check misc parameters of External."""
        self.assertEqual(str(self.entry1), self.entry1.title + " - " + self.entry1.body)

    def test_external_get(self):
        """Check auth before getting external blogs."""
        test_blog(self, "/api/external-blog", 5)

    def test_blog_order(self):
        """Test ordering of blog with no blog is pinned"""

        # deleting all the previously created posts
        ExternalBlogEntry.objects.all().delete()

        # creating new posts with no pinned post
        first_entry = ExternalBlogEntry.objects.create(title="PEntry1")
        ExternalBlogEntry.objects.create(title="PEntry2")
        ExternalBlogEntry.objects.create(title="PEntry3")
        ExternalBlogEntry.objects.create(title="PEntry4")
        latest_entry = ExternalBlogEntry.objects.create(title="PEntry5")

        user = get_new_user()
        self.client.force_authenticate(user)  # pylint: disable=E1101

        url = "/api/external-blog"
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data[0]["id"], str(latest_entry.id))
        self.assertEqual(response.data[4]["id"], str(first_entry.id))

    @freeze_time("2019-01-02")
    def test_external_chore(self):
        """Test the external blog chore."""

        # Clear table
        ExternalBlogEntry.objects.all().delete()

        # Call the external blog command
        call_command("external_blog_chore")

        # Check if posts were collected
        externals = ExternalBlogEntry.objects.all()
        self.assertEqual(externals.count(), 5)
        self.assertEqual(
            set(x.guid for x in externals), set("sample:t:%i" % i for i in range(1, 6))
        )
        self.assertEqual(
            set(x.title for x in externals),
            set("Training Item %i" % i for i in range(1, 6)),
        )

    def tearDown(self):
        # Stop server
        self.mock_server.terminate()
