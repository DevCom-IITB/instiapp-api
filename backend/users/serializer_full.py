"""Full serializer for UserProfile with detailed information and events."""
from rest_framework import serializers
from users.models import UserProfile
from roles.serializers import RoleSerializer
from roles.serializers import InstituteRoleSerializer

class UserProfileFullSerializer(serializers.ModelSerializer):
    """Full serializer for UserProfile with detailed information and events."""

    from bodies.serializer_min import BodySerializerMin
    from bodies.models import Body

    events_interested = serializers.SerializerMethodField()
    get_events_interested = lambda self, obj: self.get_events(obj, 1)

    events_going = serializers.SerializerMethodField()
    get_events_going = lambda self, obj: self.get_events(obj, 2)

    followed_bodies = BodySerializerMin(many=True, read_only=True)
    followed_bodies_id = serializers.PrimaryKeyRelatedField(
        many=True, read_only=False, queryset=Body.objects.all(), source='followed_bodies')

    roles = RoleSerializer(many=True, read_only=True)
    institute_roles = InstituteRoleSerializer(many=True, read_only=True)

    class Meta:
        model = UserProfile
        fields = ('id', 'name', 'profile_pic', 'events_interested',
                  'events_going', 'email', 'year', 'roll_no', 'contact_no',
                  'about', 'followed_bodies', 'followed_bodies_id', 'roles',
                  'institute_roles', 'website_url', 'ldap_id')

    @staticmethod
    def get_events(obj, status):
        """Returns serialized events for given status."""
        from events.serializers import EventSerializer
        return EventSerializer(obj.followed_events.filter(ues__status=status), many=True).data
