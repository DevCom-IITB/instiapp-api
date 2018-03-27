"""Unit tests for Body."""
from rest_framework.test import APITestCase
from bodies.models import Body
from roles.models import InstituteRole
from roles.models import BodyRole
from login.tests import get_new_user

class BodyTestCase(APITestCase):
    """Check if we can create bodies and link events."""
    test_body_1_id = None
    test_body_2_id = None
    user = None
    insti_role = None
    body_1_role = None

    def setUp(self):
        # Fake authenticate
        self.user = get_new_user()
        self.client.force_authenticate(self.user) # pylint: disable=E1101

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
