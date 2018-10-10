"""Viewsets for bodies."""
from rest_framework import viewsets
from rest_framework.response import Response
from roles.models import BodyRole
from roles.serializers import RoleSerializer
from roles.serializers import RoleSerializerWithEvents
from roles.helpers import user_has_privilege
from roles.helpers import user_has_insti_privilege
from roles.helpers import login_required_ajax
from roles.helpers import forbidden_no_privileges

class BodyRoleViewSet(viewsets.ModelViewSet):
    """Body Role"""
    queryset = BodyRole.objects.all()
    serializer_class = RoleSerializer

    @login_required_ajax
    def create(self, request):
        if user_has_insti_privilege(request.user.profile, 'RoleB'):
            return super().create(request)

        if 'body' not in request.data or not request.data['body']:
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
            return Response({
                'message': 'body is immutable',
                'detail': 'Body cannot be changed. Create a new role.'
            }, status=400)
        if not user_has_privilege(request.user.profile, str(body.id), 'Role'):
            return forbidden_no_privileges()
        return super().update(request, pk)

    @login_required_ajax
    def destroy(self, request, pk):
        if user_has_insti_privilege(request.user.profile, 'RoleB'):
            return super().destroy(request, pk)

        # Check for permission
        body_role = BodyRole.objects.get(id=pk)
        bodyid = str(body_role.body.id)
        if not user_has_privilege(request.user.profile, bodyid, 'Role'):
            return forbidden_no_privileges()

        # Check for former users
        if body_role.former_users.count() > 0:
            return forbidden_no_privileges()

        return super().destroy(request, pk)

    @classmethod
    @login_required_ajax
    def get_my_roles(cls, request):
        """Get roles with nested events."""
        return Response(RoleSerializerWithEvents(
            request.user.profile.roles, many=True, context={'request': request}).data)
