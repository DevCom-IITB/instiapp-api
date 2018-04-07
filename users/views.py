"""Views for users app."""
from uuid import UUID
from rest_framework import viewsets
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from events.models import UserEventStatus
from events.models import Event
from events.serializers import EventSerializer
from users.serializer_full import UserProfileFullSerializer
from users.models import UserProfile
from roles.helpers import login_required_ajax

class UserProfileViewSet(viewsets.ModelViewSet):   # pylint: disable=too-many-ancestors
    """API endpoint that allows users to be viewed or edited."""
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileFullSerializer

    def get_serializer_context(self):
        return {'request': self.request}

    def retrieve(self, request, pk):
        try:
            UUID(pk, version=4)
            return super().retrieve(self, request, pk)
        except ValueError:
            profile = get_object_or_404(UserProfile.objects.all(), ldap_id=pk)
            return Response(UserProfileFullSerializer(
                profile, context={'request': request}).data)

    @login_required_ajax
    def retrieve_me(self, request):
        """Retrieves the logged-in user's profile."""
        return Response(UserProfileFullSerializer(
            request.user.profile, context=self.get_serializer_context()).data)

    @login_required_ajax
    def update_me(self, request):
        """Update the logged-in user's profile."""
        serializer = UserProfileFullSerializer(
            request.user.profile, data=request.data, context=self.get_serializer_context())
        if not serializer.is_valid():
            return Response({'error': 'validation failed'}, status=400)
        serializer.save()
        return Response(serializer.data)

    @classmethod
    @login_required_ajax
    def set_ues_me(cls, request, event_pk):
        """Creates or updates a UserEventStatus for the current user."""

        # Get status from query paramter
        status = request.GET.get('status')
        if status is None:
            return Response({"message" : "status is required"}, status=400)

        # Create new UserEventStatus if not existing
        if not request.user.profile.followed_events.filter(id=event_pk).exists():
            get_event = get_object_or_404(Event.objects.all(), pk=event_pk)
            UserEventStatus.objects.create(
                event=get_event, user=request.user.profile, status=status)
            return Response(status=204)

        # Update existing UserEventStatus
        ues = UserEventStatus.objects.get(event__id=event_pk, user=request.user.profile)
        ues.status = status
        ues.save()
        return Response(status=204)

    @classmethod
    @login_required_ajax
    def get_my_events(cls, request):
        """Gets events created by current user."""
        events = Event.objects.filter(created_by=request.user.profile)
        serializer = EventSerializer(events, many=True)
        return Response(serializer.data)
