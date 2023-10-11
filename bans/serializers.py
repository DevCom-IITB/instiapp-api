"""Serializers for Bans """
from rest_framework import serializers
from users.serializers import UserProfileSerializer
from .models import SSOBan


class SSOBansSerializer(serializers.ModelSerializer):
    banned_by = UserProfileSerializer(read_only=False, source="name")

    class Meta:
        model = SSOBan
        fields = "__all__"
