from rest_framework import viewsets
from rest_framework.response import Response
from django.shortcuts import render
from django.contrib.auth.models import User
import requests

class LoginViewSet(viewsets.ViewSet): 
    def go(self, request):
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

        return Response({
            'response': response.content,
            'content': profile_response.content,
            'at':response_json['access_token'],
            'user': user.username
            })
