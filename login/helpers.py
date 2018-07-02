"""Helpers for login functions."""
import requests
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth import login
from rest_framework.response import Response
from users.models import UserProfile
from users.serializer_full import UserProfileFullSerializer

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
    if not 'access_token' in response_json:
        return Response(response_json, status=400)

    # Get the user's profile
    profile_response = requests.get(
        settings.SSO_PROFILE_URL,
        headers={
            "Authorization": "Bearer " + response_json['access_token'],
        }, verify=not settings.SSO_BAD_CERT)
    profile_json = profile_response.json()

    # Check if we got at least the user's SSO id
    if not 'id' in profile_json:
        return Response(profile_response, status=400)

    # Check that we have basic details like name and roll no.
    required_fields = ['first_name', 'roll_number']
    if not all([(field in profile_json) for field in required_fields]):
        return Response({'message': 'Name and roll_number not present'}, status=403)

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

    fcm_id = request.GET.get('fcm_id')
    if fcm_id is not None:
        user_profile.fcm_id = fcm_id
        user_profile.save()

    # Log in the user
    login(request, user)
    request.session.save()

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

    # Fill in data into the profile from SSO
    for response_key, data_key in {
            'first_name': 'name',
            'email': 'email',
            'mobile': 'contact_no',
            'roll_number': 'roll_no',
            'username': 'ldap_id'}.items():

        if response_key in profile_json and profile_json[response_key] is not None:
            setattr(user_profile, data_key, profile_json[response_key])

    # Fill in some special parameters
    if 'first_name' in profile_json and 'last_name' in profile_json:
        if profile_json['first_name'] is not None and profile_json['last_name'] is not None:
            user_profile.name = profile_json['first_name'] + ' ' + profile_json['last_name']
            user.first_name = profile_json['first_name']
            user.last_name = profile_json['last_name']

    if 'email' in profile_json:
        if profile_json['email'] is not None:
            user.email = profile_json['email']

    if 'contacts' in profile_json and profile_json['contacts']:
        user_profile.contact_no = profile_json['contacts'][0]['number']

    if 'profile_picture' in profile_json:
        if profile_json['profile_picture'] is not None:
            user_profile.profile_pic = 'https://gymkhana.iitb.ac.in' + profile_json['profile_picture']

    # Fill in program details
    if 'program' in profile_json:
        for field in [
            'join_year',
            'department',
            'department_name',
            'degree',
            'degree_name',
            'graduation_year']:

            if profile_json['program'][field] is not None:
                setattr(user_profile, field, profile_json['program'][field])

    if 'insti_address' in profile_json:
        if profile_json['insti_address']['room'] is not None and profile_json['insti_address']['hostel'] is not None:
            user_profile.hostel = profile_json['insti_address']['hostel']
            user_profile.room = (profile_json['insti_address']['room'])



    # Save the profile
    user.save()
    user_profile.save()
