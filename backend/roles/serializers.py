from rest_framework import serializers
from roles.models import BodyRole
from roles.models import InstituteRole
from roles.models import PERMISSION_CHOICES
from roles.models import INSTITUTE_PERMISSION_CHOICES
from bodies.serializer_min import BodySerializerMin
from users.serializers import UserProfileSerializer

class RoleSerializer(serializers.ModelSerializer):

    permissions = serializers.MultipleChoiceField(choices=PERMISSION_CHOICES)
    body_detail = BodySerializerMin(read_only=True, source='body')

    class Meta:
        model = BodyRole
        fields = ('id', 'name', 'inheritable', 'body', 'body_detail', 'permissions', 'users')

class RoleSerializerMin(serializers.ModelSerializer):

    users_detail = UserProfileSerializer(many=True, read_only=True, source='users')

    class Meta:
        model = BodyRole
        fields = ('id', 'name', 'body', 'users_detail')

class InstituteRoleSerializer(serializers.ModelSerializer):

    permissions = serializers.MultipleChoiceField(choices=INSTITUTE_PERMISSION_CHOICES)

    class Meta:
        model = InstituteRole
        fields = ('id', 'name', 'permissions')
