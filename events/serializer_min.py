"""Minimal serializers for Event."""
from rest_framework import serializers
from events.models import Event

class EventMinSerializer(serializers.ModelSerializer):
    """Very minimalistic serializer for Event."""

    class Meta:
        model = Event
        fields = ('id', 'str_id', 'name', 'image_url', 'start_time', 'end_time')
