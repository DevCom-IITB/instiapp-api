"""Settings for full-test (CircleCI) environment."""

# pylint: disable=W0401, W0614
import os
from backend.settings_test import *

NO_CELERY = False
USE_SONIC = True

# Use postgres for tests as celery is not disabled
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'test_instiapp',
        'USER': 'postgres',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': os.environ.get('PGPORT', '5432'),
        'TEST': {
            'NAME': 'test_instiapp',
        },
    }
}
