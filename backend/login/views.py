"""Login Viewset."""
import requests
from django.shortcuts import redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from rest_framework import viewsets
from rest_framework.response import Response
from users.models import UserProfile
from users.serializers import UserProfileFullSerializer

# pylint: disable=C0301

# Note: These are dummies
HOST = 'http://localhost:8000/'
CLIENT_ID = 'vR1pU7wXWyve1rUkg0fMS6StL1Kr6paoSmRIiLXJ'
CLIENT_ID_SECRET_BASE64 = 'dlIxcFU3d1hXeXZlMXJVa2cwZk1TNlN0TDFLcjZwYW9TbVJJaUxYSjpaR2J6cHR2dXlVZmh1d3NVWHZqdXJRSEhjMU51WXFmbDJrSjRmSm90YWhyc2tuYklxa2o1NUNKdDc0UktQMllwaXlabHpXaGVZWXNiNGpKVG1RMFVEZUU4M1B6bVViNzRaUjJCakhhYkVqWVJPVEwxSnIxY1ZwTWdZTzFiOWpPWQ=='

class LoginViewSet(viewsets.ViewSet):
    """Viewset to handle logging in and out, and getting the current user's profile."""

    @classmethod
    def login_page(cls, request):   # pylint: disable=W0613
        """Temporary method to redirect to login page."""
        return redirect('https://gymkhana.iitb.ac.in/sso/oauth/authorize/?client_id=' + CLIENT_ID + '&response_type=code&scope=basic profile picture sex ldap phone insti_address program secondary_emails&redirect_uri=' + HOST + 'api/login')

    @classmethod
    def login(cls, request):
        """Logs in the user using the {?code} query parameter"""

        # Check if we have the auth code
        auth_code = request.GET.get('code')
        if auth_code is None:
            return HttpResponse(status=400, content="{?code} is required")

        # Construt post data to get token
        post_data = 'code=' + auth_code + '&redirect_uri=' + HOST + 'api/login&grant_type=authorization_code'

        # Get our access token
        response = requests.post(
            'https://gymkhana.iitb.ac.in/sso/oauth/token/',
            data=post_data,
            headers={
                "Authorization": "Basic " + CLIENT_ID_SECRET_BASE64,
                "Content-Type": "application/x-www-form-urlencoded"
            }, verify=False)
        response_json = response.json()

        # Check that we have the access token
        if not 'access_token' in response_json:
            print(response.content)
            if 'error' in response_json:
                return HttpResponse(status=400, content=response_json['error'])
            return HttpResponse(status=400, content='Getting auth token failed')

        # Get the user's profile
        profile_response = requests.get(
            'https://gymkhana.iitb.ac.in/sso/user/api/user/?fields=first_name,last_name,type,profile_picture,sex,username,email,program,contacts,insti_address,secondary_emails,mobile,roll_number',
            headers={
                "Authorization": "Bearer " + response_json['access_token'],
            }, verify=False)
        profile_json = profile_response.json()

        # Print the profile for debugging
        print(profile_response.content)

        # Check if we got at least the user's SSO id
        if not 'id' in profile_json:
            if 'error' in profile_response:
                return HttpResponse(status=400, content=profile_response['error'])
            return HttpResponse(status=400, content='Getting profile failed')

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

        # Fill in data into the profile from SSO
        for response_key, data_key in {
                'first_name': 'name',
                'email': 'email',
                'mobile': 'contact_no',
                'roll_number': 'roll_no'}.items():

            if response_key in profile_json:
                setattr(user_profile, data_key, profile_json[response_key])

        # Fill in some special parameters
        if 'first_name' in profile_json and 'last_name' in profile_json:
            user_profile.name = profile_json['first_name'] + ' ' + profile_json['last_name']

        if 'contacts' in profile_json and profile_json['contacts']:
            user_profile.contact_no = profile_json['contacts'][0]['number']

        if 'profile_picture' in profile_json:
            user_profile.profile_pic = 'https://gymkhana.iitb.ac.in' + profile_json['profile_picture']

        # Save the profile
        user_profile.save()

        # Log in the user
        request.session['username'] = username
        request.session.save()

        # Return the session id
        return Response({
            'sessionid': request.session.session_key,
            'user': user.username,
            'profile_id': user_profile.id,
            'profile': UserProfileFullSerializer(user_profile).data
        })

    @classmethod
    def get_user(cls, request):
        """Get the session and user's profile."""

        # Check if the user is logged in
        if 'username' in request.session:
            username = request.session['username']
        else:
            return HttpResponse(status=401, content="Not logged in")

        # Check if the user has a profile
        try:
            user_profile = UserProfile.objects.get(user__username=username)
            profile_serialized = UserProfileFullSerializer(user_profile)
        except UserProfile.DoesNotExist:
            return HttpResponse(status=500, content="UserProfile doesn't exist")

        # Return the details and nested profile
        return Response({
            'sessionid': request.session.session_key,
            'user': username,
            'profile_id': user_profile.id,
            'profile': profile_serialized.data
        })

    @classmethod
    def logout(cls, request):
        """Log out the user."""

        # Delete the session key if we can
        try:
            del request.session['username']
        except KeyError:
            pass
        return HttpResponse('Logged out successfully')
