' Serializers for Event '
from rest_framework import serializers
from events.models import Event
from locations.serializers import LocationSerializerMin

class EventSerializer(serializers.HyperlinkedModelSerializer):
    'Serializer for Event'

    venues = LocationSerializerMin(many=True, read_only=True)

    class Meta:
        model = Event
        fields = ('url', 'id', 'name', 'description', 'image_url',
                  'start_time', 'end_time', 'all_day', 'venues', 'bodies')
