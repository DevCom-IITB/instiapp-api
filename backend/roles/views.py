from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.response import Response
from roles.models import BodyRole
from roles.serializers import RoleSerializer
from roles.helpers import user_has_privilege
from roles.helpers import user_has_insti_privilege
from roles.helpers import login_required_ajax
from roles.helpers import forbidden_no_privileges

class BodyRoleViewSet(viewsets.ModelViewSet):   # pylint: disable=too-many-ancestors
    """API endpoint that allows roles to be viewed or edited."""
    queryset = BodyRole.objects.all()
    serializer_class = RoleSerializer

    @login_required_ajax
    def create(self, request):
        if user_has_insti_privilege(request.user.profile, 'RoleB'):
            return super().create(request)

        if not request.data['body']:
            return Response({"body": "body is required"}, status=400)
        if not user_has_privilege(request.user.profile, request.data['body'], 'Role'):
            return forbidden_no_privileges()
        return super().create(request)

    @login_required_ajax
    def update(self, request, pk):
        if user_has_insti_privilege(request.user.profile, 'RoleB'):
            return super().update(request, pk)

        body = BodyRole.objects.get(id=pk).body
        if request.data['body'] != str(body.id):
            return Response({'error': 'body is immutable'}, status=400)
        if not user_has_privilege(request.user.profile, str(body.id), 'Role'):
            return forbidden_no_privileges()
        return super().update(request, pk)

    @login_required_ajax
    def destroy(self, request, pk):
        if user_has_insti_privilege(request.user.profile, 'RoleB'):
            return super().destroy(request, pk)

        bodyid = str(BodyRole.objects.get(id=pk).body.id)
        if not user_has_privilege(request.user.profile, bodyid, 'Role'):
            return forbidden_no_privileges()
        return super().destroy(request, pk)
