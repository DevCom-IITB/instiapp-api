' Views for bodies app '
from rest_framework import viewsets
from bodies.serializers import BodySerializer, BodyFollowersSerializer
from bodies.models import Body

class BodyViewSet(viewsets.ModelViewSet):   # pylint: disable=too-many-ancestors
    ' API endpoint that allows bodies to be viewed or edited '
    queryset = Body.objects.all()
    serializer_class = BodySerializer

    def get_serializer_context(self):
        return {'request': self.request}

class BodyFollowersViewSet(viewsets.ModelViewSet):   # pylint: disable=too-many-ancestors
    ' API endpoint that lists followers of bodies '
    queryset = Body.objects.all()
    serializer_class = BodyFollowersSerializer

    def get_serializer_context(self):
        return {'request': self.request}
