"""Helpers for login functions."""
import requests
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.db.models import Q
from rest_framework.response import Response
from users.models import UserProfile
from users.serializer_full import UserProfileFullSerializer
from helpers.device import update_fcm_device

# pylint: disable=R0914
def perform_login(auth_code, redir, request):
    """Perform login with code and redir."""

    post_data = 'code=' + auth_code + '&redirect_uri=' + redir + '&grant_type=authorization_code'

    # Get our access token
    response = requests.post(
        settings.SSO_TOKEN_URL,
        data=post_data,
        headers={
            "Authorization": "Basic " + settings.SSO_CLIENT_ID_SECRET_BASE64,
            "Content-Type": "application/x-www-form-urlencoded"
        }, verify=not settings.SSO_BAD_CERT)
    response_json = response.json()

    # Check that we have the access token
    if 'access_token' not in response_json:
        return Response(response_json, status=400)

    # Get the user's profile
    profile_response = requests.get(
        settings.SSO_PROFILE_URL,
        headers={
            "Authorization": "Bearer " + response_json['access_token'],
        }, verify=not settings.SSO_BAD_CERT)
    profile_json = profile_response.json()

    # Check if we got at least the user's SSO id
    if 'id' not in profile_json:
        return Response(profile_response, status=400)

    # Check that we have basic details like name and roll no.
    required_fields = ['first_name', 'roll_number', 'username']
    if not all([((field in profile_json) and profile_json[field]) for field in required_fields]):
        return Response({'message': 'All required fields not present'}, status=403)

    username = str(profile_json['id'])
    roll_no = str(profile_json['roll_number'])

    # Check if a user exists with same username or roll number
    query = Q(username=username)
    if roll_no:
        query = query | Q(profile__roll_no=roll_no)
    user = User.objects.filter(query).first()

    # Create a new user if not found
    if not user:
        user = User.objects.create_user(username)

    # Set username again in case LDAP ID changed
    user.username = username

    # Check if User has a profile and create if not
    try:
        queryset = UserProfileFullSerializer.setup_eager_loading(UserProfile.objects)
        user_profile = queryset.get(user=user)
    except UserProfile.DoesNotExist:
        user_profile = UserProfile.objects.create(user=user, name='iitbuser')

    # Fill models with new data
    fill_models_from_sso(user_profile, user, profile_json)

    # Log in the user
    login(request, user)
    request.session.save()

    # Deprecated: update fcm id
    fcm_id = request.GET.get('fcm_id')
    if fcm_id is not None:
        update_fcm_device(request, fcm_id)

    # Return the session id
    return Response({
        'sessionid': request.session.session_key,
        'user': user.username,
        'profile_id': user_profile.id,
        'profile': UserProfileFullSerializer(
            user_profile, context={'request': request}).data
    })

def fill_models_from_sso(user_profile, user, profile_json):
    """Fill models from SSO data."""
    SSOFiller(user_profile, user, profile_json).fill().save()

class SSOFiller():
    """Helper class to fill user model from SSO."""

    def __init__(self, user_profile, user, profile_json):
        self.user_profile = user_profile
        self.user = user
        self.profile_json = profile_json

    def fill(self):
        self.fill_common()
        self.fill_name()
        self.oset('email')
        self.fill_contact()
        self.fill_profile_pic()
        self.fill_program()
        self.fill_insti_address()
        return self

    def save(self):
        self.user.save()
        self.user_profile.save()
        return self

    def fill_common(self):
        """Fill in common data into the profile from SSO. """
        for response_key, data_key in {
                'first_name': 'name',
                'email': 'email',
                'mobile': 'contact_no',
                'roll_number': 'roll_no',
                'username': 'ldap_id'
        }.items():
            self.oset(response_key, data_key)

    def fill_name(self):
        if self.jhas('first_name') and self.jhas('last_name'):
            self.user_profile.name = ('%s %s' % (self.jget('first_name'), self.jget('last_name'))).title()
            self.user.first_name = str(self.jget('first_name')).title()
            self.user.last_name = str(self.jget('last_name')).title()

    def fill_contact(self):
        if self.jhas('contacts') and self.jget('contacts'):
            self.user_profile.contact_no = self.jget('contacts')[0]['number']

    def fill_profile_pic(self):
        if self.jhas('profile_picture'):
            self.user_profile.profile_pic = 'https://gymkhana.iitb.ac.in' + self.jget('profile_picture')

    def fill_program(self):
        if self.jhas('program'):
            target = self.jget('program')
            self.oset('join_year', target=target)
            self.oset('department', target=target)
            self.oset('department_name', target=target)
            self.oset('degree', target=target)
            self.oset('degree_name', target=target)
            self.oset('graduation_year', target=target)

    def fill_insti_address(self):
        if self.jhas('insti_address'):
            target = self.jget('insti_address')
            self.oset('hostel', target=target)
            self.oset('room', target=target)

    def jhas(self, response_key, target=None):
        if not target:
            target = self.profile_json
        return response_key in target and target[response_key] is not None

    def jget(self, response_key):
        return self.profile_json[response_key]

    def oset(self, response_key, data_key=None, target=None):
        if data_key is None:
            data_key = response_key
        if not target:
            target = self.profile_json
        if self.jhas(response_key, target):
            setattr(self.user_profile, data_key, target[response_key])
