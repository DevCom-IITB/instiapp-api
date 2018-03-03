' Serializers for UserProfile '
from rest_framework import serializers
from users.models import UserProfile

class UserProfileSerializer(serializers.HyperlinkedModelSerializer):
    ' Serializer for UserProfile '

    class Meta:
        model = UserProfile
        fields = ('url', 'id', 'name', 'profile_pic')

class UserProfileFullSerializer(serializers.HyperlinkedModelSerializer):
    ' Full serializer for UserProfile with detailed information and events'

    from bodies.serializers import BodySerializerMin

    events_interested = serializers.SerializerMethodField()
    events_going = serializers.SerializerMethodField()
    followed_bodies = BodySerializerMin(many=True, read_only=True)

    class Meta:
        model = UserProfile
        fields = ('url', 'id', 'name', 'profile_pic', 'events_interested', 'events_going', 'followed_bodies')

    def get_events_interested(self, obj):
        from events.serializers import EventSerializer
        return [EventSerializer(x.event, context=self.context).data \
                for x in obj.events_followed.filter(status=1)]
    
    def get_events_going(self, obj):
        from events.serializers import EventSerializer
        return [EventSerializer(x.event, context=self.context).data \
                for x in obj.events_followed.filter(status=2)]