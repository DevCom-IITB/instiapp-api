# In upload/serializers.py
from rest_framework import serializers
from .models import UploadedFile

class FileUploadSerializer(serializers.ModelSerializer):
    """Serializer for file uploads."""
    
    class Meta:
        model = UploadedFile
        fields = [
            'id', 
            'file', 
        ]
        
    def create(self, validated_data):
        validated_data["uploaded_by"] = self.context["request"].user.profile
        result = super().create(validated_data)
        return result

# ✅ Keep backward compatibility
# class UploadedImageSerializer(FileUploadSerializer):
#     """Serializer for POST file UploadedImage."""

#     picture = serializers.ImageField
class UploadedFileSerializer(FileUploadSerializer):
    """Serializer for POST file UploadedFile."""

    file = serializers.FileField()

ImageUploadSerializer = FileUploadSerializer
UploadedImageSerializer = UploadedFileSerializer



# """Serializer for Image Uploads."""
# from rest_framework import serializers
# from upload.models import UploadedImage


# class BaseUploadedImageSerializer(serializers.ModelSerializer):
#     """Base Serializer for UploadedImage."""

#     class Meta:
#         model = UploadedImage
#         fields = ("id", "picture")

#     def create(self, validated_data):
#         validated_data["uploaded_by"] = self.context["request"].user.profile
#         result = super().create(validated_data)
#         return result


# class UploadedImageSerializer(BaseUploadedImageSerializer):
#     """Serializer for POST file UploadedImage."""

#     picture = serializers.ImageField
