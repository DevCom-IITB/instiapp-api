' Views for events app '
from rest_framework import viewsets
from events.serializers import EventSerializer
from events.models import Event

class EventViewSet(viewsets.ModelViewSet):   # pylint: disable=too-many-ancestors
    ' API endpoint that allows events to be viewed or edited '
    queryset = Event.objects.all()
    serializer_class = EventSerializer

    def get_serializer_context(self):
        return {'request': self.request}
