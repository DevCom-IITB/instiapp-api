"""Minimal serializer for Body."""
from rest_framework import serializers
from bodies.models import Body


class BodySerializerMin(serializers.ModelSerializer):
    """Minimal serializer for Body."""

    followers_count = serializers.SerializerMethodField()

    class Meta:
        model = Body
        fields = (
            "id",
            "str_id",
            "name",
            "short_description",
            "website_url",
            "image_url",
            "cover_url",
            "followers_count",
            "short_name",
        )

    def get_followers_count(self, obj):
        return obj.followers.count() if hasattr(obj, "followers") else 0
