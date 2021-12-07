"""Unit tests for QueryBot."""
from rest_framework.test import APITestCase
from rest_framework.test import APIClient
from querybot.admin import handle_entry
from querybot.models import UnresolvedQuery
from querybot.management.commands.query_bot_chore import handle_entry_fromsheet
from login.tests import get_new_user

class MessTestCase(APITestCase):
    """Check querbot endpoints."""

    def setUp(self):
        # Fake authenticate
        self.user = get_new_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

        # Dummy Queries
        rows = [[0, 'test', 'test', 'cat1', '', ''], [1, 'test', 'test', 'cat2', '', '']]

        for row in rows:
            handle_entry_fromsheet(row)

        # Dummy Unresolved queries
        self.new_user = get_new_user()
        UnresolvedQuery.objects.create(question="test", category="cat1", user=self.new_user.profile)
        UnresolvedQuery.objects.create(question="test", category="cat2", user=self.new_user.profile)

    def test_query(self):
        """Test `/api/query`"""

        url = '/api/query'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

    def test_query_add(self):
        """Test `/api/query/add`"""
        data = {
            'question': 'test'
        }
        url = '/api/query/add'
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['category'], 'Others')

    def test_query_admin(self):
        queryset = UnresolvedQuery.objects.all()
        for entry in queryset:
            handle_entry(entry, notify_user=False)

        queryset = UnresolvedQuery.objects.all()
        self.assertEqual(len(queryset), 0)
