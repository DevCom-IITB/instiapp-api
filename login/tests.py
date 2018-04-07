import time
from subprocess import Popen
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from users.models import UserProfile

def get_new_user():
    user = User.objects.create(username="TestUser")
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

        # Try to log in
        url = 'http://localhost/api/login?code=TEST_CODE&redir=REDIRECT_URI&fcm_id=testfcm'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['profile']['name'], "First Name Last Name")

        # Confirm we are logged in
        url = 'http://localhost/api/login/get-user'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 200)

        # Terminate our server
        mock_server.terminate()

        # Test logout
        url = 'http://localhost/api/logout'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 200)
