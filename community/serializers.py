from rest_framework import serializers
from achievements.models import Interest
from community.models import Community, CommunityPost
from community.serializer_min import CommunityPostSerializerMin
from roles.serializers import RoleSerializerMin
from users.models import UserProfile
from bodies.models import Body
from users.serializers import UserProfileSerializer


class CommunitySerializers(serializers.ModelSerializer):
    followers_count = serializers.SerializerMethodField()
    is_user_following = serializers.SerializerMethodField()
    roles = RoleSerializerMin(many=True, read_only=True, source="body.roles")
    posts = serializers.SerializerMethodField()
    featured_posts = serializers.SerializerMethodField()

    def get_featured_posts(self, obj):
        """Get the featured posts of community"""
        queryset = obj.posts.filter(featured=True, deleted=False, status=1)
        return CommunityPostSerializerMin(queryset, many=True).data

    def get_posts(self, obj):
        """Get the posts of the community"""
        queryset = obj.posts.filter(thread_rank=1)
        return CommunityPostSerializerMin(queryset, many=True).data

    def get_followers_count(self, obj):
        """Get followers of body."""
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
            "description",
            "created_at",
            "updated_at",
            "cover_image",
            "logo_image",
            "followers_count",
            "is_user_following",
            "roles",
            "posts",
            "body",
            "featured_posts",
        )

    @staticmethod
    def setup_eager_loading(queryset, request):
        """Perform necessary eager loading of data."""

        # Prefetch body child relations

        # Annotate followers count

        return queryset


class CommunityPostSerializers(CommunityPostSerializerMin):
    comments = serializers.SerializerMethodField()
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

    def get_comments(self, obj):
        comments = obj.comments.filter(deleted=False, status=1)
        return CommunityPostSerializerMin(comments, many=True).data

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
            "comments",
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
        )

    def create(self, validated_data):
        data = self.context["request"].data
        if "parent" in data and data["parent"]:
            parent = CommunityPost.objects.get(id=data["parent"])
            validated_data["parent"] = parent
            validated_data["thread_rank"] = parent.thread_rank + 1
            validated_data["status"] = 1
        else:
            validated_data["parent"] = None
            validated_data["thread_rank"] = 1
            validated_data["status"] = 0
        validated_data["image_url"] = (
            ",".join(data["image_url"]) if "image_url" in data else ""
        )
        if "tag_user" in data and data["tag_user"]:
            validated_data["tag_user"] = [
                UserProfile.objects.get(id=i["id"]) for i in data["tag_user"]
            ]
        if "tag_body" in data and data["tag_body"]:
            validated_data["tag_body"] = [
                Body.objects.get(id=i["id"]) for i in data["tag_body"]
            ]
        if "interests" in data and data["interests"]:
            validated_data["interests"] = [
                Interest.objects.get(id=i["id"]) for i in data["interests"]
            ]
        validated_data["posted_by"] = self.context["request"].user.profile
        validated_data["community"] = Community.objects.get(id=data["community"]["id"])
        return super().create(validated_data)

    def update(self, instance, validated_data):
        data = self.context["request"].data
        if "tag_user" in data and data["tag_user"]:
            validated_data["tag_user"] = [
                UserProfile.objects.get(id=i["id"]) for i in data["tag_user"]
            ]
        if "tag_body" in data and data["tag_body"]:
            validated_data["tag_body"] = [
                Body.objects.get(id=i["id"]) for i in data["tag_body"]
            ]
        if "interests" in data and data["interests"]:
            validated_data["interests"] = [
                Interest.objects.get(id=i["id"]) for i in data["interests"]
            ]
        validated_data["status"] = 0
        validated_data["deleted"] = False
        validated_data["featured"] = False
        validated_data["image_url"] = (
            ",".join(data["image_url"])
            if "image_url" in data and data["image_url"]
            else ""
        )
        return super().update(instance, validated_data)

    def destroy(self, instance, validated_data):
        data = self.context["request"].data
        validated_data["status"] = 0
        validated_data["deleted"] = True
        validated_data["image_url"] = (
            ",".join(data["image_url"]) if "image_url" in data else ""
        )
        return super().update(instance, validated_data)
