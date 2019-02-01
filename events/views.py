"""Views for events app."""
from uuid import UUID
from rest_framework.response import Response
from rest_framework import viewsets
from django.shortcuts import get_object_or_404
from events.prioritizer import get_fresh_prioritized_events
from events.prioritizer import get_prioritized
from events.serializers import EventSerializer
from events.serializers import EventFullSerializer
from events.models import Event
from roles.helpers import user_has_privilege
from roles.helpers import login_required_ajax
from roles.helpers import forbidden_no_privileges, diff_set
from locations.helpers import create_unreusable_locations

class EventViewSet(viewsets.ModelViewSet):
    """Event"""

    queryset = Event.objects
    serializer_class = EventFullSerializer

    def get_serializer_context(self):
        return {'request': self.request}

    def retrieve(self, request, pk):
        """Get Event.
        Get by `uuid` or `str_id`"""

        self.queryset = EventFullSerializer.setup_eager_loading(self.queryset, request)
        event = self.get_event(pk)
        serialized = EventFullSerializer(event, context={'request': request}).data

        return Response(serialized)

    def list(self, request):
        """List Events.
        List fresh events prioritized for the current user."""

        # Check for date filtered query params
        start = request.GET.get('start')
        end = request.GET.get('end')

        if start is not None and end is not None:
            # Try date-filtered if we have the params
            queryset = get_prioritized(self.queryset.filter(
                start_time__range=(start, end)), request)
        else:
            # Respond with recent events
            queryset = get_fresh_prioritized_events(self.queryset, request)

        serializer = EventSerializer(queryset, many=True, context={'request': request})
        data = serializer.data

        return Response({'count': len(data), 'data': data})

    @login_required_ajax
    def create(self, request):
        """Create Event.
        Needs `AddE` permission for each body to be associated."""

        # Prevent events without any body
        if 'bodies_id' not in request.data or not request.data['bodies_id']:
            return forbidden_no_privileges()

        # Check privileges for all bodies
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

        # Prevent events without any body
        if 'bodies_id' not in request.data or not request.data['bodies_id']:
            return forbidden_no_privileges()

        # Get the event currently in database
        event = self.get_event(pk)

        # Check if difference in bodies is valid
        if not can_update_bodies(request.data['bodies_id'], event, request.user.profile):
            return forbidden_no_privileges()

        # Create added unreusable venues, unlink deleted ones
        request.data['venue_ids'] = get_update_venue_ids(request.data['venue_names'], event)

        return super().update(request, pk)

    @login_required_ajax
    def destroy(self, request, pk):
        """Delete Event.
        Needs `DelE` permission for all associated bodies."""

        event = self.get_event(pk)
        if all([user_has_privilege(request.user.profile, str(body.id), 'DelE')
                for body in event.bodies.all()]):
            return super().destroy(request, pk)

        return forbidden_no_privileges()

    def get_event(self, pk):
        """Get an event from pk uuid or strid."""
        try:
            UUID(pk, version=4)
            return get_object_or_404(self.queryset, id=pk)
        except ValueError:
            return get_object_or_404(self.queryset, str_id=pk)


def can_update_bodies(new_bodies_id, event, profile):
    """Check if the user is permitted to change the event bodies to ones given."""

    # Get current and difference in body ids
    old_bodies_id = [str(x.id) for x in event.bodies.all()]
    added_bodies = diff_set(new_bodies_id, old_bodies_id)
    removed_bodies = diff_set(old_bodies_id, new_bodies_id)

    # Check if user can add events for new bodies
    can_add_events = all(
        [user_has_privilege(profile, bid, 'AddE') for bid in added_bodies])

    # Check if user can remove events for removed
    can_del_events = all(
        [user_has_privilege(profile, bid, 'DelE') for bid in removed_bodies])

    # Check if the user can update event for any of the old bodies
    can_update = any(
        [user_has_privilege(profile, bid, 'UpdE') for bid in old_bodies_id])

    return can_add_events and can_del_events and can_update

def get_update_venue_ids(venue_names, event):
    """Get venue ids with minimal object creation for updating event."""

    old_venue_names = [x.name for x in event.venues.all()]
    new_venue_names = venue_names
    added_venues = diff_set(new_venue_names, old_venue_names)
    common_venues = list(set(old_venue_names).intersection(new_venue_names))

    common_venue_ids = [str(x.id) for x in event.venues.filter(name__in=common_venues)]
    added_venue_ids = create_unreusable_locations(added_venues)

    return added_venue_ids + common_venue_ids
