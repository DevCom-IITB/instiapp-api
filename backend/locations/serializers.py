' Serializers for Location '
from rest_framework import serializers
from locations.models import Location

class LocationSerializer(serializers.HyperlinkedModelSerializer):
    ' Serializer for Location '

    class Meta:
        model = Location
        fields = ('url', 'id', 'name', 'lat', 'lng')
