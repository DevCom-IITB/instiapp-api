"""Serializers for venter."""
from rest_framework import serializers
from users.serializers import UserProfileSerializer

from venter.models import Complaints
from venter.models import TagUris
from venter.models import Comment

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = TagUris
        fields = (
            'id', 'tag_uri'
        )

class CommentSerializer(serializers.ModelSerializer):
    commented_by = UserProfileSerializer()

    class Meta:
        model = Comment
        fields = (
            'id', 'time', 'text', 'commented_by'
        )

class ComplaintSerializer(serializers.ModelSerializer):
    created_by = UserProfileSerializer()
    users_up_voted = UserProfileSerializer(many=True)
    tags = TagSerializer(many=True)
    comments = CommentSerializer(many=True)
    images = serializers.SlugRelatedField(many=True, read_only=True, slug_field='image_url')

    class Meta:
        model = Complaints
        fields = (
            'id', 'created_by', 'description', 'report_date', 'status', 'latitude',
            'longitude', 'location_description', 'tags', 'comments', 'users_up_voted', 'images'
        )

class ComplaintPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Complaints
        fields = (
            'id', 'description', 'report_date', 'latitude', 'longitude', 'location_description', 'authority_email')

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user.profile
        return super().create(validated_data)

class CommentPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = (
            'id', 'time', 'text')
