"""Serializers for Body and BodyChildRelation."""
from rest_framework import serializers
from django.db.models import Count
from events.prioritizer import get_r_fresh_prioritized_events
from bodies.models import Body
from bodies.serializer_min import BodySerializerMin

class BodySerializer(serializers.ModelSerializer):
    """Serializer for Body."""

    from roles.serializers import RoleSerializerMin

    followers_count = serializers.IntegerField()

    parents = serializers.SerializerMethodField()
    children = serializers.SerializerMethodField()

    events = serializers.SerializerMethodField()
    roles = RoleSerializerMin(many=True, read_only=True)

    class Meta:
        model = Body
        fields = ('id', 'str_id', 'name', 'short_description', 'description',
                  'image_url', 'children', 'parents', 'events', 'followers_count',
                  'roles', 'website_url', 'blog_url', 'cover_url')

    @staticmethod
    def get_parents(obj):
        """Gets a min serialized parents of a Body."""
        return [BodySerializerMin(x.parent).data for x in obj.parents.all()]

    @staticmethod
    def get_children(obj):
        """Gets a min serialized children of a Body."""
        return [BodySerializerMin(x.child).data for x in obj.children.all()]

    def get_events(self, obj):
        """Gets filtred events."""
        from events.serializers import EventSerializer
        return EventSerializer(get_r_fresh_prioritized_events(
            obj.events, self.context['request']), many=True, read_only=True).data

    @staticmethod
    def setup_eager_loading(queryset):
        """Perform necessary eager loading of data."""
        queryset = queryset.prefetch_related(
            'parents', 'children', 'parents__parent', 'children__child')

        # Prefetch counts
        followers_count = Count('followers')
        queryset = queryset.annotate(followers_count=followers_count)

        return queryset
