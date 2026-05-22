from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

app = Celery("backend")

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

# Initialize Firebase Admin SDK
try:
    from firebase_admin import credentials, initialize_app
    cred_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if cred_path:
        initialize_app(credentials.Certificate(cred_path))
except Exception as ex:
    print("Firebase Admin init skipped/failed:", ex)


#update the current configurations
app.conf.update(
  result_backend='redis://localhost:6379/1',
  task_track_started=True,
  task_queues = {
    'default':        {'exchange': 'default'},
    'resobin_sync':   {'exchange': 'resobin_sync'},   # ResoBin sync tasks
    'notifications':  {'exchange': 'notifications'},   # Push notification tasks
    'stream_consumer':{'exchange': 'stream_consumer'}, # Redis stream consumer (concurrency=1)
    'cache_fanout':   {'exchange': 'cache_fanout'},    # Body event cache invalidation
   },

  task_routes = {
    'calendarhub.tasks.sync_resobin_for_user':     {'queue': 'resobin_sync'},
    'calendarhub.tasks.send_event_reminder':       {'queue': 'notifications'},
    'calendarhub.tasks.send_change_notification':  {'queue': 'notifications'},
    'calendarhub.tasks.consume_resobin_stream':    {'queue': 'stream_consumer'},
    'calendarhub.tasks.invalidate_followers_cache':{'queue': 'cache_fanout'},
  },
)


@app.task(bind=True)
def debug_task(self):  # pragma: no cover
    print("Request: {0!r}".format(self.request))
