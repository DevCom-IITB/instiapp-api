"""Minimal serializer for Body."""
from itertools import count
from rest_framework import serializers
from bodies.serializer_min import BodySerializerMin
from community.models import Community, CommunityPost
from bodies.serializers_followers import BodyFollowersSerializer
from users.serializers import UserProfileSerializer

class CommunitySerializerMin(serializers.ModelSerializer):
    """Minimal serializer for Community."""

    followers_count = serializers.SerializerMethodField()

    def get_followers_count(self, obj):
        """Get followers of community."""
        if obj.body == None:
            return 0
        return obj.body.followers.count()

    class Meta:
        model = Community
        fields = ('id', 'str_id', 'name', 'about', 'cover_image', 'logo_image', 'followers_count')

class CommunityPostSerializerMin(serializers.ModelSerializer):
    """Minimal serializer for Body."""

    reactions_count = serializers.SerializerMethodField()
    user_reaction = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    posted_by = UserProfileSerializer(read_only=True)
    image_url = serializers.SerializerMethodField()
    most_liked_comment = serializers.SerializerMethodField()

    def get_most_liked_comment(self, obj):
        """Get the most liked comment of the community post """
        queryset = obj.comments.all()
        max = 0
        most_liked_comment = None
        for comment in queryset:
            if comment.ucpr.count() >= max:
                max = comment.ucpr.count()
                most_liked_comment = comment

        return CommunityPostSerializerMin(most_liked_comment).data

    def get_image_url(self, obj):
        """Get the image url of the community post """
        return obj.image_url.split(',')

    @staticmethod
    def setup_eager_loading(queryset, request):
        """Perform necessary eager loading of data."""

        # Prefetch body child relations

        # Annotate followers count

        return queryset

    @staticmethod
    def get_reactions_count(obj):
        """Get number of user reactions on community post item."""
        # Get all UNR for news item
        ucprs = obj.ucpr.all()

        # Count for each type
        reaction_counts = {t: 0 for t in range(0, 6)}
        for ucpr in ucprs:
            if ucpr.reaction >= 0 and ucpr.reaction < 6:
                reaction_counts[ucpr.reaction] += 1

        return reaction_counts

    @staticmethod
    def get_comments_count(obj):
        """Get number of comments on community post item."""
        if not obj.comments.exists() or obj.comments.count() == 0:
            return 0
        count = 0

        for comment in obj.comments.all():
            count += 1
            count += CommunityPostSerializerMin.get_comments_count(comment)

        return count

    def get_user_reaction(self, obj):
        """Get the current user's reaction on the community post """
        request = self.context['request'] if 'request' in self.context else None
        if request and request.user.is_authenticated:
            profile = request.user.profile
            return next((u.reaction for u in obj.ucpr.all() if u.user_id == profile.id), -1)
        return -1

    class Meta:
        model = CommunityPost
        fields = ('id', 'str_id', 'content', 'posted_by',
                  'reactions_count', 'user_reaction', 'comments_count', 'time_of_creation', 'time_of_modification',
                  'image_url', 'most_liked_comment')
