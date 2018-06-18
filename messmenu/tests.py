"""Unit tests for Mess."""
from rest_framework.test import APITestCase
from messmenu.models import MenuEntry
from messmenu.models import Hostel

class MessTestCase(APITestCase):
    """Check mess menu endpoints."""

    def setUp(self):
        # Dummy Hostels
        self.h1 = Hostel.objects.create(name="Hostel 1")
        self.h2 = Hostel.objects.create(name="Hostel 2")

        # Dummy menus
        self.h1m1 = MenuEntry.objects.create(day=1, hostel=self.h1)

    def test_mess_other(self):
        """Check misc paramters of Mess."""
        self.assertEqual(str(self.h1), self.h1.name)
        self.assertEqual(str(self.h1m1), self.h1.name + ' - ' + str(self.h1m1.day))

    def test_mess(self):
        """Test `/api/mess`"""

        url = '/api/mess'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(len(response.data[0]['mess']), 1)
