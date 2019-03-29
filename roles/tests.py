"""Unit tests for Roles."""
from rest_framework.test import APITestCase
from bodies.models import Body
from bodies.models import BodyChildRelation
from roles.models import BodyRole
from roles.models import InstituteRole
from users.models import UserFormerRole
from login.tests import get_new_user

class RoleTestCase(APITestCase):
    """Tests for roles."""

    def setUp(self):
        # Fake authenticate
        self.user = get_new_user()
        self.client.force_authenticate(self.user)  # pylint: disable=E1101

        self.body = Body.objects.create(name="Body1")
        self.bodyrole = BodyRole.objects.create(
            name="Role", body=self.body, permissions=['Role'], inheritable=True)
        self.instirole = InstituteRole.objects.create(
            name="InstiRole", permissions=['RoleB'])

    def test_roles_other(self):
        """Check misc parameters of Roles."""
        self.assertEqual(str(self.instirole), self.instirole.name)
        self.assertEqual(str(self.bodyrole), self.body.name + " " + self.bodyrole.name)
        self.assertEqual(self.bodyrole.official_post, True)

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
        """Check we can update roles."""

        url = '/api/roles/' + str(self.bodyrole.id)
        data = {
            "id": str(self.bodyrole.id),
            "name": "Updated Role",
            "body": str(self.body.id),
            "permissions": ['Role', 'AddE'],
            "users": [],
            "official_post": False
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, 403)

        # Check with body role
        self.user.profile.roles.add(self.bodyrole)
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, 200)
        self.bodyrole.refresh_from_db()
        self.assertEqual(self.bodyrole.official_post, False)

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

    def test_delete_body_role(self):
        """Check we can delete roles."""

        bodyrole1 = BodyRole.objects.create(
            name="Role1", body=self.body, permissions=['Role'])
        bodyrole2 = BodyRole.objects.create(
            name="Role2", body=self.body, permissions=['Role'])
        bodyrole3 = BodyRole.objects.create(
            name="Role3", body=self.body, permissions=['Role'])

        # Check without role
        url = '/api/roles/' + str(bodyrole2.id)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 403)

        # Check with body role
        self.user.profile.roles.add(bodyrole1)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)

        # Check with former user
        url = '/api/roles/' + str(bodyrole3.id)
        profile = get_new_user().profile
        frole = UserFormerRole.objects.create(user=profile, role=bodyrole3, year='2019')
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 403)
        frole.delete()
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)

        # Remove role
        self.user.profile.roles.remove(bodyrole1)

        # Check with institute role
        self.user.profile.institute_roles.add(self.instirole)
        url = '/api/roles/' + str(bodyrole1.id)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)
        self.user.profile.institute_roles.remove(self.instirole)

    def test_my_roles(self):
        """Test /api/user-me/roles."""

        non_inheritable_role = BodyRole.objects.create(
            name="NIR", body=self.body, inheritable=False, permissions=['AddE'])
        self.user.profile.roles.add(non_inheritable_role)

        self.user.profile.roles.add(self.bodyrole)
        body1 = Body.objects.create(name="Body1")
        BodyChildRelation.objects.create(parent=self.body, child=body1)
        body11 = Body.objects.create(name="Body11")
        BodyChildRelation.objects.create(parent=body1, child=body11)
        body111 = Body.objects.create(name="Body111")
        BodyChildRelation.objects.create(parent=body11, child=body111)

        url = '/api/user-me/roles'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
