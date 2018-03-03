' Serializers for Event '
from rest_framework import serializers
from events.models import Event
from locations.serializers import LocationSerializerMin

class EventSerializer(serializers.HyperlinkedModelSerializer):
    'Serializer for Event'

    interested_count = serializers.SerializerMethodField()
    going_count = serializers.SerializerMethodField()

    venues = LocationSerializerMin(many=True, read_only=True)

    class Meta:
        model = Event
        fields = ('url', 'id', 'name', 'description', 'image_url',
                  'start_time', 'end_time', 'all_day', 'venues', 'bodies',
                  'interested_count', 'going_count')

    def get_interested_count(self, obj):
        return obj.user_event_statuses.filter(status=1).count()

    def get_going_count(self, obj):
        return obj.user_event_statuses.filter(status=2).count()