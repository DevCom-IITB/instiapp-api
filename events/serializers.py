"""Serializers for Event."""
from rest_framework import serializers
from django.db.models import Count
from django.db.models import Prefetch
from django.db.models import Q
from events.models import Event
from events.models import UserEventStatus
from users.models import UserTag

def get_followers(obj, status):
    """Get serialized followers with specified status."""
    from users.serializers import UserProfileSerializer
    followers = [ues.user for ues in obj.ues.all() if ues.status == status]
    return UserProfileSerializer(followers, many=True).data

def get_user_ues(self, obj):  # pylint: disable=unused-argument
    """Get UES for current user or 0."""

    # Check if the uues annotation is available
    if hasattr(obj, 'uues'):
        return obj.uues[0].status if obj.uues else 0

    return None

class EventSerializer(serializers.ModelSerializer):
    """Serializer for Event.

    This serializer returns only the count of followers in
    each category, i.e. interested and going and minimal
    venue info. Use `EventFullSerializer` if you want information
    on individual users and venues.
    """

    from locations.serializers import LocationSerializerMin
    from bodies.serializer_min import BodySerializerMin
    from achievements.serializers import OfferedAchievementSerializer

    interested_count = serializers.IntegerField(read_only=True)
    going_count = serializers.IntegerField(read_only=True)

    user_ues = serializers.SerializerMethodField()
    get_user_ues = get_user_ues  # pylint: disable=self-assigning-variable

    venues = LocationSerializerMin(many=True, read_only=True)

    bodies = BodySerializerMin(many=True, read_only=True)

    offered_achievements = OfferedAchievementSerializer(many=True, read_only=True)

    class Meta:
        model = Event
        fields = ('id', 'str_id', 'name', 'description', 'image_url',
                  'start_time', 'end_time', 'all_day', 'venues', 'bodies',
                  'interested_count', 'going_count', 'website_url', 'weight',
                  'user_ues', 'offered_achievements')

    @staticmethod
    def setup_eager_loading(queryset, request, extra_prefetch=None):
        """Perform necessary eager loading of data."""

        # Get the fields to be prefetched
        fields = ['bodies', 'venues', 'user_tags', 'offered_achievements']

        # Add prefetch for user_ues
        if request.user.is_authenticated and hasattr(request.user, 'profile'):
            user_query = UserEventStatus.objects.filter(user_id=request.user.profile.id)
            fields.append(Prefetch('ues', queryset=user_query, to_attr='uues'))

        # Add extra prefetch fields
        if extra_prefetch:
            fields += extra_prefetch

        queryset = queryset.prefetch_related(*fields)

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
    from achievements.serializers import OfferedAchievementSerializer
    from locations.models import Location
    from bodies.models import Body

    interested_count = serializers.IntegerField(read_only=True)
    going_count = serializers.IntegerField(read_only=True)

    interested = serializers.SerializerMethodField()
    get_interested = lambda self, obj: get_followers(obj, 1)

    going = serializers.SerializerMethodField()
    get_going = lambda self, obj: get_followers(obj, 2)

    user_ues = serializers.SerializerMethodField()
    get_user_ues = get_user_ues  # pylint: disable=self-assigning-variable

    venues = LocationSerializerMin(many=True, read_only=True)
    venue_names = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field='name', source='venues')
    venue_ids = serializers.PrimaryKeyRelatedField(
        many=True, read_only=False, source='venues',
        queryset=Location.objects.all(), required=False)

    bodies = BodySerializerMin(many=True, read_only=True)
    bodies_id = serializers.PrimaryKeyRelatedField(
        many=True, read_only=False, queryset=Body.objects.all(), source='bodies')

    user_tags = serializers.PrimaryKeyRelatedField(
        many=True, read_only=False, queryset=UserTag.objects.all(), default=[])

    offered_achievements = OfferedAchievementSerializer(many=True, read_only=True)

    class Meta:
        model = Event
        fields = ('id', 'str_id', 'name', 'description', 'image_url', 'start_time',
                  'end_time', 'all_day', 'venues', 'venue_names', 'bodies', 'bodies_id',
                  'interested_count', 'going_count', 'interested', 'going', 'venue_ids',
                  'website_url', 'user_ues', 'notify', 'user_tags', 'offered_achievements')

    @staticmethod
    def setup_eager_loading(queryset, request):
        """Calls the method in EventSerializer adding ues__user"""
        return EventSerializer.setup_eager_loading(
            queryset, request, extra_prefetch=['ues', 'ues__user'])

    def to_representation(self, instance):
        result = super().to_representation(instance)
        # Remove unnecessary fields
        result.pop('venue_ids')
        return result

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user.profile
        return super().create(validated_data)
