"""Serializer for ExternalBlog."""
from rest_framework import serializers
from external.models import ExternalBlogEntry


class ExternalBlogEntrySerializer(serializers.ModelSerializer):
    """Serializer for ExternalPlacementBlogEntry."""

    class Meta:
        model = ExternalBlogEntry
        fields = ("id", "guid", "body", "link", "title", "content", "published")
