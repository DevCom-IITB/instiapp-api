from rest_framework import viewsets
from rest_framework.response import Response
from django.shortcuts import render
from django.contrib.auth.models import User

class LoginViewSet(viewsets.ViewSet): 
    def go(self, request):
        return Response({'count':  request.GET.get('code')})
