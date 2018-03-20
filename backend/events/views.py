"""Views for events app."""
from uuid import UUID
from rest_framework.response import Response
from rest_framework import viewsets
from events.serializers import EventSerializer
from events.serializers import EventFullSerializer
from events.serializers import EventLocationSerializer
from events.serializers import UserEventStatusSerializer
from events.models import Event
from events.models import UserEventStatus
from roles.helpers import user_has_privilege
from roles.helpers import login_required_ajax
from roles.helpers import forbidden_no_privileges, diff_set
from locations.helpers import create_unreusable_locations

class EventViewSet(viewsets.ModelViewSet):   # pylint: disable=too-many-ancestors
    """API endpoint that allows events to be viewed or edited"""

    queryset = Event.objects.all()
    serializer_class = EventFullSerializer

    def get_serializer_context(self):
        return {'request': self.request}

    @classmethod
    def locations(cls, request):
        """Endpoint to return event locations of all POSTed events."""
        try:
            [UUID(x, version=4) for x in request.data]
        except ValueError:
            return Response("Bad Request", status=400)

        locs = EventLocationSerializer(Event.objects.filter(pk__in=request.data), many=True)
        return Response(locs.data)

    @classmethod
    def list(cls, request): #pylint: disable=unused-argument
        queryset = Event.objects.all()
        serializer = EventSerializer(queryset, many=True)
        return Response({'count':len(serializer.data), 'data':serializer.data})

    @login_required_ajax
    def create(self, request):
        if all([user_has_privilege(request.user.profile, id, 'AddE')
                for id in request.data['bodies_id']]):

            # Fill in ids of venues
            request.data['venue_ids'] = create_unreusable_locations(request.data['venue_names'])
            return super().create(request)

        return forbidden_no_privileges()

    @login_required_ajax
    def update(self, request, pk):
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
        event = Event.objects.get(id=pk)
        if all([user_has_privilege(request.user.profile, str(body.id), 'DelE')
                for body in event.bodies.all()]):
            return super().destroy(request, pk)

        return forbidden_no_privileges()

class UserEventStatusViewSet(viewsets.ModelViewSet):   # pylint: disable=too-many-ancestors
    """API endpoint that allows user-event statuses to be viewed or edited"""
    queryset = UserEventStatus.objects.all()
    serializer_class = UserEventStatusSerializer
