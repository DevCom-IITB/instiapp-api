from rest_framework import serializers

from users.serializers import UserProfileSerializer
from .models import Complaints, TagUris, Comment

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
    media= serializers.SlugRelatedField(many=True, read_only=True, slug_field='image_url')

    class Meta:
        model = Complaints
        fields = (
            'id', 'created_by', 'description', 'report_date', 'status', 'latitude',
            'longitude', 'location_description', 'tags', 'comments', 'users_up_voted','media'
        )

class ComplaintPostSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    tag_names = serializers.SlugRelatedField(many=True, read_only=True, slug_field='tag_uri', source='tags')
    tag_ids = serializers.PrimaryKeyRelatedField(many=True, read_only=False, source='tags',
                                                 queryset=TagUris.objects.all(), required=True)

    class Meta:
        model = Complaints
        fields = (
            'id', 'description', 'report_date', 'latitude', 'longitude', 'location_description', 'tags',
            'tag_names',
            'tag_ids')

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user.profile
        return super().create(validated_data)

    def to_representation(self, instance):
        result = super().to_representation(instance)
        # Remove unnecessary fields
        result.pop('tag_ids')
        result.pop('tags')
        return result

class CommentPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = (
            'id', 'time', 'text')
