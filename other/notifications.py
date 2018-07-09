"""Notifications Signals."""
from notifications.signals import notify
from rest_framework import serializers
from django.db.models.signals import post_save
from django.db.models.signals import m2m_changed

from events.models import Event
from events.serializers import EventSerializer

def notify_new_event(instance, action, **kwargs): # pylint: disable=W0613
    """Notify users that a new event was added for a followed body."""
    if action == 'post_add' and isinstance(instance, Event):
        for body in instance.bodies.prefetch_related('followers').all():
            for profile in body.followers.all():
                notify.send(
                    instance,
                    recipient=profile.user,
                    verb=body.name + " has added a new event"
                )

def notify_upd_event(instance):
    """Notify users that a followed event was updated."""
    for profile in instance.followers.all():
        notify.send(instance, recipient=profile.user, verb=instance.name + " was updated")

def event_saved(instance, created, **kwargs): # pylint: disable=W0613
    """Notify users when an event changes."""
    if not created:
        notify_upd_event(instance)

post_save.connect(event_saved, sender=Event)
m2m_changed.connect(notify_new_event, sender=Event.bodies.through)

class GenericNotificationRelatedField(serializers.RelatedField):
    """Serializer for actor/target of notifications."""
    def to_representation(self, value):
        if isinstance(value, Event):
            serializer = EventSerializer(value)

        return serializer.data

class NotificationSerializer(serializers.Serializer):
    """Notification Serializer, with unread and actor"""
    id = serializers.IntegerField()
    verb = serializers.ReadOnlyField(read_only=True)
    unread = serializers.BooleanField(read_only=True)
    actor = GenericNotificationRelatedField(read_only=True)
    actor_type = serializers.SerializerMethodField()

    def get_actor_type(self, obj):
        """Get the class name of actor."""
        return obj.actor.__class__.__name__.lower()
