' Serializers for Location '
from rest_framework import serializers
from locations.models import Location

class LocationSerializer(serializers.HyperlinkedModelSerializer):
    ' Serializer for Location '

    class Meta:
        model = Location
        fields = ('url', 'id', 'name', 'lat', 'lng')

class LocationSerializerMin(serializers.HyperlinkedModelSerializer):
    ' Minimal serializer for Location '

    class Meta:
        model = Location
        fields = ('name', 'url')
