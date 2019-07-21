"""Unit tests for Body."""
from django.test import TransactionTestCase
from rest_framework.test import APIClient
from bodies.models import Body
from bodies.models import BodyChildRelation
from roles.models import InstituteRole
from roles.models import BodyRole
from login.tests import get_new_user

class BodyTestCase(TransactionTestCase):
    """Check if we can create bodies and link events."""

    def setUp(self):
        # Fake authenticate
        self.user = get_new_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

        self.insti_role = InstituteRole.objects.create(
            name='TestInstiRole',
            permissions=['AddB'])
        self.user.profile.institute_roles.add(self.insti_role)

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
        self.body_1_role = BodyRole.objects.create(
            name="Body1Role", body=test_body_1, permissions='AddE')
        self.user.profile.roles.add(self.body_1_role)

        data = {
            'name': 'TestBody2',
            'image_url': 'http://example.com/image2.png'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 201)
        response.close()
        self.test_body_2_id = response.data['id']

    def test_body_other(self):
        """Check misc paramters of Body"""
        body = Body.objects.create(name="TestBody")
        child = Body.objects.create(name="ChildBody")
        cbr = BodyChildRelation.objects.create(parent=body, child=child)

        self.assertEqual(str(body), body.name)
        self.assertEqual(str(cbr), body.name + " --> " + child.name)

    def test_body_get(self):
        """Test getting the body with id or str_id."""
        body = Body.objects.create(name="Test #Body 123!")

        # Test GET by plain UUID
        url = '/api/bodies/' + str(body.id)
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['name'], body.name)

        # Test GET with str_id
        url = '/api/bodies/test-body-123'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['name'], body.name)

        # Change the canonical name
        body.canonical_name = "Test Canonical"
        body.save()

        # Test GET with canonical name
        url = '/api/bodies/test-canonical'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['str_id'], body.str_id)

        # Add some followers
        users = [get_new_user().profile for _ in range(10)]
        for user in users:
            user.followed_bodies.add(body)

        # Test follower count and user_follows
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['followers_count'], 10)
        self.assertEqual(response.data['user_follows'], False)

        # Add self as follower and try same thing
        self.user.profile.followed_bodies.add(body)
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['followers_count'], 11)
        self.assertEqual(response.data['user_follows'], True)

        # Mark a user as inactive and check
        users[0].active = False
        users[0].save()
        self.user.profile.followed_bodies.add(body)
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['followers_count'], 10)
        self.assertEqual(response.data['user_follows'], True)

    def test_bodies_list(self):
        """Test if bodies can be listed."""
        url = '/api/bodies'
        self.assertEqual(self.client.get(url).status_code, 200)

    def test_bodies_created(self):
        """Test if bodies was properly created."""
        test_body = Body.objects.get(id=self.test_body_1_id)
        self.assertEqual(test_body.name, 'TestBody1')
        self.assertEqual(test_body.image_url, 'http://example.com/image.png')

        test_body = Body.objects.get(id=self.test_body_2_id)
        self.assertEqual(test_body.name, 'TestBody2')
        self.assertEqual(test_body.image_url, 'http://example.com/image2.png')

    def test_body_update(self):
        """Test if body can be updated with proper roles."""

        url = '/api/bodies/' + self.test_body_1_id
        data = {
            'name': 'TestBody1Upd',
            'image_url': 'http://example.com/image_new.png'
        }

        # Try without role
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, 403)

        # Try with role
        self.body_1_role.permissions += ',UpdB'
        self.body_1_role.save()
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, 200)
        test_body = Body.objects.get(id=self.test_body_1_id)
        self.assertEqual(test_body.name, 'TestBody1Upd')

    def test_body_deletion(self):
        """Test if body can be deleted with insti role."""
        body = Body.objects.create(name="TestBody3")
        url = '/api/bodies/' + str(body.id)

        # Try without priveleges
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 403)

        # Try with priveleges
        self.insti_role.permissions += ['DelB']
        self.insti_role.save()
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)

    def test_body_follow(self):
        """Test if body follow API works."""

        body = Body.objects.create(name="TestBody3")
        url = '/api/bodies/' + str(body.id) + '/follow'

        # No query
        response = self.client.get(url)
        self.assertEqual(response.status_code, 400)

        url += '?action='

        # Invalid Action
        response = self.client.get(url + 'k')
        self.assertEqual(response.status_code, 400)

        # Follow
        response = self.client.get(url + '1')
        self.assertEqual(response.status_code, 204)
        self.assertIn(body, self.user.profile.followed_bodies.all())

        # Check user_follows
        response = self.client.get('/api/bodies/' + str(body.id))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['user_follows'], True)

        # Unfollow
        response = self.client.get(url + '0')
        self.assertEqual(response.status_code, 204)
        self.assertNotIn(body, self.user.profile.followed_bodies.all())

        # Check user_follows
        response = self.client.get('/api/bodies/' + str(body.id))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['user_follows'], False)
