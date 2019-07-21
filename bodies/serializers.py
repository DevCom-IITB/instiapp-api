"""Serializers for Body and BodyChildRelation."""
from rest_framework import serializers
from django.db.models import Count
from django.db.models import Q
from events.prioritizer import get_fresh_prioritized_events
from bodies.models import Body
from bodies.serializer_min import BodySerializerMin
from helpers.misc import sort_by_field

class BodySerializer(serializers.ModelSerializer):
    """Serializer for Body."""

    from roles.serializers import RoleSerializerMin

    followers_count = serializers.IntegerField(read_only=True)
    user_follows = serializers.BooleanField(read_only=True)

    parents = serializers.SerializerMethodField()
    children = serializers.SerializerMethodField()

    events = serializers.SerializerMethodField()
    roles = RoleSerializerMin(many=True, read_only=True)

    class Meta:
        model = Body
        fields = ('id', 'str_id', 'name', 'short_description', 'description',
                  'image_url', 'children', 'parents', 'events', 'followers_count',
                  'user_follows', 'roles', 'website_url', 'blog_url', 'cover_url')

    @staticmethod
    def get_parents(obj):
        """Gets a min serialized parents of a Body."""
        parents = obj.parents.prefetch_related('parent')
        parents = sort_by_field(
            parents, 'parent__followers', reverse=True,
            filt=Q(parent__followers__active=True))
        return [BodySerializerMin(x.parent).data for x in parents.all()]

    @staticmethod
    def get_children(obj):
        """Gets a min serialized children of a Body."""
        children = obj.children.prefetch_related('child')
        children = sort_by_field(
            children, 'child__followers', reverse=True,
            filt=Q(child__followers__active=True))
        return [BodySerializerMin(x.child).data for x in children.all()]

    def get_events(self, obj):
        """Gets filtred events."""
        from events.serializers import EventSerializer
        return EventSerializer(get_fresh_prioritized_events(
            obj.events, self.context['request'], delta=365), many=True, read_only=True).data

    @staticmethod
    def setup_eager_loading(queryset, request):
        """Perform necessary eager loading of data."""

        # Prefetch body child relations
        queryset = queryset.prefetch_related('parents', 'children')

        # Annotate followers count
        followers_count = Count('followers', filter=Q(followers__active=True))

        # Annotate user_follows
        userid = request.user.profile.id if request.user.is_authenticated else None
        user_follows = Count('followers', filter=Q(followers__id=userid))

        queryset = queryset.annotate(followers_count=followers_count, user_follows=user_follows)

        return queryset
