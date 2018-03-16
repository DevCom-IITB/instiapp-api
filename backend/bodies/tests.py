"""Unit tests for Body."""
from rest_framework.test import APITestCase
from bodies.models import Body
from events.models import Event

class BodyTestCase(APITestCase):
    """Check if we can create bodies and link events."""
    def setUp(self):
        url = '/api/bodies'
        data = {
            'name': 'TestBody1',
            'image_url': 'http://example.com/image.png'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 201)
        response.close()

        data = {
            'name': 'TestBody2',
            'image_url': 'http://example.com/image2.png'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 201)
        response.close()

    def test_bodies_created(self):
        """Test if bodies was properly created."""
        test_body = Body.objects.get(name='TestBody1')
        self.assertEqual(test_body.name, 'TestBody1')
        self.assertEqual(test_body.image_url, 'http://example.com/image.png')

        test_body = Body.objects.get(name='TestBody2')
        self.assertEqual(test_body.name, 'TestBody2')
        self.assertEqual(test_body.image_url, 'http://example.com/image2.png')

    def test_event_creation(self):
        """Test if events can be created for the body."""
        test_body = Body.objects.get(name='TestBody1')
        test_body2 = Body.objects.get(name='TestBody2')
        url = '/api/events'
        data = {
            "name": "TestEvent1",
            "start_time": "2017-03-04T18:48:47Z",
            "end_time": "2018-03-04T18:48:47Z",
            "venues_names": [],
            "bodies_id": [test_body.id, test_body2.id]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 201)
        response.close()

        test_event = Event.objects.get(name='TestEvent1')
        self.assertEqual(test_event.name, 'TestEvent1')
        self.assertEqual(test_event.bodies.all()[0].name, 'TestBody1')
        self.assertEqual(test_event.bodies.all()[1].name, 'TestBody2')
