"""Serializers for non-specific models."""
from rest_framework import serializers
from events.models import Event
from events.serializers import EventSerializer
from placements.models import BlogEntry
from placements.serializers import BlogEntrySerializer
from news.models import NewsEntry
from news.serializers import NewsEntrySerializer
from venter.models import ComplaintComment
from venter.serializers import CommentSerializer
from users.models import UserTag
from users.models import UserTagCategory

class GenericNotificationRelatedField(serializers.RelatedField):  # pylint: disable=W0223
    """Serializer for actor/target of notifications."""
    def to_representation(self, value):
        if isinstance(value, Event):
            serializer = EventSerializer(value)
        elif isinstance(value, NewsEntry):
            serializer = NewsEntrySerializer(value)
        elif isinstance(value, BlogEntry):
            serializer = BlogEntrySerializer(value)
        elif isinstance(value, ComplaintComment):
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


class UserTagSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserTag
        fields = ('id', 'name')

class UserTagCategorySerializer(serializers.ModelSerializer):

    tags = UserTagSerializer(many=True)

    class Meta:
        model = UserTagCategory
        fields = ('id', 'name', 'tags')
