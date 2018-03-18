from django.shortcuts import render
from rest_framework import viewsets
from roles.models import BodyRole
from roles.serializers import RoleSerializer

class BodyRoleViewSet(viewsets.ModelViewSet):   # pylint: disable=too-many-ancestors
    """API endpoint that allows roles to be viewed or edited."""
    queryset = BodyRole.objects.all()
    serializer_class = RoleSerializer
