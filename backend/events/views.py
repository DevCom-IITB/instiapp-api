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
from roles.helpers import forbidden_no_privileges

class EventViewSet(viewsets.ModelViewSet):   # pylint: disable=too-many-ancestors
    """API endpoint that allows events to be viewed or edited"""

    queryset = Event.objects.all()
    serializer_class = EventFullSerializer

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
        """Override list method"""
        queryset = Event.objects.all()
        serializer = EventSerializer(queryset, many=True)
        return Response({'count':len(serializer.data), 'data':serializer.data})

    def create(self, request):
        """Create a new event if the user has privileges."""
        for bodyid in request.data['bodies_id']:
            if not user_has_privilege(request.user.profile, bodyid, 'AddE'):
                return forbidden_no_privileges()
        return super().create(request)


class UserEventStatusViewSet(viewsets.ModelViewSet):   # pylint: disable=too-many-ancestors
    """API endpoint that allows user-event statuses to be viewed or edited"""
    queryset = UserEventStatus.objects.all()
    serializer_class = UserEventStatusSerializer
