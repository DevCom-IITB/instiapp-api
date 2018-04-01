"""Serializer for PlacementBlog."""
from rest_framework import serializers
from placements.models import PlacementBlogEntry

class PlacementBlogEntrySerializer(serializers.ModelSerializer):
    """Serializer for PlacementBlogEntry."""

    class Meta:
        model = PlacementBlogEntry
        fields = ('id', 'guid', 'link', 'title', 'content', 'published')
