from __future__ import absolute_import, unicode_literals
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from notifications.models import Notification
from notifications.signals import notify
from pyfcm import FCMNotification
from events.models import Event
from helpers.celery import shared_task_conditional
from helpers.celery import FaultTolerantTask

from helpers.fcm import send_notification_fcm
from helpers.fcm import get_rich_notification
from helpers.webpush import send_notification_webpush

def setUp():
    """Do initial setup for each async task"""
    # Clear ContentType caching during development and testing.
    if settings.DEBUG:
        ContentType.objects.clear_cache()


@shared_task_conditional(base=FaultTolerantTask)
def notify_new_event(pk):
    """Notify users about event creation."""
    setUp()
    instance = Event.objects.filter(id=pk).first()
    if not instance:
        return

    for body in instance.bodies.all():
        users = User.objects.filter(id__in=body.followers.filter(active=True).values('user_id'))
        notify.send(
            instance,
            recipient=users,
            verb=body.name + " has added a new event"
        )

@shared_task_conditional(base=FaultTolerantTask)
def notify_upd_event(pk):
    """Notify users about event updation."""
    setUp()
    instance = Event.objects.filter(id=pk).first()
    if not instance:
        return

    users = User.objects.filter(id__in=instance.followers.filter(active=True).values('user_id'))
    notify.send(instance, recipient=users, verb=instance.name + " was updated")

@shared_task_conditional(base=FaultTolerantTask)
def push_notify(pk):
    """Push notify a notification."""
    setUp()
    notification = Notification.objects.filter(id=pk).first()

    # Check invalid subscriptions
    if not notification or notification.emailed or not notification.actor:
        return

    # Get the user's profile
    profile = notification.recipient.profile

    # Check bad users
    if not profile:
        return

    # Stop the spam!
    notification.emailed = True
    notification.save()

    # Get rich notification
    data_message = get_rich_notification(notification)

    # Get the API endpoint
    if not hasattr(settings, 'FCM_SERVER_KEY'):
        return

    push_service = FCMNotification(api_key=settings.FCM_SERVER_KEY)

    # Send FCM push notification
    for device in profile.devices.all():
        send_notification_fcm(push_service, device, data_message)

    # For each web push subscription
    for subscription in profile.web_push_subscriptions.all():
        send_notification_webpush(subscription, data_message)
