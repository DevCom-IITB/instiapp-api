"""Views for bodies app."""
from uuid import UUID
from rest_framework import viewsets
from rest_framework.response import Response
from django.db.models import Q
from django.shortcuts import get_object_or_404

from bodies.serializers_followers import BodyFollowersSerializer
from bodies.serializers import BodySerializer
from bodies.serializer_min import BodySerializerMin
from bodies.models import Body
from roles.helpers import user_has_privilege
from roles.helpers import forbidden_no_privileges
from roles.helpers import login_required_ajax
from roles.helpers import insti_permission_required
from helpers.misc import sort_by_field

class BodyViewSet(viewsets.ModelViewSet):
    """Body"""
    queryset = Body.objects
    serializer_class = BodySerializer

    def get_serializer_context(self):
        return {'request': self.request}

    @staticmethod
    def list(request):
        queryset = Body.objects.all()
        queryset = sort_by_field(queryset, 'followers', reverse=True, filt=Q(followers__active=True))
        serializer = BodySerializerMin(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk):
        """Get Body.
        Retrieve by `uuid` or `str_id`."""

        # Prefetch and annotate data
        self.queryset = BodySerializer.setup_eager_loading(self.queryset, request)

        # Try UUID or fall back to str_id
        body = self.get_body(pk)

        # Serialize the body
        serialized = BodySerializer(body, context={'request': request}).data
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

    @login_required_ajax
    def follow(self, request, pk):
        """Follow or unfollow a body {?action}=0,1"""

        body = self.get_body(pk)

        # Get query param
        value = request.GET.get("action")
        if value is None:
            return Response({"message": "{?action} is required"}, status=400)

        # Check possible actions
        if value == "0":
            request.user.profile.followed_bodies.remove(body)
        elif value == "1":
            request.user.profile.followed_bodies.add(body)
        else:
            return Response({"message": "Invalid Action"}, status=400)

        return Response(status=204)

    def get_body(self, pk):
        """Get a body from pk uuid or strid."""
        try:
            UUID(pk, version=4)
            return get_object_or_404(self.queryset, id=pk)
        except ValueError:
            return get_object_or_404(self.queryset, str_id=pk)

class BodyFollowersViewSet(viewsets.ModelViewSet):
    """List followers of body."""
    queryset = Body.objects.all()
    serializer_class = BodyFollowersSerializer
