"""Unit tests for Events."""
from django.utils import timezone
from rest_framework.test import APITestCase
from bodies.models import Body
from bodies.models import BodyChildRelation
from events.models import Event
from roles.models import BodyRole
from login.tests import get_new_user

class EventTestCase(APITestCase):
    """Check if we can create bodies and link events."""
    test_body_1 = None
    test_body_2 = None
    user = None
    body_1_role = None
    update_test_event = None
    update_event_data = None
    update_url = None

    def setUp(self):
        # Fake authenticate
        self.user = get_new_user()
        self.client.force_authenticate(self.user) # pylint: disable=E1101

        self.test_body_1 = Body.objects.create(name="TestBody1")
        self.test_body_2 = Body.objects.create(name="TestBody2")

        self.body_1_role = BodyRole.objects.create(
            name="Body1Role", body=self.test_body_1, permissions='AddE,UpdE,DelE')
        self.user.profile.roles.add(self.body_1_role)

        self.update_test_event = Event.objects.create(
            name='TestEventUpdated', start_time=timezone.now(),
            end_time=timezone.now())
        url = '/api/events/' + str(self.update_test_event.id)
        self.update_event_data = self.client.get(url).data
        self.update_url = '/api/events/' + str(self.update_test_event.id)

        Event.objects.create(
            name='TestEvent2', start_time=timezone.now(), end_time=timezone.now())

    def test_events_list(self):
        """Test if events can be listed."""
        url = '/api/events'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertGreater(response.data['data'][0]['weight'], 0)

    def test_event_get(self):
        """Test getting the event with id or str_id."""
        event = Event.objects.create(name="Test #Event 123!",
                                     start_time=timezone.now(), end_time=timezone.now())

        url = '/api/events/' + str(event.id)
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['name'], event.name)

        url = '/api/events/test-event-123-' + str(event.id)[:8]
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['name'], event.name)

    def test_event_creation(self):
        """Test if events can be created for the body."""

        # Test simple event creation
        url = '/api/events'
        data = {
            "name": "TestEvent1",
            "start_time": timezone.now(),
            "end_time": timezone.now(),
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

    def test_event_update(self):
        """Event can be updated."""
        self.test_body_1.events.add(self.update_test_event)
        self.update_event_data['bodies_id'] = [str(self.test_body_1.id)]
        response = self.client.put(self.update_url, self.update_event_data, format='json')
        self.assertEqual(response.status_code, 200)

    def test_event_update2(self):
        """Check that an unrelated event cannot be updated."""
        self.test_body_2.events.add(self.update_test_event)
        self.update_event_data['bodies_id'] = [str(self.test_body_2.id)]
        response = self.client.put(self.update_url, self.update_event_data, format='json')
        self.assertEqual(response.status_code, 403)

    def test_event_update3(self):
        """Check if event with multiple bodies can be updated while
        having permissions for any one of them."""
        self.test_body_1.events.add(self.update_test_event)
        self.test_body_2.events.add(self.update_test_event)
        self.update_event_data['bodies_id'] = [
            str(self.test_body_1.id), str(self.test_body_2.id)]
        response = self.client.put(self.update_url, self.update_event_data, format='json')
        self.assertEqual(response.status_code, 200)

    def test_event_update4(self):
        """Confirm body cannot be removed without role."""
        self.test_body_1.events.add(self.update_test_event)
        self.test_body_2.events.add(self.update_test_event)
        self.update_event_data['bodies_id'] = [str(self.test_body_1.id)]
        response = self.client.put(self.update_url, self.update_event_data, format='json')
        self.assertEqual(response.status_code, 403)

    def test_event_update5(self):
        """Confirm body can be removed with role."""
        self.test_body_1.events.add(self.update_test_event)
        self.test_body_2.events.add(self.update_test_event)
        self.update_event_data['bodies_id'] = [str(self.test_body_2.id)]
        response = self.client.put(self.update_url, self.update_event_data, format='json')
        self.assertEqual(response.status_code, 200)

    def test_event_update6(self):
        """Check that user cannot add body without roles for both."""
        self.test_body_1.events.add(self.update_test_event)
        self.update_event_data['bodies_id'] = [str(self.test_body_1.id), str(self.test_body_2.id)]
        response = self.client.put(self.update_url, self.update_event_data, format='json')
        self.assertEqual(response.status_code, 403)

    def test_event_update7(self):
        """Check that user can change bodies with roles for both."""
        self.test_body_1.events.add(self.update_test_event)
        body_2_role = BodyRole.objects.create(
            name="Body2Role", body=self.test_body_2, permissions=['UpdE', 'DelE'])
        self.user.profile.roles.add(body_2_role)
        self.update_event_data['bodies_id'] = [str(self.test_body_1.id)]
        response = self.client.put(self.update_url, self.update_event_data, format='json')
        self.assertEqual(response.status_code, 200)

    def test_event_update8(self):
        """Check that user can update event with inherited permission."""
        # Body 2 is the parent of 1
        self.test_body_1.events.add(self.update_test_event)

        body_2_role = BodyRole.objects.create(
            name="Body2Role", body=self.test_body_2,
            permissions=['UpdE', 'DelE'], inheritable=True)
        self.user.profile.roles.remove(self.body_1_role)
        self.user.profile.roles.add(body_2_role)

        # Check before adding child body relation
        self.update_event_data['description'] = "NEW DESCRIPTION"
        response = self.client.put(self.update_url, self.update_event_data, format='json')
        self.assertEqual(response.status_code, 403)

        # Add relation and test again
        BodyChildRelation.objects.create(parent=self.test_body_2, child=self.test_body_1)

        response = self.client.put(self.update_url, self.update_event_data, format='json')
        self.assertEqual(response.status_code, 200)

    def test_event_deletion(self):
        """Check if events can be deleted with priveleges."""
        now = timezone.now()
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
