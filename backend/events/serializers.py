"""Serializers for Event."""
from rest_framework import serializers
from events.models import Event

class FollowersMethods:
    """Helper methods for followers."""

    @staticmethod
    def get_count(obj, status):
        """Get count of followers with specified status."""
        return obj.followers.filter(ues__status=status).count()

    @staticmethod
    def get_followers(obj, status):
        """Get serialized followers with specified status."""
        from users.serializers import UserProfileSerializer
        return UserProfileSerializer(obj.followers.filter(ues__status=status), many=True).data

class EventSerializer(serializers.ModelSerializer):
    """Serializer for Event.

    This serializer returns only the count of followers in
    each category, i.e. interested and going and minimal
    venue info. Use `EventFullSerializer` if you want information
    on individual users and venues.
    """

    from locations.serializers import LocationSerializerMin
    from bodies.serializer_min import BodySerializerMin

    interested_count = serializers.SerializerMethodField()
    get_interested_count = lambda self, obj: FollowersMethods.get_count(obj, 1)

    going_count = serializers.SerializerMethodField()
    get_going_count = lambda self, obj: FollowersMethods.get_count(obj, 2)

    venues = LocationSerializerMin(many=True, read_only=True)

    bodies = BodySerializerMin(many=True, read_only=True)

    class Meta:
        model = Event
        fields = ('id', 'name', 'description', 'image_url',
                  'start_time', 'end_time', 'all_day', 'venues', 'bodies',
                  'interested_count', 'going_count', 'website_url')

class EventFullSerializer(serializers.ModelSerializer):
    """Serializer for Event with more information.

    Returns a nested list of followers of each status and
    detailed information on venues.
    """

    from bodies.serializer_min import BodySerializerMin
    from locations.serializers import LocationSerializer
    from locations.models import Location
    from bodies.models import Body

    interested_count = serializers.SerializerMethodField()
    get_interested_count = lambda self, obj: FollowersMethods.get_count(obj, 1)

    going_count = serializers.SerializerMethodField()
    get_going_count = lambda self, obj: FollowersMethods.get_count(obj, 2)

    interested = serializers.SerializerMethodField()
    get_interested = lambda self, obj: FollowersMethods.get_followers(obj, 1)

    going = serializers.SerializerMethodField()
    get_going = lambda self, obj: FollowersMethods.get_followers(obj, 2)

    venues = LocationSerializer(many=True, read_only=True)
    venue_names = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field='name', source='venues')
    venue_ids = serializers.PrimaryKeyRelatedField(
        many=True, read_only=False, source='venues',
        queryset=Location.objects.all(), required=False)

    bodies = BodySerializerMin(many=True, read_only=True)
    bodies_id = serializers.PrimaryKeyRelatedField(
        many=True, read_only=False, queryset=Body.objects.all(), source='bodies')

    class Meta:
        model = Event
        fields = ('id', 'name', 'description', 'image_url', 'start_time',
                  'end_time', 'all_day', 'venues', 'venue_names', 'bodies', 'bodies_id',
                  'interested_count', 'going_count', 'interested', 'going', 'venue_ids',
                  'website_url')

    def to_representation(self, instance):
        result = super().to_representation(instance)
        # Remove unnecessary fields
        result.pop('venue_ids')
        return result

    def create(self, validated_data):
        result = super().create(validated_data)
        result.created_by = self.context['request'].user.profile
        result.save()
        return result

class UserEventStatusSerializer(serializers.ModelSerializer):
    """DEPRECATED

    Serializer for UserEventStatus."""

    class Meta:
        from events.models import UserEventStatus
        model = UserEventStatus
        fields = ('id', 'event', 'user', 'status')

class EventLocationSerializer(serializers.ModelSerializer):
    """Gets event with detailed location info.

    Intended for use only with POST list.
    """

    from locations.serializers import LocationSerializer

    venues = LocationSerializer(many=True, read_only=True)

    class Meta:
        model = Event
        fields = ('id', 'name', 'venues')
