' Views for events app '
from uuid import UUID
from rest_framework.response import Response
from rest_framework import viewsets
from events.serializers import EventFullSerializer, EventLocationSerializer
from events.models import Event

class EventViewSet(viewsets.ModelViewSet):   # pylint: disable=too-many-ancestors
    ' API endpoint that allows events to be viewed or edited '
    queryset = Event.objects.all()
    serializer_class = EventFullSerializer

    def locations(self, request):
        ' Endpoint to return event locations of all POSTed events'
        try:
            [UUID(x, version=4) for x in request.data]
        except ValueError:
            return Response("Bad Request", status=400)

        locs = EventLocationSerializer(Event.objects.filter(pk__in=request.data), many=True)
        return Response(locs.data)
