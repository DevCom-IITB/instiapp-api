' Serializers for Event '
from rest_framework import serializers
from events.models import Event

class EventSerializer(serializers.HyperlinkedModelSerializer):
    'Serializer for Event'

    class Meta:
        model = Event
        fields = ('url', 'id', 'name', 'description', 'image_url',
                  'start_time', 'end_time', 'all_day', 'venue', 'bodies')
