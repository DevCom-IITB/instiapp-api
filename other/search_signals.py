from django.conf import settings
from django.db.models.signals import post_save

from other.search import push_obj_sync
from helpers.celery import shared_task_conditional
from helpers.celery import FaultTolerantTask

from bodies.models import Body
from events.models import Event
from users.models import UserProfile
from placements.models import BlogEntry
from news.models import NewsEntry

model_classes = (Body, Event, UserProfile, BlogEntry, NewsEntry)

@shared_task_conditional(base=FaultTolerantTask)
def update_index(typ, pk):  # pragma: no cover
    """Notify users about event creation."""

    types = {m.__name__: m for m in model_classes}
    instance = types[typ].objects.filter(id=pk).first()
    if not instance:
        return

    push_obj_sync(instance)

def model_saved(instance, created, **kwargs):  # pylint: disable=unused-argument
    """Update the FTS entry through celery."""

    update_index.delay(type(instance).__name__, instance.id)


if settings.USE_SONIC:
    for model in model_classes:
        post_save.connect(model_saved, sender=model)
