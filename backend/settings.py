"""Settings for dev environment."""

# pylint: disable=W0401, W0614
from backend.settings_base import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "lu3+xlyjj940k46e!h$wp#_l5^g4eb4zr(*a286=o6!@di8cbg"

BASE_URL = "http://localhost:8000"
STATIC_BASE_URL = BASE_URL

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"]
CORS_ORIGIN_WHITELIST = [
    "https://www.insti.app",
    "https://api.insti.app",
    "https://gymkhana.iitb.ac.in",
    "http://10.105.177.175",
    "http://localhost:4200",
    "http://localhost:3000",
    "http://10.198.49.175",
    "http://10.195.160.191",
]
CORS_ALLOW_CREDENTIALS = True

LDAP_USERNAME = os.environ.get("LDAP_USERNAME", "")
LDAP_PASSWORD = os.environ.get("LDAP_PASSWORD", "")

# SSO Config
SSO_TOKEN_URL = "https://gymkhana.iitb.ac.in/profiles/oauth/token/"
SSO_PROFILE_URL = "https://gymkhana.iitb.ac.in/profiles/user/api/user/?fields=first_name,last_name,type,profile_picture,sex,username,email,program,contacts,insti_address,secondary_emails,mobile,roll_number"
SSO_CLIENT_ID = 'wcXeaPWFL4G3j2xA78JYEc3xZ6uZeoSwEW4xkbbx'
SSO_CLIENT_ID_SECRET_BASE64 = 'd2NYZWFQV0ZMNEczajJ4QTc4SllFYzN4WjZ1WmVvU3dFVzR4a2JieDp2NnV0eVNVM0I4cnYxd1pIWGVkNnU3aHBZdDkwV1hBeXlWQml5ejM2QjQyNUEyS0hjb29yNVVGQk1MbTJJakRhUkM2WlYwY3h4RGdWRU5FdHFYTTl0cW1LY3piYnZORTRPenFDNHhBckdCU1JMMUx6cXVjQnBCWTJ0OFVqOEZ3bA=='
# Password Login
SSO_DEFAULT_REDIR = "http://localhost:3000/login"
SSO_LOGIN_URL = (
    "https://gymkhana.iitb.ac.in/sso/account/login/?next=/profiles/oauth/authorize/%3Fclient_id%3DwcXeaPWFL4G3j2xA78JYEc3xZ6uZeoSwEW4xkbbx%26response_type%3Dcode%26scope%3Dbasic%2520profile%2520picture%2520sex%2520ldap%2520phone%2520insti_address%2520program%2520secondary_emails%26redirect_uri%3D"
    + SSO_DEFAULT_REDIR
)

MEDIA_ROOT = "./upload/static/upload"
MEDIA_URL = "http://localhost:8000/static/upload/"

USER_AVATAR_URL = "/static/upload/useravatar.jpg"

VAPID_PRIV_KEY = ""
FCM_SERVER_KEY = ""
MESSI_ACCESS_TOKEN = "Tolm_fRDkfoN5WMU4oUXWxNwmn1E0MmYlbeh1LA29cU="

# Change this to LOGGING to enable SQLite logging
NO_LOGGING = {
    "version": 1,
    "filters": {
        "require_debug_true": {
            "()": "django.utils.log.RequireDebugTrue",
        }
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "filters": ["require_debug_true"],
            "class": "logging.StreamHandler",
        }
    },
    "loggers": {
        "django.db.backends": {
            "level": "DEBUG",
            "handlers": ["console"],
        }
    },
}

# EMAIL settings
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = "587"
EMAIL_HOST_USER = "devcom.iitbombay@gmail.com"
EMAIL_HOST_PASSWORD = "ioui qriy jcpe ixjz"
EMAIL_EVENT_HOST_USER = ""
EMAIL_USE_TLS = True
RECIPIENT_LIST = ['amitmalakar887@gmail.com','harigovindraghunath@gmail.com']
CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True
AUTH_USER = EMAIL_HOST_USER
