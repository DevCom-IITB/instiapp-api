from django.test import TestCase
from django.contrib.auth.models import User
from django.contrib.auth import login
from users.models import UserProfile
from rest_framework.test import force_authenticate

def get_new_user():
    user = User.objects.create(username="TestUser")
    UserProfile.objects.create(name="TestUserProfile", user=user)
    return user
