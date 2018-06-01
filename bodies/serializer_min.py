"""Minimal serializer for Body."""
from rest_framework import serializers
from bodies.models import Body

class BodySerializerMin(serializers.ModelSerializer):
    """Minimal serializer for Body."""

    class Meta:
        model = Body
        fields = ('id', 'str_id', 'name', 'short_description', 'website_url', 'image_url', 'cover_url')
