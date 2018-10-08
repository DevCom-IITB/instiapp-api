"""Serializers for UserProfile."""
from django.conf import settings
from rest_framework import serializers
from users.models import UserProfile

class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for UserProfile."""

    class Meta:
        model = UserProfile
        fields = ('id', 'name', 'profile_pic', 'ldap_id')

    def to_representation(self, instance):
        return settings.USER_PROFILE_SERIALIZER_TRANSFORM(
            super().to_representation(instance))
