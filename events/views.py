"""Views for events app."""
from uuid import UUID
from rest_framework.response import Response
from rest_framework import viewsets
from django.shortcuts import get_object_or_404
from events.prioritizer import get_fresh_prioritized_events
from events.serializers import EventSerializer
from events.serializers import EventFullSerializer
from events.models import Event
from roles.helpers import user_has_privilege
from roles.helpers import login_required_ajax
from roles.helpers import forbidden_no_privileges, diff_set
from locations.helpers import create_unreusable_locations

class EventViewSet(viewsets.ModelViewSet):   # pylint: disable=too-many-ancestors
    """Event"""

    queryset = Event.objects.all()
    serializer_class = EventFullSerializer

    def get_serializer_context(self):
        return {'request': self.request}

    def retrieve(self, request, pk):
        """Get Event.
        Get by `uuid` or `str_id`"""

        try:
            UUID(pk, version=4)
            return super().retrieve(self, request, pk)
        except ValueError:
            event = get_object_or_404(Event.objects.all(), str_id=pk)
            return Response(EventFullSerializer(event).data)

    def list(self, request): #pylint: disable=unused-argument
        """List Events.
        List fresh events prioritized for the current user."""
        queryset = get_fresh_prioritized_events(self.queryset, request)

        serializer = EventSerializer(queryset, many=True)
        data = serializer.data

        return Response({'count':len(data), 'data':data})

    @login_required_ajax
    def create(self, request):
        """Create Event.
        Needs `AddE` permission for each body to be associated."""

        if all([user_has_privilege(request.user.profile, id, 'AddE')
                for id in request.data['bodies_id']]):

            # Fill in ids of venues
            request.data['venue_ids'] = create_unreusable_locations(request.data['venue_names'])
            return super().create(request)

        return forbidden_no_privileges()

    @login_required_ajax
    def update(self, request, pk):
        """Update Event.
        Needs BodyRole with `UpdE` for at least one associated body.
        Disassociating bodies from the event requires the `DelE`
        permission and associating needs `AddE`"""

        # Get difference in bodies
        event = Event.objects.get(id=pk)
        old_bodies_id = [str(x.id) for x in event.bodies.all()]
        new_bodies_id = request.data['bodies_id']
        added_bodies = diff_set(new_bodies_id, old_bodies_id)
        removed_bodies = diff_set(old_bodies_id, new_bodies_id)

        # Check if user can add events for new bodies
        can_add_events = all(
            [user_has_privilege(request.user.profile, id, 'AddE') for id in added_bodies])

        # Check if user can remove events for removed
        can_del_events = all(
            [user_has_privilege(request.user.profile, id, 'DelE') for id in removed_bodies])

        # Check if the user can update event for any of the old bodies
        can_update = any(
            [user_has_privilege(request.user.profile, id, 'UpdE') for id in old_bodies_id])

        if can_add_events and can_del_events and can_update:
            # Create added unreusable venues, unlink deleted ones
            old_venue_names = [x.name for x in event.venues.all()]
            new_venue_names = request.data['venue_names']
            added_venues = diff_set(new_venue_names, old_venue_names)
            common_venues = list(set(old_venue_names).intersection(new_venue_names))

            common_venue_ids = [str(x.id) for x in event.venues.filter(name__in=common_venues)]
            added_venue_ids = create_unreusable_locations(added_venues)

            request.data['venue_ids'] = added_venue_ids + common_venue_ids

            return super().update(request, pk)

        return forbidden_no_privileges()


    @login_required_ajax
    def destroy(self, request, pk):
        """Delete Event.
        Needs `DelE` permission for all associated bodies."""

        event = Event.objects.get(id=pk)
        if all([user_has_privilege(request.user.profile, str(body.id), 'DelE')
                for body in event.bodies.all()]):
            return super().destroy(request, pk)

        return forbidden_no_privileges()
