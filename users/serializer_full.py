"""Full serializer for UserProfile with detailed information and events."""
from django.conf import settings
from rest_framework import serializers
from events.prioritizer import get_fresh_prioritized_events
from users.models import UserProfile
from roles.serializers import RoleSerializer
from roles.serializers import RoleSerializerMinAlt
from roles.serializers import InstituteRoleSerializer

class UserProfileFullSerializer(serializers.ModelSerializer):
    """Full serializer for UserProfile with detailed information and events."""

    from bodies.serializer_min import BodySerializerMin
    from bodies.models import Body

    email = serializers.SerializerMethodField()
    contact_no = serializers.SerializerMethodField()

    events_interested = serializers.SerializerMethodField()
    get_events_interested = lambda self, obj: self.get_events(obj, 1)

    events_going = serializers.SerializerMethodField()
    get_events_going = lambda self, obj: self.get_events(obj, 2)

    followed_bodies = BodySerializerMin(many=True, read_only=True)
    followed_bodies_id = serializers.PrimaryKeyRelatedField(
        many=True, read_only=False, queryset=Body.objects.all(), source='followed_bodies')

    roles = RoleSerializer(many=True, read_only=True)
    former_roles = RoleSerializerMinAlt(many=True, read_only=True)
    institute_roles = InstituteRoleSerializer(many=True, read_only=True)

    class Meta:
        model = UserProfile
        fields = ('id', 'name', 'profile_pic', 'events_interested',
                  'events_going', 'email', 'roll_no', 'contact_no',
                  'about', 'followed_bodies', 'followed_bodies_id', 'roles',
                  'institute_roles', 'website_url', 'ldap_id', 'hostel', 'former_roles')

    def get_email(self, obj):
        """Gets the email only if a user is logged in."""
        if self.context['request'].user.is_authenticated:
            return obj.email
        return 'N/A'

    def get_contact_no(self, obj):
        """Gets contact no only if a user is logged in."""
        if self.context['request'].user.is_authenticated:
            return obj.contact_no
        return 'N/A'

    def get_events(self, obj, status):
        """Returns serialized events for given status."""
        from events.serializers import EventSerializer
        request = self.context['request']
        return EventSerializer(get_fresh_prioritized_events(
            obj.followed_events.filter(ues__status=status), request, delta=60), many=True).data

    @staticmethod
    def setup_eager_loading(queryset):
        """Perform necessary eager loading of data."""
        queryset = queryset.prefetch_related(
            'followed_bodies', 'roles', 'roles__body', 'roles__body__children', 'roles__users',
            'former_roles', 'former_roles__body')
        return queryset

    def to_representation(self, instance):
        return settings.USER_PROFILE_FULL_SERIALIZER_TRANSFORM(
            super().to_representation(instance))
