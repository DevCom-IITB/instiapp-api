"""Views for bodies app."""
from rest_framework import viewsets
from rest_framework.response import Response
from bodies.serializers_followers import BodyFollowersSerializer
from bodies.serializers import BodySerializer
from bodies.serializers import BodySerializerMin
from bodies.models import Body
from roles.helpers import user_has_privilege
from roles.helpers import user_has_insti_privilege
from roles.helpers import forbidden_no_privileges
from roles.helpers import login_required_ajax

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

    @login_required_ajax
    def create(self, request):
        """Creates body if the user has institute privileges."""
        if not user_has_insti_privilege(request.user.profile, 'AddB'):
            return forbidden_no_privileges()
        return super().create(request)

    @login_required_ajax
    def update(self, request, pk):
        """Updates an existing body if the user has privileges."""
        if not user_has_privilege(request.user.profile, pk, 'UpdB'):
            return forbidden_no_privileges()
        return super().update(request, pk)

    @login_required_ajax
    def destroy(self, request, pk):
        """Deletes an existing body if the user has privileges."""
        if not user_has_insti_privilege(request.user.profile, 'DelB'):
            return forbidden_no_privileges()
        return super().destroy(request, pk)

class BodyFollowersViewSet(viewsets.ModelViewSet):   # pylint: disable=too-many-ancestors
    """API endpoint that lists followers of bodies."""
    queryset = Body.objects.all()
    serializer_class = BodyFollowersSerializer
