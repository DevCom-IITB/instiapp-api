"""Serializers for Achievements."""
from rest_framework import serializers
from achievements.models import Achievement
from bodies.serializer_min import BodySerializerMin
from events.serializers import EventMinSerializer
from users.serializers import UserProfileSerializer

class AchievementSerializer(serializers.ModelSerializer):
    """Serializer for Achievement model."""

    body_detail = BodySerializerMin(read_only=True, source="body")
    event_detail = EventMinSerializer(read_only=True, source="event")

    class Meta:
        model = Achievement
        fields = ('id', 'title', 'description', 'body_detail',
                  'dismissed', 'verified', 'event_detail')

    @staticmethod
    def setup_eager_loading(queryset):
        """Perform necessary eager loading of data."""
        queryset = queryset.prefetch_related('body')
        return queryset

class VerifiedAchievementListSerializer(serializers.ListSerializer):  # pylint: disable=abstract-method
    """List serializer for verified achievements"""

    def to_representation(self, data):
        data = data.filter(verified=True)
        return super(VerifiedAchievementListSerializer, self).to_representation(data)

class VerifiedAchievementSerializer(AchievementSerializer):
    """Verified achievement serializer."""
    class Meta(AchievementSerializer.Meta):
        list_serializer_class = VerifiedAchievementListSerializer

class AchievementUserSerializer(serializers.ModelSerializer):
    """Serializer for Achievement model."""

    body_detail = BodySerializerMin(read_only=True, source="body")
    event_detail = EventMinSerializer(read_only=True, source="event")
    user = UserProfileSerializer(read_only=True)

    class Meta:
        model = Achievement
        fields = ('id', 'title', 'description', 'admin_note',
                  'body_detail', 'dismissed', 'verified', 'user', 'body',
                  'verified_by', 'event', 'event_detail')

    @staticmethod
    def setup_eager_loading(queryset):
        """Perform necessary eager loading of data."""
        queryset = queryset.prefetch_related('body', 'user')
        return queryset

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user.profile
        validated_data['dismissed'] = False
        validated_data['verified'] = False
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data['verified_by'] = self.context['request'].user.profile
        return super().update(instance, validated_data)
