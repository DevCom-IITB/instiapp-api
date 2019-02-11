"""Unit tests for Events."""
from django.utils import timezone
from django.test import TransactionTestCase
from rest_framework.test import APIClient
from bodies.models import BodyChildRelation
from events.models import Event
from roles.models import BodyRole
from login.tests import get_new_user
from helpers.test_helpers import create_body
from helpers.test_helpers import create_event
from helpers.test_helpers import create_usertag
from helpers.test_helpers import create_usertagcategory

# pylint: disable=R0902

class EventTestCase(TransactionTestCase):
    """Check if we can create bodies and link events."""

    def setUp(self):
        # Fake authenticate
        self.user = get_new_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

        self.test_body_1 = create_body()
        self.test_body_2 = create_body()

        self.body_1_role = BodyRole.objects.create(
            name="Body1Role", body=self.test_body_1, permissions='AddE,UpdE,DelE')
        self.user.profile.roles.add(self.body_1_role)

        self.update_test_event = create_event(-24, -24)
        url = '/api/events/%s' % self.update_test_event.id
        self.update_event_data = self.client.get(url).data
        self.update_url = '/api/events/%s' % self.update_test_event.id

        create_event(-24, -24)

    def test_event_other(self):
        """Check misc paramters of Event"""
        self.assertEqual(str(self.update_test_event), self.update_test_event.name)

    def test_event_prioritizer(self):  # pylint: disable=R0914,R0915
        """Test the event prioritizer."""

        def assertOrder(events, url='/api/events'):
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            for index, event in enumerate(events):
                self.assertEqual(response.data['data'][index]['id'], str(event.id))

        def assertWeightOrder(events, url='/api/events'):
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            prev_weight = response.data['data'][0]['weight']
            for event in events:
                response_event = next(x for x in response.data['data'] if x['id'] == str(event.id))
                self.assertLess(response_event['weight'], prev_weight)
                prev_weight = response_event['weight']

        # Events in future:
        # event1 after event3 after event2
        # eventP1, eventP1 in past
        event1 = create_event(48, 48)
        event2 = create_event(4, 5)
        event3 = create_event(15, 16)
        eventP1 = create_event(-5, -4)
        eventP2 = create_event(-6, -5)

        # These events check linear decay after 15 days
        eventL1 = create_event(24 * 30, 24 * 30)
        eventL2 = create_event(24 * 20, 24 * 20)
        eventL3 = create_event(24 * 40, 24 * 40)

        assertOrder([event2, event3, event1, eventP1, eventP2])
        assertWeightOrder([eventL2, eventL1, eventL3])

        # Check followed bodies priorities
        body1 = create_body()
        body2 = create_body()
        body3 = create_body()
        body4 = create_body()
        body5 = create_body()
        self.user.profile.followed_bodies.add(body1, body2, body3, body4, body5)

        # After the user is following  a body of event 3, it should bump up
        event3.bodies.add(body1)
        assertOrder([event3, event2, event1, eventP1, eventP2])

        # Test the cap on followed bodies bonus
        event1.bodies.add(body1, body2, body3, body4, body5)
        assertOrder([event3, event1, event2, eventP1, eventP2])

        # Test that ended events do not receive bonus
        eventP2.bodies.add(body1, body2, body3, body4)
        eventP2.promotion_boost = 2000
        eventP2.save()
        assertOrder([event3, event1, event2, eventP1, eventP2])

        # Check user tags - setup the user
        self.user.profile.hostel = '1'
        self.user.profile.department = 'ME'
        self.user.profile.save()

        # Add one matching and one non-matching tag to both
        category1 = create_usertagcategory()
        h1_tag = create_usertag(category1, '1')
        h13_tag = create_usertag(category1, '13')
        event1.user_tags.add(h1_tag)
        event3.user_tags.add(h13_tag)

        # Add one matching tag to both events
        category2 = create_usertagcategory()
        me_tag = create_usertag(category2, 'ME', target='department')
        event1.user_tags.add(me_tag)
        event3.user_tags.add(me_tag)

        # Check new order
        assertOrder([event1, event2, eventP1])

        # Check if user needs to satisfy only one tag from each category
        event1.user_tags.add(h13_tag)
        assertOrder([event1, event2, eventP1])

        # Test null check - now the department matching tag is non matching
        self.user.profile.department = None
        self.user.profile.save()
        assertOrder([event2, eventP1])

        # Test if secondary_target is working
        me_tag.secondary_target = 'hostel'
        me_tag.secondary_regex = '1'
        me_tag.save()
        assertOrder([event1, event2, eventP1])

        # Test promotion boost
        event2.promotion_boost = 2000
        event2.save()
        assertOrder([event2, event1, eventP1])
        event2.promotion_boost = 0
        event2.save()

        # Test for anonymous user
        self.client.logout()
        assertOrder([event2, eventP1])

    def test_events_list(self):
        """Test if events can be listed."""
        url = '/api/events'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertGreater(response.data['data'][0]['weight'], 0)

        url = '/api/events?start=2017-05-17T08:10:35.599Z&end=2017-06-17T08:10:35.599Z'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['data']), 0)

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
        self.update_event_data['bodies_id'] = [str(self.test_body_1.id)]
        response = self.client.put(self.update_url, self.update_event_data, format='json')
        self.assertEqual(response.status_code, 403)

        # Add relation and test again
        BodyChildRelation.objects.create(parent=self.test_body_2, child=self.test_body_1)

        response = self.client.put(self.update_url, self.update_event_data, format='json')
        self.assertEqual(response.status_code, 200)

    def test_event_update9(self):
        """Event tags can be updated."""
        # Add an event to an updateable body
        event = create_event()
        self.test_body_1.events.add(event)

        # Get the response
        url = '/api/events/%s' % event.id
        data = self.client.get(url).data

        # Create tags and assign them
        category = create_usertagcategory()
        tag1 = create_usertag(category, '1')
        tag2 = create_usertag(category, '2')
        data['user_tags'] = [str(tag1.id), str(tag2.id)]
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(event.user_tags.count(), 2)

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

    def test_nobody(self):
        """Test events can't be created/updated to have no body."""
        response = self.client.post("/api/events", self.update_event_data, format='json')
        self.assertEqual(response.status_code, 403)

        response = self.client.put(self.update_url, self.update_event_data, format='json')
        self.assertEqual(response.status_code, 403)

    def test_ues(self):
        """Test user-event-status APIs."""

        def assert_user_ues(t_event, t_ues):
            """Test user_ues in event serializer."""

            url = '/api/events/%s' % t_event.id
            response = self.client.get(url, format='json')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.data['user_ues'], t_ues)

        def mark_test(event, ues, count):
            """Helper to mark UES and test creation/updation."""

            # Mark UES for the event
            url = '/api/user-me/ues/%s?status=%s' % (event.id, str(ues))
            response = self.client.get(url, format='json')
            self.assertEqual(response.status_code, 204)

            # Assert creation of UES
            self.assertEqual(event.ues.count(), count)
            assert_user_ues(event, ues)

            # Check first only if exists
            if count > 0:
                self.assertEqual(event.ues.first().status, ues)

        # Create event with one body
        test_body = create_body(name="Test Body1")
        test_event = create_event(name="Test Event1")
        test_event.bodies.add(test_body)
        self.assertEqual(test_event.ues.count(), 0)
        assert_user_ues(test_event, 0)

        # Test interested, going and neutral
        # When the user un-marks the event, UES must be removed
        mark_test(test_event, 1, 1)
        mark_test(test_event, 2, 1)
        mark_test(test_event, 0, 0)

        # Assert user_ues as anonymous
        self.client.logout()
        assert_user_ues(test_event, None)

    def test_anonymous(self):
        """Check APIs as anonymous user."""
        self.client.logout()

        url = '/api/events'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        response = self.client.get(self.update_url)
        self.assertEqual(response.status_code, 200)
