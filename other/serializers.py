"""Serializers for non-specific models."""
from rest_framework import serializers
from users.models import UserTag
from users.models import UserTagCategory

class UserTagSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserTag
        fields = ('id', 'name')

class UserTagCategorySerializer(serializers.ModelSerializer):

    tags = UserTagSerializer(many=True)

    class Meta:
        model = UserTagCategory
        fields = ('id', 'name', 'tags')
