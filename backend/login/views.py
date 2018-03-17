"""Login Viewset"""
import requests
from rest_framework import viewsets
from rest_framework.response import Response
from django.http import HttpResponse
from django.contrib.auth.models import User
from users.models import UserProfile
from users.serializers import UserProfileFullSerializer

class LoginViewSet(viewsets.ViewSet): 
    def login(self, request):
        auth_code = request.GET.get('code')
        if auth_code is None:
            return HttpResponse(status=400, content="{?code} is required")
        post_data = 'code=' + auth_code  + '&redirect_uri=http://localhost:8000/go&grant_type=authorization_code'

        response = requests.post(
            'https://gymkhana.iitb.ac.in/sso/oauth/token/',
            data=post_data,
            headers={
                "Authorization": "Basic dlIxcFU3d1hXeXZlMXJVa2cwZk1TNlN0TDFLcjZwYW9TbVJJaUxYSjpaR2J6cHR2dXlVZmh1d3NVWHZqdXJRSEhjMU51WXFmbDJrSjRmSm90YWhyc2tuYklxa2o1NUNKdDc0UktQMllwaXlabHpXaGVZWXNiNGpKVG1RMFVEZUU4M1B6bVViNzRaUjJCakhhYkVqWVJPVEwxSnIxY1ZwTWdZTzFiOWpPWQ==",
                "Content-Type": "application/x-www-form-urlencoded"
            })
        response_json = response.json()

        if not 'access_token' in response_json:
            print(response.content)
            if 'error' in response_json:
                return HttpResponse(status=400, content=response_json['error'])
            return HttpResponse(status=400, content='Getting auth token failed')

        profile_response = requests.get(
            'https://gymkhana.iitb.ac.in/sso/user/api/user/?fields=first_name,last_name,type,profile_picture,sex,username,email,program,contacts,insti_address,secondary_emails,mobile,roll_number',
            headers={
                "Authorization": "Bearer " + response_json['access_token'],
            })
        profile_json = profile_response.json()

        print(profile_response.content)

        if not 'id' in profile_json:
            if 'error' in profile_response:
                return HttpResponse(status=400, content=profile_response['error'])
            return HttpResponse(status=400, content='Getting profile failed')

        username = str(profile_json['id'])

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            user = User.objects.create_user(username)

        try:
            user_profile = UserProfile.objects.get(user=user)
        except UserProfile.DoesNotExist:
            user_profile = UserProfile.objects.create(user=user, name='iitbuser')

        for response_key, data_key in {
                'first_name': 'name',
                'email': 'email',
                'mobile': 'contact_no',
                'roll_number': 'roll_no'}.items():

            if response_key in profile_json:
                setattr(user_profile, data_key, profile_json[response_key])

        if 'first_name' in profile_json and 'last_name' in profile_json:
            user_profile.name = profile_json['first_name'] + ' ' + profile_json['last_name']

        if 'contacts' in profile_json and profile_json['contacts']:
            user_profile.contact_no = profile_json['contacts'][0]['number']

        if 'profile_picture' in profile_json:
            user_profile.profile_pic = 'https://gymkhana.iitb.ac.in' + profile_json['profile_picture']

        user_profile.save()

        request.session['username'] = username

        return Response({
            'sessionid': request.session.session_key,
            'user': user.username,
            'profile_id': user_profile.id
        })

    def get_user(self, request):
        if 'username' in request.session:
            username = request.session['username']
        else:
            return HttpResponse(status=401, content="Not logged in")

        try:
            user_profile = UserProfile.objects.get(user__username=username)
            profile_serialized = UserProfileFullSerializer(user_profile)
        except UserProfile.DoesNotExist:
            return HttpResponse(status=500, content="UserProfile doesn't exist")

        return Response({
            'sessionid': request.session.session_key,
            'user': username,
            'profile_id': user_profile.id,
            'profile': profile_serialized.data
        })

    def logout(self, request):
        try:
            del request.session['username']
        except KeyError:
            pass
        return HttpResponse('Logged out successfully')
