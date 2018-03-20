"""Unit tests for Body."""
from rest_framework.test import APITestCase
from bodies.models import Body
from events.models import Event
from roles.models import InstituteRole
from roles.models import BodyRole
from login.tests import get_new_user

class BodyTestCase(APITestCase):
    """Check if we can create bodies and link events."""
    test_body_1_id = None
    test_body_2_id = None
    user = None

    def setUp(self):
        # Fake authenticate
        self.user = get_new_user()
        self.client.force_authenticate(self.user) # pylint: disable=E1101

        insti_role = InstituteRole.objects.create(
            name='TestInstiRole',
            permissions=['AddB'])
        self.user.profile.institute_roles.add(insti_role)

        url = '/api/bodies'
        data = {
            'name': 'TestBody1',
            'image_url': 'http://example.com/image.png'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 201)
        response.close()
        self.test_body_1_id = response.data['id']

        test_body_1 = Body.objects.get(id=self.test_body_1_id)
        body_1_role = BodyRole.objects.create(
            name="Body1Role", body=test_body_1, permissions='AddE')
        self.user.profile.roles.add(body_1_role)

        data = {
            'name': 'TestBody2',
            'image_url': 'http://example.com/image2.png'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 201)
        response.close()
        self.test_body_2_id = response.data['id']

    def test_bodies_created(self):
        """Test if bodies was properly created."""
        test_body = Body.objects.get(id=self.test_body_1_id)
        self.assertEqual(test_body.name, 'TestBody1')
        self.assertEqual(test_body.image_url, 'http://example.com/image.png')

        test_body = Body.objects.get(id=self.test_body_2_id)
        self.assertEqual(test_body.name, 'TestBody2')
        self.assertEqual(test_body.image_url, 'http://example.com/image2.png')

    def test_event_creation(self):
        """Test if events can be created for the body."""

        test_body_1 = Body.objects.get(id=self.test_body_1_id)
        test_body_2 = Body.objects.get(id=self.test_body_2_id)

        url = '/api/events'
        data = {
            "name": "TestEvent1",
            "start_time": "2017-03-04T18:48:47Z",
            "end_time": "2018-03-04T18:48:47Z",
            "venue_names": [],
            "bodies_id": [self.test_body_1_id]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 201)
        response.close()

        test_event = Event.objects.get(id=response.data['id'])
        self.assertEqual(test_event.name, 'TestEvent1')
        self.assertEqual(test_event.bodies.get(id=test_body_1.id), test_body_1)
