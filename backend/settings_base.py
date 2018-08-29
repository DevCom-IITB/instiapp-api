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

    'rest_framework',
    'rest_framework_swagger',

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
    'venter',
    'notifications',
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

REST_FRAMEWORK = {

}

PRERENDER_TITLE = 'InstiApp'
PRERENDER_DESCRIPTION = 'InstiApp | IIT Bombay'
LOGO_URL = 'https://insti.app/assets/logo.png'

PLACEMENTS_URL = 'http://placements.iitb.ac.in/blog/?feed=rss2'
TRAINING_BLOG_URL = 'http://placements.iitb.ac.in/trainingblog/?feed=rss2'

PLACEMENTS_BLOG_BODY = 'Placement Blog'
TRAINING_BLOG_BODY = 'Internship Blog'

LDAP_USERNAME = None
LDAP_PASSWORD = None

if 'LDAP_USERNAME' in os.environ and 'LDAP_PASSWORD' in os.environ:
    LDAP_USERNAME = os.environ['LDAP_USERNAME']
    LDAP_PASSWORD = os.environ['LDAP_PASSWORD']
    print('INFO: LDAP username and password present in environment.')

SSO_BAD_CERT = False
