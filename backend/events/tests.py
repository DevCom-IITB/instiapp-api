"""Unit tests for Events."""
from rest_framework.test import APITestCase
from bodies.models import Body
from events.models import Event
from roles.models import BodyRole
from login.tests import get_new_user

class EventTestCase(APITestCase):
    """Check if we can create bodies and link events."""
    test_body_1 = None
    test_body_2 = None
    user = None
    body_1_role = None

    def setUp(self):
        # Fake authenticate
        self.user = get_new_user()
        self.client.force_authenticate(self.user) # pylint: disable=E1101

        self.test_body_1 = Body.objects.create(name="TestBody1")
        self.test_body_2 = Body.objects.create(name="TestBody2")

        self.body_1_role = BodyRole.objects.create(
            name="Body1Role", body=self.test_body_1, permissions='AddE,UpdE,DelE')
        self.user.profile.roles.add(self.body_1_role)

    def test_events_list(self):
        """Test if events can be listed."""
        url = '/api/events'
        self.assertEqual(self.client.get(url).status_code, 200)

    def test_event_creation(self):
        """Test if events can be created for the body."""

        # Test simple event creation
        url = '/api/events'
        data = {
            "name": "TestEvent1",
            "start_time": "2017-03-04T18:48:47Z",
            "end_time": "2018-03-04T18:48:47Z",
            "venue_names": [],
            "bodies_id": [str(self.test_body_1.id)]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 201)
        response.close()

        test_event = Event.objects.get(id=response.data['id'])
        self.assertEqual(test_event.name, 'TestEvent1')
        self.assertEqual(test_event.bodies.get(id=self.test_body_1.id), self.test_body_1)

        # Check that events cannot be created without roles
        data['bodies_id'] = [str(self.test_body_1.id), str(self.test_body_2.id)]
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 403)

        # Check that events can be created with roles
        body_2_role = BodyRole.objects.create(
            name="Body2Role", body=self.test_body_2, permissions='AddE')
        self.user.profile.roles.add(body_2_role)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 201)
        self.user.profile.roles.remove(body_2_role)

    def test_event_deletion(self):
        """Check if events can be deleted with priveleges."""
        now = "2018-03-05T06:00:00Z"
        event = Event.objects.create(
            name="TestEvent", start_time=now, end_time=now)
        self.test_body_1.events.add(event)
        self.test_body_2.events.add(event)

        url = '/api/events/' + str(event.id)

        # Check that events cannot be deleted without role for body_2
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 403)

        # Check that events can be deleted with roles for both bodies
        body_2_role = BodyRole.objects.create(
            name="Body2Role", body=self.test_body_2, permissions='DelE')
        self.user.profile.roles.add(body_2_role)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)
        self.user.profile.roles.remove(body_2_role)
