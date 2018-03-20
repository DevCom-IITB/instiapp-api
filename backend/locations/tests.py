"""Unit tests for Location."""
from rest_framework.test import APITestCase
from events.models import Event
from locations.models import Location
from bodies.models import Body
from roles.models import BodyRole
from login.tests import get_new_user

class LocationTestCase(APITestCase):
    """Check if we can create locations."""

    test_body_1 = None
    reusable_test_location = None
    user = None

    def setUp(self):
        # Fake authenticate
        self.user = get_new_user()
        self.client.force_authenticate(self.user) # pylint: disable=E1101

        self.test_body_1 = Body.objects.create(name="TestBody1")
        self.body_1_role = BodyRole.objects.create(
            name="Body1Role", body=self.test_body_1, permissions='AddE,UpdE,DelE')
        self.user.profile.roles.add(self.body_1_role)

        self.reusable_test_location = Location.objects.create(
            name='TestLocation1', reusable=True)

    def test_event_link(self):
        """Test if events can be linked."""

        url = '/api/events'
        data = {
            "name": "TestEvent1",
            "start_time": "2017-03-04T18:48:47Z",
            "end_time": "2018-03-04T18:48:47Z",
            "venue_names": [self.reusable_test_location.name, 'DirectAddedVenue'],
            "bodies_id": [str(self.test_body_1.id)]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 201)

        test_event = Event.objects.get(id=response.data['id'])
        self.assertEqual(test_event.venues.get(
            id=self.reusable_test_location.id), self.reusable_test_location)
