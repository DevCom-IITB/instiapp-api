"""Settings for test environment."""

# pylint: disable=W0401, W0614
import os
from backend.settings_base import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'lu3+xlyjj940k46e!h$wp#_l5^g4eb4zr(*a286=o6!@di8cbg'

BASE_URL = 'http://localhost:4200'
STATIC_BASE_URL = BASE_URL

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

SSO_TOKEN_URL = 'http://localhost:33000/CODE_TOKEN/'
SSO_PROFILE_URL = 'http://localhost:33000/PROFILE/'
SSO_CLIENT_ID = 'vR1pU7wXWyve1rUkg0fMS6StL1Kr6paoSmRIiLXJ'
SSO_CLIENT_ID_SECRET_BASE64 = 'dlIxcFU3d1hXeXZlMXJVa2cwZk1TNlN0TDFLcjZwYW9TbVJJaUxYSjpaR2J6cHR2dXlVZmh1d3NVWHZqdXJRSEhjMU51WXFmbDJrSjRmSm90YWhyc2tuYklxa2o1NUNKdDc0UktQMllwaXlabHpXaGVZWXNiNGpKVG1RMFVEZUU4M1B6bVViNzRaUjJCakhhYkVqWVJPVEwxSnIxY1ZwTWdZTzFiOWpPWQ=='

# Password Login
SSO_DEFAULT_REDIR = 'REDIRECT_URI'
SSO_LOGIN_URL = 'http://localhost:33000/SSO/?redir=' + SSO_DEFAULT_REDIR

MEDIA_ROOT = './upload/static/upload'
MEDIA_URL = '/static/upload/'

USER_AVATAR_URL = '/static/upload/useravatar.jpg'

# Placement blog URLs
PLACEMENTS_URL = 'http://localhost:33000/placementblog'
TRAINING_BLOG_URL = 'http://localhost:33000/trainingblog'
