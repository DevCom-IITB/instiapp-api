"""Settings for test environment."""

# pylint: disable=W0401, W0614
from backend.settings_base import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'lu3+xlyjj940k46e!h$wp#_l5^g4eb4zr(*a286=o6!@di8cbg'

BASE_URL = 'http://localhost:4200'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

SSO_TOKEN_URL = 'http://localhost/CODE_TOKEN/'
SSO_PROFILE_URL = 'http://localhost'
HOST_FOR_SSO = 'http://localhost:8000/'
SSO_CLIENT_ID = 'vR1pU7wXWyve1rUkg0fMS6StL1Kr6paoSmRIiLXJ'
SSO_CLIENT_ID_SECRET_BASE64 = 'dlIxcFU3d1hXeXZlMXJVa2cwZk1TNlN0TDFLcjZwYW9TbVJJaUxYSjpaR2J6cHR2dXlVZmh1d3NVWHZqdXJRSEhjMU51WXFmbDJrSjRmSm90YWhyc2tuYklxa2o1NUNKdDc0UktQMllwaXlabHpXaGVZWXNiNGpKVG1RMFVEZUU4M1B6bVViNzRaUjJCakhhYkVqWVJPVEwxSnIxY1ZwTWdZTzFiOWpPWQ=='

MEDIA_ROOT = './upload/static/upload'
MEDIA_URL = 'http://localhost:8000/static/upload/'

USER_AVATAR_URL = '/static/upload/useravatar.jpg'
