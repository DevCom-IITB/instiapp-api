from rest_framework import serializers
from roles.models import BodyRole
from roles.models import PERMISSION_CHOICES

class RoleSerializer(serializers.ModelSerializer):

    permissions = serializers.MultipleChoiceField(choices=PERMISSION_CHOICES)

    class Meta:
        model = BodyRole
        fields = ('id', 'name', 'inheritable', 'body', 'permissions')
