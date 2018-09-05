from rest_framework import serializers

from users.serializers import UserProfileSerializer
from .models import complaints, tag_uris, comment
from upload.models import UploadedImage
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
    tags = TagSerializer(many=True, read_only=True)
    tag_names = serializers.SlugRelatedField(many=True, read_only=True, slug_field='tag_uri', source='tags')
    tag_ids = serializers.PrimaryKeyRelatedField(many=True, read_only=False, source='tags',
                                                 queryset=tag_uris.objects.all(), required=True)

    media = UploadedImageSerializer(many=True, read_only=True)
    # media = serializers.SlugRelatedField(many=True, read_only=True, slug_field='picture', source='media')
    media_ids = serializers.PrimaryKeyRelatedField(many=True, read_only=False, source='media',
                                                   queryset=UploadedImage.objects.all(), required=False)

    class Meta:
        model = complaints
        fields = (
            'id','description', 'report_date', 'latitude', 'longitude', 'location_description', 'tags',
            'tag_names',
            'tag_ids',
            'media', 'media_ids')

    def create(self, validated_data):
        result = super().create(validated_data)
        result.created_by = self.context['request'].user.profile
        result.save()
        return result