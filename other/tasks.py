from __future__ import absolute_import, unicode_literals
from celery import shared_task
from django.contrib.auth.models import User
from notifications.signals import notify
from events.models import Event
from helpers.celery_fault import FaultTolerantTask

@shared_task(base=FaultTolerantTask)
def notify_new_event(pk):
    """Notify users about event creation."""
    instance = Event.objects.filter(id=pk).first()
    if not instance:
        return

    for body in instance.bodies.all():
        users = User.objects.filter(id__in=body.followers.values('user_id'))
        notify.send(
            instance,
            recipient=users,
            verb=body.name + " has added a new event"
        )

@shared_task(base=FaultTolerantTask)
def notify_upd_event(pk):
    """Notify users about event updation."""
    instance = Event.objects.filter(id=pk).first()
    if not instance:
        return

    users = User.objects.filter(id__in=instance.followers.values('user_id'))
    notify.send(instance, recipient=users, verb=instance.name + " was updated")
