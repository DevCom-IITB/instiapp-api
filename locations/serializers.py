"""Serializer for Location."""
from rest_framework import serializers
from locations.models import Location

class LocationSerializer(serializers.ModelSerializer):
    """Serializer for Location."""

    class Meta:
        model = Location
        fields = ('id', 'name', 'short_name', 'group_id', 'pixel_x', 'pixel_y',
                  'parent', 'parent_relation', 'description', 'lat', 'lng', 'reusable')

class LocationSerializerMin(serializers.ModelSerializer):
    """Minimal serializer for Location."""

    class Meta:
        model = Location
        fields = ('id', 'name', 'short_name', 'lat', 'lng')
