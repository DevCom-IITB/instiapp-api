"""
Django settings for backend project.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""
import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',

    'rest_framework',
    'drf_yasg',

    'achievements.apps.AchievementsConfig',
    'events.apps.EventsConfig',
    'locations.apps.LocationsConfig',
    'users.apps.UsersConfig',
    'bodies.apps.BodiesConfig',
    'upload.apps.UploadConfig',
    'roles.apps.RolesConfig',
    'placements.apps.PlacementsConfig',
    'news.apps.NewsConfig',
    'messmenu.apps.MessmenuConfig',
    'other.apps.OtherConfig',
    'venter.apps.VenterConfig',

    'notifications',
    'markdownify',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    #'django.middleware.csrf.CsrfViewMiddleware',
    'backend.middle.DisableCSRFMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['./prerender/templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'backend.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Kolkata'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/

STATIC_URL = '/static/'

# Settings for Django REST Framework
REST_FRAMEWORK = {}

# Sonic FTS address
SONIC_CONFIG = {
    "host": '127.0.0.1',
    "port": 1491,
    "password": 'SecretPassword',
    "max_connections": 10
}
USE_SONIC = False
SONIC_MAX_LEN = 1024

# Do not delete notifications records from database
DJANGO_NOTIFICATIONS_CONFIG = {'SOFT_DELETE': True}

# Prerender configuration
PRERENDER_TITLE = 'InstiApp | IIT Bombay'
PRERENDER_DESCRIPTION = 'InstiApp is the front page of all student activities at IIT Bombay'
LOGO_URL = 'https://insti.app/assets/logo.png'

# Placement blog URLs
PLACEMENTS_URL = 'http://placements.iitb.ac.in/blog/?feed=rss2'
TRAINING_BLOG_URL = 'http://placements.iitb.ac.in/trainingblog/?feed=rss2'

# Names of bodies to notify when there are new posts on placement/training blog
PLACEMENTS_BLOG_BODY = 'Placement Blog'
TRAINING_BLOG_BODY = 'Internship Blog'

# Authentication for chores
LDAP_USERNAME = None
LDAP_PASSWORD = None

if 'LDAP_USERNAME' in os.environ and 'LDAP_PASSWORD' in os.environ:
    LDAP_USERNAME = os.environ['LDAP_USERNAME']
    LDAP_PASSWORD = os.environ['LDAP_PASSWORD']
    print('INFO: LDAP username and password present in environment.')

# Flip for broken external server certificates
SSO_BAD_CERT = False

# Default icons for notifications
NOTIFICATION_LARGE_ICON_DEFAULT = 'assets/logo.png'

# Optional deployment dependent transforms
USER_PROFILE_SERIALIZER_TRANSFORM = lambda x: x
USER_PROFILE_FULL_SERIALIZER_TRANSFORM = lambda x: x
NOTIFICATION_LARGE_ICON_TRANSFORM = lambda x: x
NOTIFICATION_IMAGE_TRANSFORM = lambda x: x
YOUTUBE_THUMB = lambda x: 'https://img.youtube.com/vi/%s/mqdefault.jpg' % x

# Set this to False to actually use Celery
NO_CELERY = os.environ.get('NO_CELERY') != 'false'

# Number of seconds to count down
CELERY_DELAY = 0

DEFAULT_FROM_EMAIL = 'webmaster@localhost'

COMPLAINT_AUTO_SUBSCRIBE = True
