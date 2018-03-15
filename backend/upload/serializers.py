"""Serializer for Image Uploads."""
from rest_framework import serializers
from upload.models import UploadedImage

class UploadedImageSerializer(serializers.ModelSerializer):
    """Serializer for UploadedImage."""

    class Meta:
        model = UploadedImage
        fields = ('id', 'picture')
