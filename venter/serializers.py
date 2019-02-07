"""Serializers for venter."""
from rest_framework import serializers
from users.serializers import UserProfileSerializer

from venter.models import Complaint
from venter.models import ComplaintTag
from venter.models import ComplaintComment

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComplaintTag
        fields = (
            'id', 'tag_uri'
        )

class CommentSerializer(serializers.ModelSerializer):
    commented_by = UserProfileSerializer()
    complaint = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = ComplaintComment
        fields = ('id', 'time', 'text', 'commented_by', 'complaint')

class ComplaintSerializer(serializers.ModelSerializer):
    created_by = UserProfileSerializer()
    users_up_voted = UserProfileSerializer(many=True)
    tags = TagSerializer(many=True)
    comments = CommentSerializer(many=True)
    images = serializers.SlugRelatedField(many=True, read_only=True, slug_field='image_url')

    class Meta:
        model = Complaint
        fields = (
            'id', 'created_by', 'description', 'suggestions', 'location_details', 'report_date', 'status', 'latitude',
            'longitude', 'location_description', 'tags', 'comments', 'users_up_voted', 'images'
        )

class ComplaintPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Complaint
        fields = (
            'id', 'description', 'suggestions', 'location_details', 'report_date', 'latitude', 'longitude',
            'location_description'
        )

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user.profile
        return super().create(validated_data)

class CommentPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComplaintComment
        fields = (
            'id', 'time', 'text')
