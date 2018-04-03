"""Serializers for UserProfile."""
from rest_framework import serializers
from users.models import UserProfile

class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for UserProfile."""

    class Meta:
        model = UserProfile
        fields = ('id', 'name', 'profile_pic', 'ldap_id')
