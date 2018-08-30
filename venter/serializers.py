from rest_framework import serializers

from users.serializers import UserProfileSerializer
from .models import complaints, tag_uris, comment
from upload.serializers import UploadedImageSerializer


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = tag_uris
        fields = '__all__'


class CommentSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer()

    class Meta:
        model = comment
        fields = '__all__'


class ComplaintSerializer(serializers.ModelSerializer):
    created_by = UserProfileSerializer()
    users_up_voted = UserProfileSerializer(many=True)
    tags = TagSerializer(many=True)
    comments = CommentSerializer(many=True)  # related name (comments)
    media = UploadedImageSerializer(many=True)

    class Meta:
        model = complaints
        fields = '__all__'


class ComplaintPostSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=False)
    media = UploadedImageSerializer(many=True, read_only=False)
    created_by = UserProfileSerializer(read_only= False)

    class Meta:
        model = complaints
        fields = (
            'created_by', 'description', 'report_date', 'latitude', 'longitude', 'location_description', 'tags',
            'media')