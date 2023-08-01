"""Settings for dev environment."""

# pylint: disable=W0401, W0614
from backend.settings_base import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'lu3+xlyjj940k46e!h$wp#_l5^g4eb4zr(*a286=o6!@di8cbg'

BASE_URL = 'http://localhost:8000'
STATIC_BASE_URL = BASE_URL

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']
CORS_ORIGIN_WHITELIST = ['https://www.insti.app', 'https://api.insti.app', 'https://gymkhana.iitb.ac.in', 'http://10.105.177.175', 'http://localhost:4200', 'http://10.198.49.175']
CORS_ALLOW_CREDENTIALS = True

# SSO Config
SSO_TOKEN_URL = 'https://gymkhana.iitb.ac.in/sso/oauth/token/'
SSO_PROFILE_URL = 'https://gymkhana.iitb.ac.in/sso/user/api/user/?fields=first_name,last_name,type,profile_picture,sex,username,email,program,contacts,insti_address,secondary_emails,mobile,roll_number'
SSO_CLIENT_ID = 'HeKlfCluQLxa5cG5c4yHYiAEFZynroiKwylpiwNV'
SSO_CLIENT_ID_SECRET_BASE64 = 'SGVLbGZDbHVRTHhhNWNHNWM0eUhZaUFFRlp5bnJvaUt3eWxwaXdOVjpYbDg4OHNaOWFhbVVmV1FMR0Y3SjI1MU5taUFYeHRtdzRtM3pHejJLUVQ1d3M0b3hTRGNCTnhSNWw4SXpYbHNDTVVWVHh3MUE0VXRnRU5YZ1FpWlFDZ1RUcERoVHFXeUZmckhLdDhadU5SQk9SY2Q3Z2ZmWjNXUzQ5bGxCMXNBUg=='

# Password Login
SSO_DEFAULT_REDIR = 'https://insti.app/login'
SSO_LOGIN_URL = 'https://gymkhana.iitb.ac.in/sso/account/login/?next=/sso/oauth/authorize/%3Fclient_id%3DvR1pU7wXWyve1rUkg0fMS6StL1Kr6paoSmRIiLXJ%26response_type%3Dcode%26scope%3Dbasic%2520profile%2520picture%2520sex%2520ldap%2520phone%2520insti_address%2520program%2520secondary_emails%26redirect_uri%3D' + SSO_DEFAULT_REDIR

MEDIA_ROOT = './upload/static/upload'
MEDIA_URL = 'http://localhost:8000/static/upload/'

USER_AVATAR_URL = '/static/upload/useravatar.jpg'

VAPID_PRIV_KEY = ""
FCM_SERVER_KEY = ""
MESSI_ACCESS_TOKEN = ""

# Change this to LOGGING to enable SQLite logging
NO_LOGGING = {
    'version': 1,
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
        }
    },
    'loggers': {
        'django.db.backends': {
            'level': 'DEBUG',
            'handlers': ['console'],
        }
    }
}

# EMAIL settings
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = '587'
EMAIL_HOST_USER = ''
EMAIL_USE_TLS = True
