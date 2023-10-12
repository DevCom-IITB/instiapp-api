"""Settings for full-test (mysql) environment."""

# pylint: disable=W0401, W0614
from backend.settings_test import *

NO_CELERY = False
USE_SONIC = True

# Use postgres for tests as celery is not disabled
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "test_instiapp",
        "USER": "root",
        "PASSWORD": "root",
        "HOST": "127.0.0.1",
        "PORT": 3306,
        "TEST": {
            "NAME": "test_instiapp",
        },
    }
}
