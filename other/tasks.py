from __future__ import absolute_import, unicode_literals
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from notifications.models import Notification
from notifications.signals import notify
from pyfcm import FCMNotification
from achievements.models import UserInterest
from community.models import CommunityPost, CommunityPostUserReaction
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
        users = User.objects.filter(
            id__in=body.followers.filter(active=True).values("user_id")
        )
        notify.send(
            instance, recipient=users, verb=body.name + " has added a new event"
        )

    for interest in instance.event_interest.all():
        users = User.objects.filter(
            id__in=UserInterest.filter(title=interest.title)
            .user.filter(active=True)
            .values("user_id")
        )
        notify.send(
            instance,
            recipient=users,
            verb=f"A new event with tag {interest.title} has been added",
        )


@shared_task_conditional(base=FaultTolerantTask)
def notify_upd_event(pk):
    """Notify users about event updation."""
    setUp()
    instance = Event.objects.filter(id=pk).first()
    if not instance:
        return

    users = User.objects.filter(
        id__in=instance.followers.filter(active=True).values("user_id")
    )
    notify.send(instance, recipient=users, verb=instance.name + " was updated")


@shared_task_conditional(base=FaultTolerantTask)
def notify_new_commpost(pk):
    """Notify users about post creation."""
    setUp()
    instance = CommunityPost.objects.filter(id=pk).first()
    if not instance:
        return

    community = instance.community
    body = community.body
    users = User.objects.filter(
        id__in=body.followers.filter(active=True).values("user_id")
    )
    notify.send(instance, recipient=users, verb="New post added in " + community.name)

    for interest in instance.interests.all():
        users = (
            User.objects.filter(
                id__in=UserInterest.objects.filter(title=interest.title)
            )
            .filter(is_active=True)
            .values("id")
        )

        notify.send(
            instance,
            recipient=users,
            verb=f"New post with tag {interest.title} added in {community.name}",
        )


@shared_task_conditional(base=FaultTolerantTask)
def notify_new_comm(pk):
    """Notify users about event creation."""
    setUp()
    instance = CommunityPost.objects.filter(id=pk).first()
    if not instance:
        return

    commented_user = instance.posted_by
    users = []
    while instance.thread_rank > 1:
        instance = instance.parent
        users.append(instance.posted_by.user)
    notify.send(
        instance,
        recipient=users,
        verb=commented_user.name + " commented to your post " + instance.content,
    )


@shared_task_conditional(base=FaultTolerantTask)
def notify_new_commpostadmin(pk):
    """Notify users about event creation."""
    setUp()
    instance = CommunityPost.objects.filter(id=pk).first()
    if not instance:
        return

    community = instance.community
    roles = instance.community.body.roles.all()
    users = []
    for role in roles:
        if "AppP" in role.permissions:
            users.extend(map(lambda user: user.user, role.users.all()))
    print(users)
    notify.send(
        instance,
        recipient=users,
        verb="New post added for verification in " + community.name,
    )


@shared_task_conditional(base=FaultTolerantTask)
def notify_new_reaction(pk):
    """Notify user about new reaction to his post/comment"""
    setUp()
    instance = CommunityPostUserReaction.objects.filter(id=pk).first()
    if not instance:
        return

    user = [instance.communitypost.posted_by.user]
    notify.send(
        instance,
        recipient=user,
        verb=instance.user.name
        + " reacted to you post "
        + instance.communitypost.content,
    )


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
    if not hasattr(settings, "FCM_SERVER_KEY"):
        return

    try:
        push_service = FCMNotification(api_key=settings.FCM_SERVER_KEY)
    except Exception:
        return

    # Send FCM push notification
    for device in profile.devices.all():
        send_notification_fcm(push_service, device, data_message)

    # For each web push subscription
    for subscription in profile.web_push_subscriptions.all():
        send_notification_webpush(subscription, data_message)
