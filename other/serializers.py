"""Serializers for non-specific models."""
from rest_framework import serializers
from community.models import CommunityPost, Community, CommunityPostUserReaction
from community.serializers import CommunityPostSerializers, CommunitySerializers
from events.models import Event
from events.serializers import EventSerializer
from external.models import ExternalBlogEntry
from placements.models import BlogEntry
from placements.serializers import BlogEntrySerializer
from news.models import NewsEntry
from news.serializers import NewsEntrySerializer
from venter.models import ComplaintComment
from venter.serializers import CommentSerializer
from users.models import UserTag, UserTagCategory, UserProfile
from users.serializers import UserProfileSerializer
from querybot.models import UnresolvedQuery
from querybot.serializers import UnresolvedQuerySerializer


class GenericNotificationRelatedField(
    serializers.RelatedField
):  # pylint: disable=W0223
    """Serializer for actor/target of notifications."""

    def to_representation(self, value):
        serializer = None
        if isinstance(value, Event):
            serializer = EventSerializer(value)
        elif isinstance(value, NewsEntry):
            serializer = NewsEntrySerializer(value)
        elif isinstance(value, BlogEntry):
            serializer = BlogEntrySerializer(value)
        elif isinstance(value, ComplaintComment):
            serializer = CommentSerializer(value)
        elif isinstance(value, UnresolvedQuery):
            serializer = UnresolvedQuerySerializer(value)
        elif isinstance(value, ExternalBlogEntry):
            serializer = ExternalBlogEntry(value)
        elif isinstance(value, CommunityPost):
            serializer = CommunityPostSerializers(value)
        elif isinstance(value, Community):
            serializer = CommunitySerializers(value)
        elif isinstance(value, CommunityPostUserReaction):
            serializer = CommunityPostSerializers(value.communitypost)
        elif isinstance(value, UserProfile):
            serializer = UserProfileSerializer(value)
        if serializer:
            return serializer.data
        return None


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
        fields = ("id", "name")


class UserTagCategorySerializer(serializers.ModelSerializer):
    tags = UserTagSerializer(many=True)

    class Meta:
        model = UserTagCategory
        fields = ("id", "name", "tags")
