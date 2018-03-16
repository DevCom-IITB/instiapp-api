"""Unit tests for Location."""
from rest_framework.test import APITestCase
from events.models import Event
from locations.models import Location

class LocationTestCase(APITestCase):
    """Check if we can create locations."""

    test_location_id = None

    def setUp(self):
        url = '/api/locations'
        data = {
            'name': 'TestLocation1',
            'lat': '1.000000',
            'lng': '2.000000'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 201)
        response.close()
        self.test_location_id = response.data['id']

    def test_event_link(self):
        """Test if events can be linked."""
        test_location = Location.objects.get(id=self.test_location_id)

        url = '/api/events'
        data = {
            "name": "TestEvent1",
            "start_time": "2017-03-04T18:48:47Z",
            "end_time": "2018-03-04T18:48:47Z",
            "venue_names": [test_location.name],
            "bodies_id": []
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 201)
        response.close()

        test_event = Event.objects.get(id=response.data['id'])
        self.assertEqual(test_event.venues.get(id=test_location.id), test_location)
