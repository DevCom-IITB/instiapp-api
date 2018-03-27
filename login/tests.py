# from django.test import TestCase
from django.contrib.auth.models import User
from users.models import UserProfile

def get_new_user():
    user = User.objects.create(username="TestUser")
    UserProfile.objects.create(name="TestUserProfile", user=user)
    return user
