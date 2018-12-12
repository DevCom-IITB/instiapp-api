"""Notifications Signals."""
from notifications.signals import notify
from rest_framework import serializers
from django.db.models.signals import post_save
from django.db.models.signals import m2m_changed

from events.models import Event
from events.serializers import EventSerializer
from news.models import NewsEntry
from news.serializers import NewsEntrySerializer
from placements.models import BlogEntry
from placements.serializers import BlogEntrySerializer
from venter.models import Comment
from venter.serializers import CommentSerializer

def notify_new_event(instance, action, **kwargs):  # pylint: disable=W0613
    """Notify users that a new event was added for a followed body."""
    if action == 'post_add' and isinstance(instance, Event):
        # Skip notification
        if not instance.notify:
            return

        # Notify all body followers
        for body in instance.bodies.prefetch_related('followers').all():
            for profile in body.followers.all():
                notify.send(
                    instance,
                    recipient=profile.user,
                    verb=body.name + " has added a new event"
                )

def notify_upd_event(instance):
    """Notify users that a followed event was updated."""
    # Skip notification
    if not instance.notify:
        return

    # Notify all event followers
    for profile in instance.followers.all():
        notify.send(instance, recipient=profile.user, verb=instance.name + " was updated")

def event_saved(instance, created, **kwargs):  # pylint: disable=W0613
    """Notify users when an event changes."""
    if not created:
        notify_upd_event(instance)

def news_saved(instance, created, **kwargs):  # pylint: disable=W0613
    """Notify users when a followed body adds new news."""
    if created and instance.body:
        for profile in instance.body.followers.all():
            notify.send(instance, recipient=profile.user, verb=instance.body.name + " added a new news article")

def new_comment(instance, created, **kwargs):  # pylint: disable=W0613
    """Notify users when a followed complaint gets a new comment."""
    if created:
        # Preventing the user who commented from being notified about their own comment
        for profile in instance.complaint.subscriptions.all().exclude(id=instance.commented_by.id):
            notify.send(instance, recipient=profile.user, verb="New comment on a complaint you're following")

class GenericNotificationRelatedField(serializers.RelatedField):  # pylint: disable=W0223
    """Serializer for actor/target of notifications."""
    def to_representation(self, value):
        if isinstance(value, Event):
            serializer = EventSerializer(value)
        elif isinstance(value, NewsEntry):
            serializer = NewsEntrySerializer(value)
        elif isinstance(value, BlogEntry):
            serializer = BlogEntrySerializer(value)
        elif isinstance(value, Comment):
            serializer = CommentSerializer(value)

        return serializer.data

class NotificationSerializer(serializers.Serializer):  # pylint: disable=W0223
    """Notification Serializer, with unread and actor"""
    id = serializers.IntegerField()
    verb = serializers.ReadOnlyField(read_only=True)
    unread = serializers.BooleanField(read_only=True)
    actor = GenericNotificationRelatedField(read_only=True)
    actor_type = serializers.SerializerMethodField()

    @staticmethod
    def get_actor_type(obj):
        """Get the class name of actor."""
        return obj.actor.__class__.__name__.lower()


post_save.connect(event_saved, sender=Event)
m2m_changed.connect(notify_new_event, sender=Event.bodies.through)
post_save.connect(news_saved, sender=NewsEntry)
post_save.connect(new_comment, sender=Comment)
