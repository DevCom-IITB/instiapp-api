"""Unit tests for upload."""
from django.utils import timezone
from rest_framework.test import APITestCase
from bodies.models import Body
from bodies.models import BodyChildRelation
from events.models import Event
from news.models import NewsEntry
from users.models import UserProfile
from locations.models import Location

class PrerenderTestCase(APITestCase):
    """Check if prerender is working."""

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

        self.news1 = NewsEntry.objects.create(
            guid="https://test.com", title="NewsIsGreat",
            body=self.test_body, blog_url="https://blog", link="https://blog-item"
        )

        parent_body = Body.objects.create(name="Parent")
        grandparent_body = Body.objects.create(name="GrandParent")
        BodyChildRelation.objects.create(parent=parent_body, child=self.test_body)
        BodyChildRelation.objects.create(parent=grandparent_body, child=parent_body)

    def test_root(self):
        """Root page prerender test."""
        url = '/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.test_event.name)
        self.assertContains(response, self.test_event.bodies.all()[0].name)

    def test_news(self):
        """Test news prerender."""
        url = '/news'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.news1.title)
        self.assertContains(response, self.news1.link)
        self.assertContains(response, self.test_body.name)

    def test_explore(self):
        """Test explore prerender."""
        url = '/explore'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.test_body.name)

    def test_user_details(self):
        """Test user prerender."""

        url = '/user/' + str(self.test_profile.id)
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.test_profile.name)
        self.assertContains(response, self.test_profile.roll_no)
        self.assertNotContains(response, self.test_profile.email)
        self.assertNotContains(response, self.test_profile.contact_no)

        url = '/user/' + str(self.test_profile.ldap_id)
        self.assertEqual(self.client.get(url).content, response.content)

    def test_body_details(self):
        """Test body prerender."""

        url = '/org/' + str(self.test_body.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.test_body.name)
        self.assertContains(response, self.test_body.events.all()[0].name)
        self.assertContains(response, self.test_body.events.all()[1].name)

        url = '/org/' + str(self.test_body.str_id)
        self.assertEqual(self.client.get(url).content, response.content)

    def test_event_details(self):
        """Test event prerender."""

        url = '/event/' + str(self.test_event.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.test_event.name)
        self.assertContains(response, self.test_body.name)

        url = '/event/' + str(self.test_event.str_id)
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

    def test_map(self):
        url = '/map'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        nonlocation = Location.objects.create(
            name='I am great!', short_name='My Big Location', reusable=False)
        location = Location.objects.create(
            name='Nice location', short_name='My Big Location', reusable=True)
        url = '/map/my-big-location'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, location.name)
        self.assertNotContains(response, nonlocation.name)
        self.assertContains(response, str(location.id) + '.jpg')
