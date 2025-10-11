"""Login Viewset."""
from datetime import timedelta
import requests
from django.conf import settings
from django.contrib.auth import logout
from django.utils import timezone
from django.core.mail import send_mail
from rest_framework import viewsets
from rest_framework.response import Response
from login.helpers import perform_login, create_key_send_mail, perform_alumni_login
from users.models import UserProfile
from users.serializer_full import UserProfileFullSerializer
from alumni.models import AlumniUser
from backend.settings import EMAIL_HOST_USER

# pylint: disable=C0301,W0702


class LoginViewSet(viewsets.ViewSet):
    """Login"""

    @staticmethod
    def login(request):
        """Log in.
        Uses the `code` and `redir` query parameters."""

        # Check if we have the auth code
        auth_code = request.GET.get("code")
        if auth_code is None:
            return Response({"message": "{?code} is required"}, status=400)

        # Check we have redir param
        redir = request.GET.get("redir")
        if redir is None:
            return Response({"message": "{?redir} is required"}, status=400)

        return perform_login(auth_code, redir, request)

    @staticmethod
    def pass_login(request):
        """DANGEROUS: Password Log in.
        Uses the `username` and `password` query parameters."""

        # Check if we have the username
        username = request.GET.get("username")
        if username is None:
            return Response({"message": "{?username} is required"}, status=400)

        # Check if we have the password
        password = request.GET.get("password")
        if password is None:
            return Response({"message": "{?password} is required"}, status=400)

        # Make a new session
        session = requests.Session()

        # Get constants
        URL = settings.SSO_LOGIN_URL
        REDIR = settings.SSO_DEFAULT_REDIR

        # Get a CSRF token and update referer
        response = session.get(URL, verify=not settings.SSO_BAD_CERT)
        csrf = response.cookies["csrftoken"]
        session.headers.update({"referer": URL})

        # Make POST data
        data = {
            "csrfmiddlewaretoken": csrf,
            "next": URL,
            "username": username,
            "password": password,
        }

        # Authenticate
        response = session.post(URL, data=data, verify=not settings.SSO_BAD_CERT)
        if not response.history:
            return Response({"message": "Bad username or password"}, status=403)

        # If the user has not authenticated in the past
        if "?code=" not in response.url:
            # Get the authorize page
            response = session.get(response.url, verify=not settings.SSO_BAD_CERT)
            csrf = response.cookies["csrftoken"]

            # Grant all SSO permissions
            data = {
                "csrfmiddlewaretoken": csrf,
                "redirect_uri": REDIR,
                "scope": "basic profile picture ldap sex phone program secondary_emails insti_address",
                "client_id": settings.SSO_CLIENT_ID,
                "state": "",
                "response_type": "code",
                "scopes_array": [
                    "profile",
                    "picture",
                    "ldap",
                    "sex",
                    "phone",
                    "program",
                    "secondary_emails",
                    "insti_address",
                ],
                "allow": "Authorize",
            }
            response = session.post(
                response.url, data, verify=not settings.SSO_BAD_CERT
            )

        # Get our auth code
        auth_code = response.url.split("?code=", 1)[1]

        return perform_login(auth_code, REDIR, request)

    @staticmethod
    def get_user(request):
        """Get session and profile."""

        # Check if the user is authenticated
        if not request.user.is_authenticated:
            return Response({"message": "not logged in"}, status=401)

        # Check if the user has a profile
        try:
            queryset = UserProfileFullSerializer.setup_eager_loading(
                UserProfile.objects
            )
            user_profile = queryset.get(user=request.user)
            profile_serialized = UserProfileFullSerializer(
                user_profile, context={"request": request}
            )
        except UserProfile.DoesNotExist:
            return Response({"message": "UserProfile doesn't exist"}, status=500)

        # Count this as a ping
        user_profile.last_ping = timezone.now()
        user_profile.save(update_fields=["last_ping"])

        # Return the details and nested profile
        return Response(
            {
                "sessionid": request.session.session_key,
                "user": request.user.username,
                "profile_id": user_profile.id,
                "profile": profile_serialized.data,
            }
        )

    @staticmethod
    def alumni_login(request):
        ldap = request.GET.get("ldap")
        if not ldap:
            return Response({"exist": False, "msg": "Ldap not defined"})
        # Helper function
        exist, msg = create_key_send_mail(ldap)
        # msg stores error message
        return Response({"exist": exist, "ldap": ldap, "msg": msg})

    @staticmethod
    def alumni_otp_conf(request):
        ldap_entered = request.GET.get("ldap")
        key = request.GET.get("otp")

        # Check existence of LDAP
        if ldap_entered is None:
            return Response({"error_status": True, "msg": "Please enter correct LDAP"})

        # Check past requests
        pastRequests = AlumniUser.objects.filter(ldap=ldap_entered)
        if not pastRequests:
            return Response({"error_status": True, "msg": "No past OTP Requests found"})
        lastRequest = pastRequests.order_by("-timeLoginRequest").first()

        # Check time limit of OTP
        if timezone.now() > lastRequest.timeLoginRequest + timedelta(minutes=15):
            return Response({"error_status": True, "msg": "Time Limit Exceeded"})

        # Check key
        if lastRequest.isCorrectKey(key):
            # Perform login
            session_key, user, profile_id, profile = perform_alumni_login(
                request, ldap_entered
            )
            return Response(
                {
                    "error_status": False,
                    "msg": "Logged in",
                    "sessionid": session_key,
                    "user": user,
                    "profile_id": profile_id,
                    "profile": profile,
                }
            )

        return Response({"error_status": True, "msg": "Wrong OTP, retry"})

    @staticmethod
    def resend_alumni_otp(request):
        ldap_entered = request.GET.get("ldap")

        # Check existence of LDAP
        if ldap_entered is None:
            return Response({"error_status": True, "msg": "Please enter correct LDAP"})

        # Check if OTP was ever generated
        pastRequests = AlumniUser.objects.filter(ldap=ldap_entered)
        if not pastRequests:
            return Response({"error_status": True, "msg": "No OTP generated"})

        # Check how long ago an OTP was generated and whether it can be resent
        lastRequest = pastRequests.order_by("-timeLoginRequest").first()
        if timezone.now() > lastRequest.timeLoginRequest + timedelta(minutes=15):
            return Response(
                {
                    "error_status": True,
                    "msg": "Session has expired, please enter LDAP again",
                }
            )

        # Check how many mails have been sent for this key
        lastKey = lastRequest.keyStored
        sameKeys = AlumniUser.objects.filter(ldap=ldap_entered, keyStored=lastKey)
        if len(sameKeys) == 3:
            return Response(
                {
                    "error_status": True,
                    "msg": "Limit reached: 3 emails sent for this OTP",
                }
            )

        # Resend mail
        try:
            send_mail(
                "Login Request on Alumni Portal",
                "Your OTP for Alumni Login on Instiapp is " + str(lastKey),
                EMAIL_HOST_USER,
                [str(ldap_entered) + "@iitb.ac.in"],
                fail_silently=False,
            )
        except:  # noqa: E722
            # Mail couldn't be sent
            return Response(
                {"error_status": True, "msg": "Server issues, please retry later"}
            )

        # Save request
        new_otp_req = AlumniUser(
            ldap=ldap_entered, keyStored=str(lastKey), timeLoginRequest=timezone.now()
        )
        new_otp_req.save()
        return Response({"error_status": False, "msg": "Resent OTP"})

    @staticmethod
    def logout(request):
        """Log out."""

        logout(request)
        return Response({"message": "logged out"})
