"""Unit tests for upload."""
from django.utils import timezone
from rest_framework.test import APITestCase
from bodies.models import Body
from bodies.models import BodyChildRelation
from events.models import Event
from users.models import UserProfile

class PrerenderTestCase(APITestCase):
    """Check if prerender is working."""

    test_profile = None
    test_body = None
    test_event = None

    def setUp(self):
        self.test_profile = UserProfile.objects.create(
            name="TestUser", email="my@email.com", roll_no="10000001", ldap_id='ldap')
        self.test_body = Body.objects.create(name="Test Body")
        event1 = Event.objects.create(
            name="Event 1", start_time=timezone.now(), end_time=timezone.now())
        event2 = Event.objects.create(
            name="Test Event2", start_time=timezone.now(), end_time=timezone.now())
        self.test_body.events.add(event1)
        self.test_body.events.add(event2)
        self.test_event = event1

    def test_user_details(self):
        """Test user-details prerender."""

        url = '/user-details/' + str(self.test_profile.id)
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.test_profile.name)
        self.assertContains(response, self.test_profile.roll_no)
        self.assertNotContains(response, self.test_profile.email)

        url = '/user-details/' + str(self.test_profile.ldap_id)
        self.assertEqual(self.client.get(url).content, response.content)

    def test_body_details(self):
        """Test body-details prerender."""

        url = '/body-details/' + str(self.test_body.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.test_body.name)
        self.assertContains(response, self.test_body.events.all()[0].name)
        self.assertContains(response, self.test_body.events.all()[1].name)

        url = '/body-details/' + str(self.test_body.str_id)
        self.assertEqual(self.client.get(url).content, response.content)

    def test_event_details(self):
        """Test event-details prerender."""

        url = '/event-details/' + str(self.test_event.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.test_event.name)
        self.assertContains(response, self.test_body.name)

        url = '/event-details/' + str(self.test_event.str_id)
        self.assertEqual(self.client.get(url).content, response.content)

    def test_tree(self):
        body1 = Body.objects.create(name="Body1")
        body2 = Body.objects.create(name="Body2")
        body11 = Body.objects.create(name="Body11")

        BodyChildRelation.objects.create(parent=self.test_body, child=body1)
        BodyChildRelation.objects.create(parent=self.test_body, child=body2)
        BodyChildRelation.objects.create(parent=body1, child=body11)

        url = '/body-tree/' + str(self.test_body.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        self.assertContains(response, self.test_body.name)
        self.assertContains(response, body1.name)
        self.assertContains(response, body2.name)
        self.assertContains(response, body11.name)
