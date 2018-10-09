import time
import random
from subprocess import Popen
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from users.models import UserProfile

def get_new_user():
    user = User.objects.create(username="TestUser" + str(time.time() + random.randint(1, 2e6)))
    UserProfile.objects.create(name="TestUserProfile", user=user)
    return user

class LoginTestCase(APITestCase):
    """Check login flow."""

    def setUp(self):
        pass

    def test_login(self):
        """Test if SSO login works."""

        # Start mock SSO server and wait to be sure it has started
        mock_server = Popen(['python', 'login/test_server.py'])
        time.sleep(1)

        # Check validation
        # Without code
        url = 'http://localhost/api/login?redir=REDIRECT_URI'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 400)

        # Without redir
        url = 'http://localhost/api/login?code=TEST_CODE'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 400)

        # Try to log in with wrong code
        url = 'http://localhost/api/login?code=T_CODE&redir=REDIRECT_URI'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 400)

        # Try to log in with bad code
        url = 'http://localhost/api/login?code=BAD_TEST_CODE&redir=REDIRECT_URI&fcm_id=testfcm'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 400)

        # Try to log in with insufficient SSO privileges
        url = 'http://localhost/api/login?code=TEST_CODE_LP&redir=REDIRECT_URI&fcm_id=testfcm'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 403)

        # Try to log in
        url = 'http://localhost/api/login?code=TEST_CODE&redir=REDIRECT_URI&fcm_id=testfcm'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['profile']['name'], "First Name Last Name")

        # Confirm we are logged in
        url = 'http://localhost/api/login/get-user'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 200)

        # Assert that at least a few fields are saved correctly
        user = UserProfile.objects.get(id=response.data['profile_id'])
        self.assertEqual(user.email, "username@iitb.ac.in")
        self.assertEqual(user.department, "DEPARTMENT")
        self.assertEqual(user.join_year, 2012)
        self.assertEqual(user.hostel, "HOSTEL")
        self.assertEqual(user.room, "room_number")

        # Terminate our server
        mock_server.terminate()

        # Test logout
        url = 'http://localhost/api/logout'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 200)

        # Try get-user after logout
        url = 'http://localhost/api/login/get-user'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 401)

        # Try get-user without profile
        user = User.objects.get(username='3')
        self.client.force_authenticate(user)  # pylint: disable=E1101
        user.profile.delete()
        url = 'http://localhost/api/login/get-user'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 500)

    def test_pass_login(self):
        """Test if password login works."""

        # Start mock server
        mock_server = Popen(['python', 'login/test_server.py'])
        time.sleep(1)

        # Check validation
        # Without password
        url = 'http://localhost/api/pass-login?username=user'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 400)

        # Without user
        url = 'http://localhost/api/pass-login?password=pass'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 400)

        # Login with bad password
        url = 'http://localhost/api/pass-login?username=biguser&password=badpass'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 403)

        # Login with correct username password
        url = 'http://localhost/api/pass-login?username=biguser&password=bigpass'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 200)

        # Login with correct username password
        url = 'http://localhost/api/pass-login?username=smalluser&password=smallpass'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 200)

        # Terminate server
        mock_server.terminate()
