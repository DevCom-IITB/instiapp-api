"""Serializer for ExternalBlog."""
from rest_framework import serializers
from placements.models import BlogEntry

class ExternalBlogEntrySerializer(serializers.ModelSerializer):
    """Serializer for ExternalPlacementBlogEntry."""

    class Meta:
        model = BlogEntry
        fields = ('id', 'guid', 'body', 'link', 'title', 'content', 'published')
