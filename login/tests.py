from datetime import datetime
import time
import random
from subprocess import Popen
from freezegun.api import freeze_time
from rest_framework.test import APIClient, APITestCase
from django.core import mail
from django.contrib.auth.models import User
from alumni.models import AlumniUser
from users.models import UserProfile


def get_new_user():
    user = User.objects.create(
        username="TestUser" + str(time.time() + random.randint(1, 2e6))
    )
    UserProfile.objects.create(name="TestUserProfile", user=user, ldap_id="test")
    return user


class LoginTestCase(APITestCase):
    """Check login flow."""

    def setUp(self):
        self.mock_server = Popen(["python", "login/test_server.py"])
        time.sleep(1)

    def test_login(self):
        """Test if SSO login works."""

        # Check validation
        # Without code
        url = "http://localhost/api/login?redir=REDIRECT_URI"
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, 400)

        # Without redir
        url = "http://localhost/api/login?code=TEST_CODE"
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, 400)

        # Try to log in with wrong code
        url = "http://localhost/api/login?code=T_CODE&redir=REDIRECT_URI"
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, 400)

        # Try to log in with bad code
        url = "http://localhost/api/login?code=BAD_TEST_CODE&redir=REDIRECT_URI&fcm_id=testfcm"
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, 400)

        # Try to log in with insufficient SSO privileges
        url = "http://localhost/api/login?code=TEST_CODE_LP&redir=REDIRECT_URI&fcm_id=testfcm"
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, 403)

        # Try to log in
        url = "http://localhost/api/login?code=TEST_CODE&redir=REDIRECT_URI&fcm_id=testfcm"
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["profile"]["name"], "First Name Last Name")

        # Confirm we are logged in
        url = "http://localhost/api/login/get-user"
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, 200)

        # Assert user profile properties
        user = UserProfile.objects.get(id=response.data["profile_id"])
        self.assertEqual(user.name, "First Name Last Name")
        self.assertEqual(user.email, "username@iitb.ac.in")
        self.assertEqual(user.contact_no, "9876543210")
        self.assertEqual(
            user.profile_pic,
            "https://gymkhana.iitb.ac.in/sso/path/to/profile_picture_file",
        )
        self.assertEqual(user.join_year, "2012")
        self.assertEqual(user.department, "DEPARTMENT")
        self.assertEqual(user.degree, "DEGREE")
        self.assertEqual(user.hostel, "HOSTEL")
        self.assertEqual(user.room, "room_number")

        # Assert user object properties
        self.assertEqual(user.user.first_name, "First Name")
        self.assertEqual(user.user.last_name, "Last Name")

        # Test logout
        url = "http://localhost/api/logout"
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, 200)

        # Try get-user after logout
        url = "http://localhost/api/login/get-user"
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, 401)

        # Try get-user without profile
        user = User.objects.get(username="3")
        self.client.force_authenticate(user)  # pylint: disable=E1101
        user.profile.delete()
        url = "http://localhost/api/login/get-user"
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, 500)

    def test_pass_login(self):
        """Test if password login works."""

        # Check validation
        # Without password
        url = "http://localhost/api/pass-login?username=user"
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, 400)

        # Without user
        url = "http://localhost/api/pass-login?password=pass"
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, 400)

        # Login with bad password
        url = "http://localhost/api/pass-login?username=biguser&password=badpass"
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, 403)

        # Login with correct username password
        url = "http://localhost/api/pass-login?username=biguser&password=bigpass"
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, 200)

        # Login with correct username password
        url = "http://localhost/api/pass-login?username=smalluser&password=smallpass"
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, 200)

    def tearDown(self):
        self.mock_server.terminate()


class AlumniLoginTestCase(APITestCase):
    @freeze_time("2018-01-02")
    def setUp(self):
        self.user = get_new_user()
        self.client = APIClient()
        self.alumni = AlumniUser.objects.create(
            ldap="test-1", keyStored="100000", timeLoginRequest=datetime.now()
        )
        self.assertEqual(str(self.alumni), "test-1")

    @freeze_time("2019-01-02")
    def test_alumni_login(self):
        """Test if alumni login is working"""

        # Try OTP generation with fake ldap
        url = "/api/alumniLogin"
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["exist"], False)

        url = "/api/alumniLogin?ldap="
        response = self.client.get(url + "fake", format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["exist"], False)

        # Using settings to test sending an email
        with self.settings(
            EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend"
        ):
            # Try OTP generation with real ldap
            response = self.client.get(url + "test", format="json")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.data["exist"], True)
            self.assertEqual(response.data["ldap"], "test")
            self.assertEqual(len(mail.outbox), 1)

            # Try creating a new OTP within 15 min
            response = self.client.get(url + "test", format="json")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.data["exist"], True)
            self.assertEqual(
                response.data["msg"], "An OTP was already sent to your mail before"
            )
            self.assertEqual(len(mail.outbox), 1)

            # Resending OTP without valid ldap
            url = "/api/resendAlumniOTP"
            response = self.client.get(url, format="json")
            self.assertEqual(response.data["error_status"], True)

            url = "/api/resendAlumniOTP?ldap="
            response = self.client.get(url + "fake", format="json")
            self.assertEqual(response.data["error_status"], True)

            # Resending OTP with valid ldap
            response = self.client.get(url + "test", format="json")
            self.assertEqual(response.data["error_status"], False)
            response = self.client.get(url + "test", format="json")
            self.assertEqual(response.data["error_status"], False)
            self.assertEqual(len(mail.outbox), 3)

            # Resending OTP more than 3 timestamp
            response = self.client.get(url + "test", format="json")
            self.assertEqual(response.data["error_status"], True)
            self.assertEqual(len(mail.outbox), 3)

            # Testing resend with old OTP
            response = self.client.get(url + "test-1", format="json")
            self.assertEqual(response.data["error_status"], True)

            # Testing OTP validation with invalid ldap
            url = "/api/alumniOTP"
            response = self.client.get(url, format="json")
            self.assertEqual(response.data["error_status"], True)

            url = "/api/alumniOTP?ldap="
            response = self.client.get(url + "fake", format="json")
            self.assertEqual(response.data["error_status"], True)

            # Testing OTP validation with incorrect OTP
            response = self.client.get(url + "test&otp=invalid", format="json")
            self.assertEqual(response.data["error_status"], True)

            # Testing validation with old OTP
            response = self.client.get(url + "test-1", format="json")
            self.assertEqual(response.data["error_status"], True)

            # Testing validation with correct OTP
            otp = AlumniUser.objects.order_by("-timeLoginRequest").first().keyStored
            response = self.client.get(url + "test&otp=" + otp, format="json")
            self.assertEqual(response.data["error_status"], False)

    @freeze_time("2020-01-02")
    def test_send_mail_error(self):
        # Testing the try and except blocks

        with self.settings(EMAIL_BACKEND="django.core.mail.backends.smtp.EmailBackend"):
            url = "/api/alumniLogin?ldap="
            response = self.client.get(url + "test", format="json")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.data["exist"], False)

        with self.settings(
            EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend"
        ):
            response = self.client.get(url + "test", format="json")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.data["exist"], True)

        url = "/api/resendAlumniOTP?ldap="
        with self.settings(EMAIL_BACKEND="django.core.mail.backends.smtp.EmailBackend"):
            response = self.client.get(url + "test", format="json")
            self.assertEqual(response.data["error_status"], True)
