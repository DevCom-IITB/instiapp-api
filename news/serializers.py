"""Serializer for News Feed."""
from rest_framework import serializers
from news.models import NewsEntry
from bodies.serializers import BodySerializerMin

class NewsEntrySerializer(serializers.ModelSerializer):
    """Serializer for NewsEntry."""
    body = BodySerializerMin()

    reactions_count = serializers.SerializerMethodField()

    def get_reactions_count(self, obj):
        """Get number of user reactions on news item."""
        return {t : obj.reacted_by.filter(unr__reaction=t).count() for t in range(0, 6)}

    class Meta:
        model = NewsEntry
        fields = ('id', 'guid', 'link', 'title', 'content', 'published', 'body', 'reactions_count')
