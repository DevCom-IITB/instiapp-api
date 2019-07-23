"""Views that don't fit anywhere else."""
from datetime import timedelta

from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.response import Response
from rest_framework import viewsets

from roles.helpers import login_required_ajax
from bodies.models import Body
from bodies.serializer_min import BodySerializerMin
from events.models import Event
from events.serializers import EventSerializer
from events.prioritizer import get_prioritized
from users.models import UserProfile
from users.models import UserTagCategory
from users.models import UserTag
from users.serializers import UserProfileSerializer
from other.serializers import NotificationSerializer
from other.serializers import UserTagCategorySerializer
from helpers.misc import query_search
from helpers.misc import users_from_tags

def get_notif_queryset(queryset):
    return queryset.unread().filter(timestamp__gte=timezone.now() - timedelta(days=7))

class OtherViewset(viewsets.ViewSet):

    @staticmethod
    def search(request):
        """EXPENSIVE: Search with query param `query` throughout the database."""
        MIN_LENGTH = 3

        req_query = request.GET.get("query")
        if not req_query or len(req_query) < MIN_LENGTH:
            return Response({"message": "No query or too short!"}, status=400)

        types = ('bodies', 'events', 'users')
        req_types = request.GET.get('types')
        if req_types:
            types = tuple(req_types.split(','))

        # Include only the types we want
        bodies, events, users = ([] for i in range(3))

        # Search bodies by name and description
        if 'bodies' in types:
            bodies = query_search(
                request, MIN_LENGTH, Body.objects, ['name', 'description'],
                'bodies', order_relevance=True)

        # Search events by name and description
        if 'events' in types:
            events = get_prioritized(query_search(
                request, MIN_LENGTH, Event.objects, ['name', 'description'], 'events')[:20], request)

        # Search users by only name: don't add anything else here
        if 'users' in types:
            users = query_search(
                request, MIN_LENGTH, UserProfile.objects.filter(active=True),
                ['name', 'ldap_id', 'roll_no'], 'profiles', order_relevance=True)[:20]

        return Response({
            "bodies": BodySerializerMin(bodies, many=True).data,
            "events": EventSerializer(events, many=True).data,
            "users": UserProfileSerializer(users, many=True).data
        })

    @classmethod
    @login_required_ajax
    def get_notifications(cls, request):
        """Get unread notifications for current user."""
        notifications = get_notif_queryset(request.user.notifications)
        return Response(NotificationSerializer(notifications, many=True).data)

    @classmethod
    @login_required_ajax
    def mark_notification_read(cls, request, pk):
        """Mark one notification as read."""
        notification = get_object_or_404(request.user.notifications, id=pk)

        # Mark as deleted if query parameter is present
        if request.GET.get("delete") is not None:
            notification.deleted = True

        notification.unread = False
        notification.save()

        return Response(status=204)

    @classmethod
    @login_required_ajax
    def mark_all_notifications_read(cls, request):
        """Mark all notifications as read."""
        request.user.notifications.mark_all_as_read()
        request.user.notifications.mark_all_as_deleted()
        return Response(status=204)

    @classmethod
    @login_required_ajax
    def get_all_user_tags(cls, request):
        """Get a list of categories of user tags with nested tags."""
        return Response(UserTagCategorySerializer(
            UserTagCategory.objects.all(), many=True).data)

    @classmethod
    @login_required_ajax
    def get_user_tags_reach(cls, request):
        """Get reach of selected user tags."""
        tags = UserTag.objects.filter(id__in=request.data)
        return Response({'count': users_from_tags(tags).filter(active=True).count()})
