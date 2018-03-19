from rest_framework import serializers
from roles.models import BodyRole
from roles.models import InstituteRole
from roles.models import PERMISSION_CHOICES
from roles.models import INSTITUTE_PERMISSION_CHOICES

class RoleSerializer(serializers.ModelSerializer):

    permissions = serializers.MultipleChoiceField(choices=PERMISSION_CHOICES)

    class Meta:
        model = BodyRole
        fields = ('id', 'name', 'inheritable', 'body', 'permissions')

class InstituteRoleSerializer(serializers.ModelSerializer):

    permissions = serializers.MultipleChoiceField(choices=INSTITUTE_PERMISSION_CHOICES)

    class Meta:
        model = BodyRole
        fields = ('id', 'name', 'permissions')
