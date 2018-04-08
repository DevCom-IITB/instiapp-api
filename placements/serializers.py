"""Serializer for PlacementBlog."""
from rest_framework import serializers
from placements.models import BlogEntry

class BlogEntrySerializer(serializers.ModelSerializer):
    """Serializer for PlacementBlogEntry."""

    class Meta:
        model = BlogEntry
        fields = ('id', 'guid', 'link', 'title', 'content', 'published')
