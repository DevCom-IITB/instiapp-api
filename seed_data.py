import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

token_key = "7cpjt6dunjp9nn6ldxigrnf7lcc4ifgn"
try:
    token = Token.objects.get(key=token_key)
    print(f"Found user: {token.user.username}")
except Token.DoesNotExist:
    print("Token not found in the database. Please check the token.")
except Exception as e:
    print(f"Error: {e}")
