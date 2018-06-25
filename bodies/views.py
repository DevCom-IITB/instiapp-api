"""Views for bodies app."""
from uuid import UUID
from rest_framework import viewsets
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from bodies.serializers_followers import BodyFollowersSerializer
from bodies.serializers import BodySerializer
from bodies.serializer_min import BodySerializerMin
from bodies.models import Body
from roles.helpers import user_has_privilege
from roles.helpers import forbidden_no_privileges
from roles.helpers import login_required_ajax
from roles.helpers import insti_permission_required

class BodyViewSet(viewsets.ModelViewSet):   # pylint: disable=too-many-ancestors
    """Body"""
    queryset = Body.objects.all()
    serializer_class = BodySerializer

    def get_serializer_context(self):
        return {'request': self.request}

    @classmethod
    def list(cls, request): #pylint: disable=unused-argument
        queryset = Body.objects.all()
        serializer = BodySerializerMin(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk):
        """Get Body.
        Retrieve by `uuid` or `str_id`."""

        # Try UUID or fall back to str_id
        try:
            UUID(pk, version=4)
            body = get_object_or_404(Body.objects.all(), id=pk)
        except ValueError:
            body = get_object_or_404(Body.objects.all(), str_id=pk)

        # Add user_follows to response
        serialized = BodySerializer(body, context={'request': request}).data
        serialized['user_follows'] = request.user.is_authenticated and \
            body in request.user.profile.followed_bodies.all()
        return Response(serialized)

    @insti_permission_required('AddB')
    def create(self, request):
        """Create Body.
        Needs the `AddB` Institute Role permission."""

        return super().create(request)

    @login_required_ajax
    def update(self, request, pk):
        """Update Body.
        Needs the `UpdB` permission."""

        if not user_has_privilege(request.user.profile, pk, 'UpdB'):
            return forbidden_no_privileges()
        return super().update(request, pk)

    @insti_permission_required('DelB')
    def destroy(self, request, pk):
        """Delete Body.
        Needs the `DelB` institute permission."""

        return super().destroy(request, pk)

class BodyFollowersViewSet(viewsets.ModelViewSet):   # pylint: disable=too-many-ancestors
    """List followers of body."""
    queryset = Body.objects.all()
    serializer_class = BodyFollowersSerializer
