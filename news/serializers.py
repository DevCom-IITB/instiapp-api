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
        # Get all UNR for news item
        unrs = obj.unr.all()

        # Count for each type
        reaction_counts = {t: 0 for t in range(0, 6)}
        for unr in unrs:
            if unr.reaction >= 0 and unr.reaction < 6:
                reaction_counts[unr.reaction] += 1

        return reaction_counts

    def get_user_reaction(self, obj):
        """Get the current user's reaction on the news item"""
        request = self.context['request'] if 'request' in self.context else None
        if request and request.user.is_authenticated:
            profile = request.user.profile
            return next((u.reaction for u in obj.unr.all() if u.user_id == profile.id), -1)
        return -1

    class Meta:
        model = NewsEntry
        fields = ('id', 'guid', 'link', 'title', 'content', 'published', 'body', 'reactions_count',
                  'user_reaction')

    @staticmethod
    def setup_eager_loading(queryset):
        """Perform necessary eager loading of data."""
        queryset = queryset.prefetch_related(
            'body', 'unr'
        )
        return queryset
