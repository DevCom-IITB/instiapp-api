' Serializers for Event '
from rest_framework import serializers
from events.models import Event
from locations.serializers import LocationSerializerMin, LocationSerializer
from users.serializers import UserProfileSerializer

class FollowersMethods:
    ' Methods for followers '
    def get_count(self, obj, s):
        return obj.user_event_statuses.filter(status=s).count()

    def get_followers(self, obj, s):
        return [UserProfileSerializer(x.user, context=self.context).data \
                for x in obj.user_event_statuses.filter(status=s)]

class EventSerializer(serializers.HyperlinkedModelSerializer):
    'Serializer for Event'

    interested_count = serializers.SerializerMethodField()
    get_interested_count = lambda self, obj: FollowersMethods.get_count(self, obj, 1)

    going_count = serializers.SerializerMethodField()
    get_going_count = lambda self, obj: FollowersMethods.get_count(self, obj, 2)

    venues = LocationSerializerMin(many=True, read_only=True)

    class Meta:
        model = Event
        fields = ('url', 'id', 'name', 'description', 'image_url',
                  'start_time', 'end_time', 'all_day', 'venues', 'bodies',
                  'interested_count', 'going_count')

class EventFullSerializer(serializers.HyperlinkedModelSerializer):
    'Serializer for Event with more information (followers, venues etc.)'

    interested_count = serializers.SerializerMethodField()
    get_interested_count = lambda self, obj: FollowersMethods.get_count(self, obj, 1)

    going_count = serializers.SerializerMethodField()
    get_going_count = lambda self, obj: FollowersMethods.get_count(self, obj, 2)

    interested = serializers.SerializerMethodField()
    get_interested = lambda self, obj: FollowersMethods.get_followers(self, obj, 1)

    going = serializers.SerializerMethodField()
    get_going = lambda self, obj: FollowersMethods.get_followers(self, obj, 2)

    venues = LocationSerializer(many=True, read_only=True)

    class Meta:
        model = Event
        fields = ('url', 'id', 'name', 'description', 'image_url',
                  'start_time', 'end_time', 'all_day', 'venues', 'bodies',
                  'interested_count', 'going_count', 'interested', 'going')
