' Views for locations app '
from rest_framework import viewsets
from locations.serializers import LocationSerializer
from locations.models import Location

class LocationViewSet(viewsets.ModelViewSet):   # pylint: disable=too-many-ancestors
    ' API endpoint that allows events to be viewed or edited '
    queryset = Location.objects.all()
    serializer_class = LocationSerializer

    def get_serializer_context(self):
        return {'request': self.request}
