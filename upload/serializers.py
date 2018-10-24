"""Serializer for Image Uploads."""
from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField
from upload.models import UploadedImage

class BaseUploadedImageSerializer(serializers.ModelSerializer):
    """Base Serializer for UploadedImage."""

    class Meta:
        model = UploadedImage
        fields = ('id', 'picture')

    def create(self, validated_data):
        validated_data['uploaded_by'] = self.context['request'].user.profile
        result = super().create(validated_data)
        return result

class UploadedImageSerializer(BaseUploadedImageSerializer):
    """Serializer for POST file UploadedImage."""
    picture = serializers.ImageField

class Base64UploadedImageSerializer(BaseUploadedImageSerializer):
    """Serializer for Base64 UploadedImage."""
    picture = Base64ImageField()
