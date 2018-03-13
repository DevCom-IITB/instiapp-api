"""Serializers for Body Followers."""
from rest_framework import serializers
from bodies.models import Body

class BodyFollowersSerializer(serializers.ModelSerializer):
    """Serizlizer with list of followers of body."""

    from users.serializers import UserProfileSerializer

    followers = UserProfileSerializer(many=True, read_only=True)

    class Meta:
        model = Body
        fields = ('id', 'followers')
