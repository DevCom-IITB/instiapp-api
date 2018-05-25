"""Serializer for News Feed."""
from rest_framework import serializers
from news.models import NewsEntry
from bodies.serializers import BodySerializerMin

class NewsEntrySerializer(serializers.ModelSerializer):
    """Serializer for NewsEntry."""
    body = BodySerializerMin()

    class Meta:
        model = NewsEntry
        fields = ('id', 'guid', 'link', 'title', 'content', 'published', 'body')
