"""Login Viewset."""
import requests
from django.shortcuts import redirect
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.contrib.auth import logout
from rest_framework import viewsets
from rest_framework.response import Response
from login.helpers import fill_models_from_sso
from users.models import UserProfile
from users.serializers import UserProfileFullSerializer

# pylint: disable=C0301

class LoginViewSet(viewsets.ViewSet):
    """Viewset to handle logging in and out, and getting the current user's profile."""

    @staticmethod
    def login_page(request):   # pylint: disable=W0613
        """Temporary method to redirect to login page."""
        return redirect('https://gymkhana.iitb.ac.in/sso/oauth/authorize/?client_id=' + settings.SSO_CLIENT_ID + '&response_type=code&scope=basic profile picture sex ldap phone insti_address program secondary_emails&redirect_uri=' + settings.HOST_FOR_SSO + 'api/login')

    @staticmethod
    def login(request):
        """Logs in the user using the {?code} query parameter"""

        # Check if we have the auth code
        auth_code = request.GET.get('code')
        if auth_code is None:
            return Response({"message" : "{?code} is required"}, status=400)

        # Construt post data to get token
        redir = request.GET.get('redir')
        if redir is None:
            post_data = 'code=' + auth_code + '&redirect_uri=' + settings.HOST_FOR_SSO + 'api/login&grant_type=authorization_code'
        else:
            post_data = 'code=' + auth_code + '&redirect_uri=' + redir + '&grant_type=authorization_code'

        # Get our access token
        response = requests.post(
            settings.SSO_TOKEN_URL,
            data=post_data,
            headers={
                "Authorization": "Basic " + settings.SSO_CLIENT_ID_SECRET_BASE64,
                "Content-Type": "application/x-www-form-urlencoded"
            }, verify=False)
        response_json = response.json()

        # Check that we have the access token
        if not 'access_token' in response_json:
            print(response.content)
            return Response(response_json, status=400)

        # Get the user's profile
        profile_response = requests.get(
            settings.SSO_PROFILE_URL,
            headers={
                "Authorization": "Bearer " + response_json['access_token'],
            }, verify=False)
        profile_json = profile_response.json()

        # Print the profile for debugging
        print(profile_response.content)

        # Check if we got at least the user's SSO id
        if not 'id' in profile_json:
            return Response(profile_response, status=400)

        username = str(profile_json['id'])

        # Check if the User exists, otherwise create a new object
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            user = User.objects.create_user(username)

        # Check if User has a profile and create if not
        try:
            user_profile = UserProfile.objects.get(user=user)
        except UserProfile.DoesNotExist:
            user_profile = UserProfile.objects.create(user=user, name='iitbuser')

        # Fill models with new data
        fill_models_from_sso(user_profile, user, profile_json)

        # Log in the user
        login(request, user)
        request.session.save()

        # Return the session id
        return Response({
            'sessionid': request.session.session_key,
            'user': user.username,
            'profile_id': user_profile.id,
            'profile': UserProfileFullSerializer(user_profile).data
        })

    @staticmethod
    def get_user(request):
        """Get the session and user's profile."""

        # Check if the user is authenticated
        if not request.user.is_authenticated:
            return Response({"message":"not logged in"}, status=401)

        # Check if the user has a profile
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            profile_serialized = UserProfileFullSerializer(user_profile)
        except UserProfile.DoesNotExist:
            return Response({'message': "UserProfile doesn't exist"}, status=500)

        # Return the details and nested profile
        return Response({
            'sessionid': request.session.session_key,
            'user': request.user.username,
            'profile_id': user_profile.id,
            'profile': profile_serialized.data
        })

    @staticmethod
    def logout(request):
        """Log out the user."""

        # Delete the session key if we can
        try:
            logout(request)
        except KeyError:
            pass
        return Response({'message': 'logged out'})
