"""Serializer for Image Uploads."""
from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField
from upload.models import UploadedImage

class UploadedImageSerializer(serializers.ModelSerializer):
    """Serializer for UploadedImage."""

    picture = Base64ImageField()

    class Meta:
        model = UploadedImage
        fields = ('id', 'picture')

    def create(self, validated_data):
        validated_data['uploaded_by'] = self.context['request'].user.profile
        result = super().create(validated_data)
        return result
