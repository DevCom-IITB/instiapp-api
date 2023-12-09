"""Serializer for QueryBot."""
from rest_framework import serializers
from querybot.models import Query, UnresolvedQuery


class QuerySerializer(serializers.ModelSerializer):
    """Serializer for QueryBotEntry."""

    class Meta:
        model = Query
        fields = "__all__"


class UnresolvedQuerySerializer(serializers.ModelSerializer):
    """Serializer for Unresolved Queries."""

    class Meta:
        model = UnresolvedQuery
        fields = "__all__"
