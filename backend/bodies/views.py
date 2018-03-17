"""Views for bodies app."""
from rest_framework import viewsets
from rest_framework.response import Response
from bodies.serializers_followers import BodyFollowersSerializer
from bodies.serializers import BodySerializer
from bodies.serializers import BodySerializerMin
from bodies.models import Body

class BodyViewSet(viewsets.ModelViewSet):   # pylint: disable=too-many-ancestors
    """API endpoint that allows bodies to be viewed or edited."""
    queryset = Body.objects.all()
    serializer_class = BodySerializer

    @classmethod
    def list(cls, request): #pylint: disable=unused-argument
        """Override list method"""
        queryset = Body.objects.all()
        serializer = BodySerializerMin(queryset, many=True)
        return Response(serializer.data)

class BodyFollowersViewSet(viewsets.ModelViewSet):   # pylint: disable=too-many-ancestors
    """API endpoint that lists followers of bodies."""
    queryset = Body.objects.all()
    serializer_class = BodyFollowersSerializer
