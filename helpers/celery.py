from django.db import connection
from django.conf import settings
from celery import Task
from celery import shared_task

# pylint: disable=W0223

class FaultTolerantTask(Task):  # pragma: no cover
    """ Implements after return hook to close the invalid connection.
    This way, django is forced to serve a new connection for the next
    task.
    """
    abstract = True

    def after_return(self, *args, **kwargs):
        connection.close()


def shared_task_conditional(**kwargs):
    """Decorator to optionally disable celery tests."""
    def decorator(func):
        if settings.NO_CELERY:
            setattr(func, 'delay', func)
            return func
        return shared_task(func, **kwargs)
    return decorator
