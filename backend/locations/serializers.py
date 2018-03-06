"""Serializer for Location."""
from rest_framework import serializers
from locations.models import Location

class LocationSerializer(serializers.ModelSerializer):
    """Serializer for Location."""

    class Meta:
        model = Location
        fields = ('id', 'name', 'lat', 'lng')

class LocationSerializerMin(serializers.ModelSerializer):
    """Minimal serializer for Location."""

    class Meta:
        model = Location
        fields = ('id', 'name')
