' Serializers for UserProfile '
from rest_framework import serializers
from users.models import UserProfile

class UserProfileSerializer(serializers.ModelSerializer):
    ' Serializer for UserProfile '

    class Meta:
        model = UserProfile
        fields = ('id', 'name', 'profile_pic')

class UserProfileFullSerializer(serializers.ModelSerializer):
    ' Full serializer for UserProfile with detailed information and events'

    from bodies.serializers import BodySerializerMin
    from bodies.models import Body

    events_interested = serializers.SerializerMethodField()
    events_going = serializers.SerializerMethodField()

    followed_bodies = BodySerializerMin(many=True, read_only=True)
    followed_bodies_id = serializers.PrimaryKeyRelatedField(many=True, read_only=False,
                                     queryset=Body.objects.all(), source='followed_bodies')

    class Meta:
        model = UserProfile
        fields = ('id', 'name', 'profile_pic', 'events_interested', 'events_going',
                  'email', 'year', 'roll_no', 'contact_no', 'about',
                  'followed_bodies', 'followed_bodies_id')

    def get_events_interested(self, obj):
        from events.serializers import EventSerializer
        return EventSerializer(obj.followed_events.filter(ues__status=1), many=True).data

    def get_events_going(self, obj):
        from events.serializers import EventSerializer
        return EventSerializer(obj.followed_events.filter(ues__status=2), many=True).data
