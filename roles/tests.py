"""Unit tests for Roles."""
from rest_framework.test import APITestCase
from bodies.models import Body
from roles.models import BodyRole
from roles.models import InstituteRole
from login.tests import get_new_user

class RoleTestCase(APITestCase):
    """Tests for roles."""

    body = None
    bodyrole = None
    instirole = None

    def setUp(self):
        # Fake authenticate
        self.user = get_new_user()
        self.client.force_authenticate(self.user) # pylint: disable=E1101

        self.body = Body.objects.create(name="Body1")
        self.bodyrole = BodyRole.objects.create(name="Role", body=self.body)
        self.instirole = InstituteRole.objects.create(name="InstiRole")

    def test_roles_other(self):
        """Check misc parameters of Roles"""
        self.assertEqual(str(self.instirole), self.instirole.name)
        self.assertEqual(str(self.bodyrole), self.body.name + " " + self.bodyrole.name)
