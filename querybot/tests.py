"""Unit tests for QueryBot."""
from rest_framework.test import APITestCase
from rest_framework.test import APIClient
from querybot.admin import handle_entry, make_resolved
from querybot.models import Query, UnresolvedQuery
from querybot.management.commands.query_bot_chore import handle_entry_fromsheet
from login.tests import get_new_user


class QueryTestCase(APITestCase):
    """Check querbot endpoints."""

    def setUp(self):
        # Fake authenticate
        self.user = get_new_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

        # Dummy Queries
        rows = [
            [0, "test", "test", "cat1 ", "", ""],
            [1, "test", "test", "cat2", "", ""],
        ]

        for row in rows:
            handle_entry_fromsheet(row)

        # Dummy Unresolved queries
        self.new_user = get_new_user()
        entry_1 = UnresolvedQuery.objects.create(
            question="test", category="cat1", user=self.new_user.profile
        )
        UnresolvedQuery.objects.create(
            question="test", category="cat2", user=self.new_user.profile
        )

        # Checking the __str__ methods
        self.assertEqual(str(entry_1), entry_1.question)

        entry_2 = Query.objects.first()
        self.assertEqual(str(entry_2), entry_2.question)

    def test_query(self):
        """Test `/api/query`"""

        url = "/api/query"
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

    def test_categories(self):
        """Test `/api/query/categories`"""

        url = "/api/query/categories"
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

    def test_query_add(self):
        """Test `/api/query/add`"""
        data = {}
        url = "/api/query/add"
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, 403)

        data = {"question": "test"}
        url = "/api/query/add"
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["category"], "Others")

    def test_query_admin(self):
        queryset = UnresolvedQuery.objects.all()
        make_resolved("", "", queryset)

        queryset = UnresolvedQuery.objects.filter(resolved=False)
        self.assertEqual(len(queryset), 0)

    def test_query_notification(self):
        entry = UnresolvedQuery.objects.create(
            question="test", category="cat1", user=self.user.profile
        )
        handle_entry(entry)

        # Get notifications
        url = "/api/notifications"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["actor"]["question"], entry.question)
