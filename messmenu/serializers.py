"""Serializers for mess menu."""
from rest_framework import serializers
from messmenu.models import MenuEntry
from messmenu.models import Hostel

class MenuEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuEntry
        fields = '__all__'

class HostelSerializer(serializers.ModelSerializer):
    """Serializer for the hostel model"""
    mess = MenuEntrySerializer(many=True)
    class Meta:
        model = Hostel
        fields = ('id', 'name')
