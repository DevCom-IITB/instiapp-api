"""Serializer for Image Uploads."""
from rest_framework import serializers
from upload.models import UploadedImage


class BaseUploadedImageSerializer(serializers.ModelSerializer):
    """Base Serializer for UploadedImage."""

    class Meta:
        model = UploadedImage
        fields = ("id", "picture")

    def create(self, validated_data):
        validated_data["uploaded_by"] = self.context["request"].user.profile
        result = super().create(validated_data)
        return result


class UploadedImageSerializer(BaseUploadedImageSerializer):
    """Serializer for POST file UploadedImage."""

    picture = serializers.ImageField
