"""Unit tests for Roles."""
from rest_framework.test import APITestCase
from bodies.models import Body
from roles.models import BodyRole
from roles.models import InstituteRole
from login.tests import get_new_user

class RoleTestCase(APITestCase):
    """Tests for roles."""

    user = None
    body = None
    bodyrole = None
    instirole = None

    def setUp(self):
        # Fake authenticate
        self.user = get_new_user()
        self.client.force_authenticate(self.user) # pylint: disable=E1101

        self.body = Body.objects.create(name="Body1")
        self.bodyrole = BodyRole.objects.create(
            name="Role", body=self.body, permissions=['Role'])
        self.instirole = InstituteRole.objects.create(
            name="InstiRole", permissions=['RoleB'])

    def test_roles_other(self):
        """Check misc parameters of Roles."""
        self.assertEqual(str(self.instirole), self.instirole.name)
        self.assertEqual(str(self.bodyrole), self.body.name + " " + self.bodyrole.name)

    def test_create_body_role(self):
        """Check we can create roles."""

        # Check without permission
        url = '/api/roles'
        data = {
            "name": "New Role",
            "body": str(self.body.id),
            "permissions": ['AddE'],
            "users": []
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 403)

        # Check with body role
        self.user.profile.roles.add(self.bodyrole)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 201)

        # Check validation
        bad_data = {
            "name": "New Role",
            "permissions": ['AddE'],
            "users": []
        }
        response = self.client.post(url, bad_data, format='json')

        self.user.profile.roles.remove(self.bodyrole)

        # Check with institute role
        self.user.profile.institute_roles.add(self.instirole)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 201)
        self.user.profile.institute_roles.remove(self.instirole)

    def test_update_body_role(self):
        """Check we can create roles."""

        url = '/api/roles/' + str(self.bodyrole.id)
        data = {
            "id": str(self.bodyrole.id),
            "name": "Updated Role",
            "body": str(self.body.id),
            "permissions": ['Role', 'AddE'],
            "users": []
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, 403)

        # Check with body role
        self.user.profile.roles.add(self.bodyrole)
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, 200)

        # Test validation
        body2 = Body.objects.create(name="Body2")
        data['body'] = str(body2.id)
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, 400)
        data['body'] = str(self.body.id)

        self.user.profile.roles.remove(self.bodyrole)

        # Check with institute role
        self.user.profile.institute_roles.add(self.instirole)
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, 200)
        self.user.profile.institute_roles.remove(self.instirole)
