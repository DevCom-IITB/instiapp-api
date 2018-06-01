"""Serializer for News Feed."""
from rest_framework import serializers
from news.models import NewsEntry
from bodies.serializers import BodySerializerMin

class NewsEntrySerializer(serializers.ModelSerializer):
    """Serializer for NewsEntry."""
    body = BodySerializerMin()

    reactions_count = serializers.SerializerMethodField()
    user_reaction = serializers.SerializerMethodField()

    @staticmethod
    def get_reactions_count(obj):
        """Get number of user reactions on news item."""
        return {t : obj.reacted_by.filter(unr__reaction=t).count() for t in range(0, 6)}

    def get_user_reaction(self, obj):
        """Get the current user's reaction on the news item"""
        request = self.context['request']
        if request.user.is_authenticated:
            profile = request.user.profile
            unr = obj.unr.filter(user=profile)
            if unr.exists():
                return unr[0].reaction
        return -1

    class Meta:
        model = NewsEntry
        fields = ('id', 'guid', 'link', 'title', 'content', 'published', 'body', 'reactions_count',
                  'user_reaction')
