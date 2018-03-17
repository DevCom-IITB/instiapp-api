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
        post_data = 'code=' + request.GET.get('code') + '&redirect_uri=http://localhost:8000/go&grant_type=authorization_code'
        response = requests.post(
            'https://gymkhana.iitb.ac.in/sso/oauth/token/',
            data=post_data,
            headers={
                "Authorization": "Basic dlIxcFU3d1hXeXZlMXJVa2cwZk1TNlN0TDFLcjZwYW9TbVJJaUxYSjpaR2J6cHR2dXlVZmh1d3NVWHZqdXJRSEhjMU51WXFmbDJrSjRmSm90YWhyc2tuYklxa2o1NUNKdDc0UktQMllwaXlabHpXaGVZWXNiNGpKVG1RMFVEZUU4M1B6bVViNzRaUjJCakhhYkVqWVJPVEwxSnIxY1ZwTWdZTzFiOWpPWQ==",
                "Content-Type": "application/x-www-form-urlencoded"
            })
        response_json = response.json()

        profile_response = requests.get(
            'https://gymkhana.iitb.ac.in/sso/user/api/user/?fields=first_name,last_name,type,profile_picture,sex,username,email,program,contacts,insti_address,secondary_emails,mobile,roll_number',
            headers={
                "Authorization": "Bearer " + response_json['access_token'],
            })
        profile_json = profile_response.json()

        username = str(profile_json['id'])

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            user = User.objects.create_user(username)

        try:
            user_profile = UserProfile.objects.get(user=user)
        except UserProfile.DoesNotExist:
            user_profile = UserProfile.objects.create(user=user, name='iitbuser')

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
