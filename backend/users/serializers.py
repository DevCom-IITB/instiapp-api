' Serializers for UserProfile '
from rest_framework import serializers
from users.models import UserProfile

class UserProfileSerializer(serializers.HyperlinkedModelSerializer):
    ' Serializer for UserProfile '

    class Meta:
        model = UserProfile
        fields = ('url', 'id', 'name', 'roll_no', 'profile_pic',
                  'email', 'year', 'about')
