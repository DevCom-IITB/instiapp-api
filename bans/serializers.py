"""Serializers for Bans """
from rest_framework import serializers
from users.serializers import UserProfileSerializer
from .models import SSOBans

class SSOBansSerializer(serializers.ModelSerializer):
    banned_by = UserProfileSerializer(read_only = False, source = 'name')

    class Meta:
        model = SSOBans
        fields = '__all__'
