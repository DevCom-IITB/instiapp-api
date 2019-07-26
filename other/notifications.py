"""Notifications Signals."""
from notifications.models import Notification
from notifications.signals import notify
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.db.models.signals import m2m_changed
import other.tasks as tasks
from events.models import Event
from news.models import NewsEntry
from venter.models import ComplaintComment

# pylint: disable=W0223,W0613

def notify_new_event(instance, action, **kwargs):
    """Notify users that a new event was added for a followed body."""
    if action == 'post_add' and isinstance(instance, Event):
        # Skip notification
        if not instance.notify:
            return

        # Notify all body followers
        tasks.notify_new_event.delay(instance.id)

def notify_upd_event(instance):
    """Notify users that a followed event was updated."""
    # Skip notification
    if not instance.notify:
        return

    # Notify all event followers
    tasks.notify_upd_event.delay(instance.id)

def event_saved(instance, created, **kwargs):
    """Notify users when an event changes."""
    if not created:
        notify_upd_event(instance)

def news_saved(instance, created, **kwargs):
    """Notify users when a followed body adds new news."""
    if created and instance.body and instance.notify:
        users = User.objects.filter(id__in=instance.body.followers.filter(active=True).values('user_id'))
        notify.send(instance, recipient=users, verb=instance.body.name + " added a new news article")

def new_comment(instance, created, **kwargs):
    """Notify users when a followed complaint gets a new comment."""
    if created:
        # Preventing the user who commented from being notified about their own comment
        profiles = instance.complaint.subscriptions.exclude(id=instance.commented_by.id)
        users = User.objects.filter(id__in=profiles.values('user_id'))
        notify.send(instance, recipient=users, verb="New comment on a complaint you're following")

def notification_saved(instance, created, **kwargs):
    """Queue up push notifications."""
    if created and not instance.emailed:
        tasks.push_notify.delay(instance.id)


post_save.connect(event_saved, sender=Event)
m2m_changed.connect(notify_new_event, sender=Event.bodies.through)
post_save.connect(news_saved, sender=NewsEntry)
post_save.connect(new_comment, sender=ComplaintComment)

post_save.connect(notification_saved, sender=Notification)
