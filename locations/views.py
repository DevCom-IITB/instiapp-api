"""Views for locations app."""
from rest_framework import viewsets
from rest_framework.response import Response
from locations.serializers import LocationSerializer
from locations.models import Location
from roles.helpers import insti_permission_required
from roles.helpers import login_required_ajax
from roles.helpers import user_has_insti_privilege
from roles.helpers import user_has_privilege
from roles.helpers import forbidden_no_privileges

class LocationViewSet(viewsets.ModelViewSet):
    """Location"""
    queryset = Location.objects.all()
    serializer_class = LocationSerializer

    @staticmethod
    def list(request):
        """List reusable locations."""
        queryset = Location.objects.filter(reusable=True)

        # Check if we don't want residences
        exclude = request.GET.get('exclude_group')
        if exclude is not None:
            queryset = queryset.exclude(group_id=int(exclude))

        return Response(LocationSerializer(queryset, many=True).data)

    @insti_permission_required('Location')
    def create(self, request):
        """Create a Location.
        Needs 'Location' institute permission."""

        return super().create(request)

    @login_required_ajax
    def update(self, request, pk):
        """Update Location.
        This requires the user to have the 'Location' institute permission
        or BodyRole for the event using the location if the it is not reusable."""

        # Allow insti privelege to do anything
        if user_has_insti_privilege(request.user.profile, 'Location'):
            return super().update(request, pk)

        # Disallow modifying reusable locations or marking reusable
        location = Location.objects.get(id=pk)
        if 'reusable' in request.data:
            if (request.data['reusable'] != location.reusable) or location.reusable:
                return forbidden_no_privileges()

        # Check if user has update privileges for each associated event
        for event in location.events.all():
            can_update = any([user_has_privilege(
                request.user.profile, str(b.id), 'UpdE') for b in event.bodies.all()])
            if not can_update:
                return forbidden_no_privileges()

        return super().update(request, pk)

    @insti_permission_required('Location')
    def destroy(self, request, pk):
        """Delete a Location.
        Needs 'Location' institute permission."""

        return super().destroy(request, pk)
