"""Minimal serializer for Body."""
from rest_framework import serializers
from achievements.serializers import InterestSerializer
from bodies.serializer_min import BodySerializerMin
from community.models import Community, CommunityPost
from users.models import UserProfile
from users.serializers import UserProfileSerializer


class CommunitySerializerMin(serializers.ModelSerializer):
    """Minimal serializer for Community."""

    followers_count = serializers.SerializerMethodField()
    is_user_following = serializers.SerializerMethodField()

    def get_followers_count(self, obj):
        """Get followers of community."""
        if obj.body is None:
            return 0
        return obj.body.followers.count()

    def get_is_user_following(self, obj):
        """Get the current user's reaction on the community post"""
        request = self.context["request"] if "request" in self.context else None
        if request and request.user.is_authenticated:
            profile = request.user.profile
            return profile.followed_bodies.filter(id=obj.body.id).exists()
        return False

    class Meta:
        model = Community
        fields = (
            "id",
            "str_id",
            "name",
            "about",
            "cover_image",
            "logo_image",
            "followers_count",
            "body",
            "is_user_following",
        )


class CommunityPostSerializerMin(serializers.ModelSerializer):
    """Minimal serializer for Body."""

    reactions_count = serializers.SerializerMethodField()
    user_reaction = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    # posted_by = UserProfileSerializer(read_only=True)
    posted_by = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()
    most_liked_comment = serializers.SerializerMethodField()
    community = CommunitySerializerMin(read_only=True)
    tag_body = BodySerializerMin(read_only=True, many=True)
    tag_user = UserProfileSerializer(read_only=True, many=True)
    interests = InterestSerializer(read_only=True, many=True)
    has_user_reported = serializers.SerializerMethodField()
    posted_by = serializers.SerializerMethodField()

    # def get_posted_by(self, obj):
    #     pb = UserProfile.objects.get(id=obj.posted_by.id)
    #     if obj.anonymous:
    #         pb.name = "Anonymous"
    #         pb.id = "null"
    #         pb.ldap_id = "null"
    #         pb.profile_pic = \
    #             'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSM9q9XJKxlskry5gXTz1OXUyem5Ap59lcEGg&usqp=CAU'
    #     return UserProfileSerializer(pb).data

    def get_posted_by(self, obj):
        pb = UserProfile.objects.get(id=obj.posted_by.id)
        if (
            obj.anonymous
            and "return_for_mod" in self.context
            and not self.context["return_for_mod"]
        ):
            pb.name = "Anonymous"
            pb.id = "null"
            pb.ldap_id = "null"
            pb.profile_pic = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSM9q9XJKxlskry5gXTz1OXUyem5Ap59lcEGg&usqp=CAU"
        elif (
            obj.anonymous
            and "return_for_mod" in self.context
            and self.context["return_for_mod"]
        ):
            pb.name += "  (Anon)"
        return UserProfileSerializer(pb).data

    def get_most_liked_comment(self, obj):
        """Get the most liked comment of the community post"""
        queryset = obj.comments.filter(deleted=False, status=1)
        if len(queryset) == 0:
            return None
        max = 0
        most_liked_comment = None
        for comment in queryset:
            if comment.ucpr.count() >= max:
                max = comment.ucpr.count()
                most_liked_comment = comment

        return CommunityPostSerializerMin(most_liked_comment).data

    def get_image_url(self, obj):
        """Get the image url of the community post"""
        return obj.image_url.split(",") if obj.image_url else None

    @staticmethod
    def setup_eager_loading(queryset, request):
        """Perform necessary eager loading of data."""

        # Prefetch body child relations

        # Annotate followers count

        return queryset

    @staticmethod
    def get_reactions_count(obj):
        """Get number of user reactions on community post item."""
        # Get all UCPR for news item
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
        if (
            not obj.comments.exists()
            or len(obj.comments.filter(deleted=False, status=1)) == 0
        ):
            return 0
        count = 0

        for comment in obj.comments.filter(deleted=False, status=1):
            count += 1
            count += CommunityPostSerializerMin.get_comments_count(comment)

        return count

    def get_user_reaction(self, obj):
        """Get the current user's reaction on the community post"""
        request = self.context["request"] if "request" in self.context else None
        if request and request.user.is_authenticated:
            profile = request.user.profile
            return next(
                (u.reaction for u in obj.ucpr.all() if u.user_id == profile.id), -1
            )
        return -1

    def get_has_user_reported(self, obj):
        """Get the current user's report on the community post"""
        request = self.context["request"] if "request" in self.context else None
        if request and request.user.is_authenticated:
            profile = request.user.profile

            return obj.reported_by.filter(id=profile.id).exists()
        return False

    class Meta:
        model = CommunityPost
        fields = (
            "id",
            "str_id",
            "content",
            "posted_by",
            "reactions_count",
            "user_reaction",
            "comments_count",
            "time_of_creation",
            "time_of_modification",
            "image_url",
            "most_liked_comment",
            "thread_rank",
            "community",
            "status",
            "tag_body",
            "tag_user",
            "interests",
            "featured",
            "deleted",
            "anonymous",
            "reported_by",
            "has_user_reported",
        )
