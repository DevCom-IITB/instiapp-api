"""Serializers for Event."""
from rest_framework import serializers
from django.db.models import Count
from django.db.models import Q
from events.models import Event

class FollowersMethods:
    """Helper methods for followers."""

    @staticmethod
    def get_followers(obj, status):
        """Get serialized followers with specified status."""
        from users.serializers import UserProfileSerializer
        followers = [ues.user for ues in obj.ues.all() if ues.status == status]
        return UserProfileSerializer(followers, many=True).data

    @staticmethod
    def get_user_ues(slf, obj):
        """Get UES for current user or 0."""
        # May not always want this
        if 'request' not in slf.context:
            return None

        request = slf.context['request']
        profile = request.user.profile
        if request.user.is_authenticated:
            ues = [ues.status for ues in obj.ues.all() if ues.user == profile]
            return ues[0] if ues else 0

class EventSerializer(serializers.ModelSerializer):
    """Serializer for Event.

    This serializer returns only the count of followers in
    each category, i.e. interested and going and minimal
    venue info. Use `EventFullSerializer` if you want information
    on individual users and venues.
    """

    from locations.serializers import LocationSerializerMin
    from bodies.serializer_min import BodySerializerMin

    interested_count = serializers.IntegerField(read_only=True)
    going_count = serializers.IntegerField(read_only=True)

    user_ues = serializers.SerializerMethodField()
    get_user_ues = FollowersMethods.get_user_ues

    venues = LocationSerializerMin(many=True, read_only=True)

    bodies = BodySerializerMin(many=True, read_only=True)

    class Meta:
        model = Event
        fields = ('id', 'str_id', 'name', 'description', 'image_url',
                  'start_time', 'end_time', 'all_day', 'venues', 'bodies',
                  'interested_count', 'going_count', 'website_url', 'weight',
                  'user_ues')

    @staticmethod
    def setup_eager_loading(queryset):
        """Perform necessary eager loading of data.
        To be used for EventFullSerializer as well."""
        queryset = queryset.prefetch_related('bodies', 'venues', 'ues', 'ues__user')

        # Prefetch counts
        interested_count = Count('followers', distinct=True, filter=Q(ues__status=1))
        going_count = Count('followers', distinct=True, filter=Q(ues__status=2))
        queryset = queryset.annotate(interested_count=interested_count).annotate(going_count=going_count)

        return queryset

class EventFullSerializer(serializers.ModelSerializer):
    """Serializer for Event with more information.

    Returns a nested list of followers of each status and
    detailed information on venues.
    """

    from bodies.serializer_min import BodySerializerMin
    from locations.serializers import LocationSerializerMin
    from locations.models import Location
    from bodies.models import Body

    interested_count = serializers.IntegerField(read_only=True)
    going_count = serializers.IntegerField(read_only=True)

    interested = serializers.SerializerMethodField()
    get_interested = lambda self, obj: FollowersMethods.get_followers(obj, 1)

    going = serializers.SerializerMethodField()
    get_going = lambda self, obj: FollowersMethods.get_followers(obj, 2)

    user_ues = serializers.SerializerMethodField()
    get_user_ues = FollowersMethods.get_user_ues

    venues = LocationSerializerMin(many=True, read_only=True)
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
        fields = ('id', 'str_id', 'name', 'description', 'image_url', 'start_time',
                  'end_time', 'all_day', 'venues', 'venue_names', 'bodies', 'bodies_id',
                  'interested_count', 'going_count', 'interested', 'going', 'venue_ids',
                  'website_url', 'user_ues')

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
