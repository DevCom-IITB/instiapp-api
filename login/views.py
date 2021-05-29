"""Login Viewset."""
import requests
from django.conf import settings
from django.contrib.auth import logout
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.response import Response
from login.helpers import perform_google_login, perform_login
from users.models import UserProfile
from users.serializer_full import UserProfileFullSerializer

# Google login
import google.oauth2.credentials
import google_auth_oauthlib.flow
import requests

CLIENT_SECRETS_FILE = "client_secret.json"
SCOPES = ['https://www.googleapis.com/auth/userinfo.email', 'https://www.googleapis.com/auth/userinfo.profile', 'openid']


# pylint: disable=C0301

class LoginViewSet(viewsets.ViewSet):
    """Login"""

    @staticmethod
    def login(request):
        """Log in.
        Uses the `code` and `redir` query parameters."""

        # Check if we have the auth code
        auth_code = request.GET.get('code')
        if auth_code is None:
            return Response({"message": "{?code} is required"}, status=400)

        # Check we have redir param
        redir = request.GET.get('redir')
        if redir is None:
            return Response({"message": "{?redir} is required"}, status=400)

        return perform_login(auth_code, redir, request)

    @staticmethod
    def pass_login(request):
        """DANGEROUS: Password Log in.
        Uses the `username` and `password` query parameters."""

        # Check if we have the username
        username = request.GET.get('username')
        if username is None:
            return Response({"message": "{?username} is required"}, status=400)

        # Check if we have the password
        password = request.GET.get('password')
        if password is None:
            return Response({"message": "{?password} is required"}, status=400)

        # Make a new session
        session = requests.Session()

        # Get constants
        URL = settings.SSO_LOGIN_URL
        REDIR = settings.SSO_DEFAULT_REDIR

        # Get a CSRF token and update referer
        response = session.get(URL, verify=not settings.SSO_BAD_CERT)
        csrf = response.cookies['csrftoken']
        session.headers.update({'referer': URL})

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
            csrf = response.cookies['csrftoken']

            # Grant all SSO permissions
            data = {
                "csrfmiddlewaretoken": csrf,
                "redirect_uri": REDIR,
                "scope": "basic profile picture ldap sex phone program secondary_emails insti_address",
                "client_id": settings.SSO_CLIENT_ID,
                "state": "",
                "response_type": "code",
                "scopes_array": [
                    "profile", "picture", "ldap", "sex", "phone",
                    "program", "secondary_emails", "insti_address"
                ],
                "allow": "Authorize"
            }
            response = session.post(response.url, data, verify=not settings.SSO_BAD_CERT)

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
            queryset = UserProfileFullSerializer.setup_eager_loading(UserProfile.objects)
            user_profile = queryset.get(user=request.user)
            profile_serialized = UserProfileFullSerializer(
                user_profile, context={'request': request})
        except UserProfile.DoesNotExist:
            return Response({'message': "UserProfile doesn't exist"}, status=500)

        # Count this as a ping
        user_profile.last_ping = timezone.now()
        user_profile.save(update_fields=['last_ping'])

        # Return the details and nested profile
        return Response({
            'sessionid': request.session.session_key,
            'user': request.user.username,
            'profile_id': user_profile.id,
            'profile': profile_serialized.data
        })

    @staticmethod
    def g_login(request):

        # Check if we have the auth code
        auth_code = request.GET.get('code')
        if auth_code is None:
            return Response({"message": "{?code} is required"}, status=400)

        # Check we have redir param
        redir = request.GET.get('redir')
        if redir is None:
            return Response({"message": "{?redir} is required"}, status=400)

        import os
        os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
        flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
            CLIENT_SECRETS_FILE, scopes=SCOPES)
        flow.redirect_uri = 'http://localhost:4200/glogin'

        # Use the authorization server's response to fetch the OAuth 2.0 tokens.
        flow.fetch_token(authorization_response=request.get_full_path())

        # Store credentials in the session.
        # ACTION ITEM: In a production app, you likely want to save these
        #              credentials in a persistent database instead.
        credentials = flow.credentials

        userinfo_req = requests.post('https://www.googleapis.com/oauth2/v3/userinfo',
            params={'access_token': credentials.token},
            headers = {'content-type': 'application/json'})

        userinfo = userinfo_req.json()
        print(userinfo['name'], userinfo['email'])

        name = str(userinfo['name'])
        email = str(userinfo['email'])

        return perform_google_login(name, email, request)

    @staticmethod
    def logout(request):
        """Log out."""

        logout(request)
        return Response({'message': 'logged out'})
