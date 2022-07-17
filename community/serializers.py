from collections import Counter
import re
from wsgiref import validate
from rest_framework import serializers
from community.models import Community, CommunityPost
from community.serializer_min import CommunityPostSerializerMin
from roles.serializers import RoleSerializerMin
from users.models import UserProfile
from bodies.models import Body
from locations.models import Location
from unicodedata import name

class CommunitySerializers(serializers.ModelSerializer):

    followers_count = serializers.SerializerMethodField()
    is_user_following = serializers.SerializerMethodField()
    roles = RoleSerializerMin(many=True, read_only=True, source='body.roles')
    posts = serializers.SerializerMethodField()

    def featured_posts(self, obj):
        """Get the featured posts of community"""
        queryset = obj.posts.filter(featured=True)

        return CommunityPostSerializerMin(queryset, many=True).data

    def get_posts(self, obj):
        """Get the posts of the community """
        queryset = obj.posts.filter(thread_rank=1)
        return CommunityPostSerializerMin(queryset, many=True).data

    def get_followers_count(self, obj):
        """Get followers of body."""
        if obj.body == None:
            return 0
        return obj.body.followers.count()

    def get_is_user_following(self, obj):
        """Get the current user's reaction on the community post """
        request = self.context['request'] if 'request' in self.context else None
        if request and request.user.is_authenticated:
            profile = request.user.profile
            return profile.followed_bodies.filter(id=obj.body.id).exists()
        return False

    class Meta:
        model = Community
        fields = ('id', 'str_id', 'name', 'about', 'description', 'created_at', 'updated_at',
                  'cover_image', 'logo_image', 'followers_count', 'is_user_following', 'roles', 'posts', 'body')

    @staticmethod
    def setup_eager_loading(queryset, request):
        """Perform necessary eager loading of data."""

        # Prefetch body child relations

        # Annotate followers count

        return queryset


class CommunityPostSerializers(CommunityPostSerializerMin):
    comments = CommunityPostSerializerMin(many=True, read_only=True)

    class Meta:
        model = CommunityPost
        fields = ('id', 'str_id', 'content', 'posted_by',
                  'reactions_count', 'user_reaction', 'comments_count', 'time_of_creation', 'time_of_modification',
                  'image_url', 'comments', 'thread_rank', 'community')

    def create(self, validated_data):
        data = self.context["request"].data
        if 'parent' in data and data['parent']:
            parent = CommunityPost.objects.get(id=data['parent'])
            validated_data['parent'] = parent
            validated_data["thread_rank"] = parent.thread_rank + 1
            validated_data["status"] = 1
        else:
            validated_data['parent'] = None
            validated_data["thread_rank"] = 1
            validated_data["status"] = 0
        validated_data['image_url'] = ",".join(validated_data["image_url"]) if 'image_url' in validated_data else ""
        if 'tag_user' in data and data["tag_user"]:
            validated_data["tag_user"] = [UserProfile.objects.get(id=i['id']) for i in data['tag_user']]
        if 'tag_body' in data and data['tag_body']:
            validated_data['tag_body'] = [Body.objects.get(id=i['id']) for i in data['tag_body']]
        if 'tag_location' in data and data['tag_location']:
            validated_data['tag_location'] = [Location.objects.get(id=i['id']) for i in data['tag_location']]

        validated_data['posted_by'] = self.context['request'].user.profile
        return super().create(validated_data)

    def update(self, validated_data, pk):
        if validated_data["tag_user_call"]:
            validated_data["tag_user_call"] = UserProfile.objects.get(name)
        if validated_data["tag_body_call"]:
            validated_data["tag_body_call"] = Body.objects.get(name)
        if validated_data["tag_location_call"]:
            validated_data["tag_location_call"] = Location.objects.get(name)
        return super().update(validated_data, pk)
