from rest_framework import serializers
from gcleaderboard.models import GC, GC_Hostel_Points


class GCSerializer(serializers.ModelSerializer):
    class Meta:
        model = GC
        fields = ['name']


class Hostel_PointsSerializer(serializers.ModelSerializer):
    class Meta:
        model = GC_Hostel_Points
        fields = ['hostel' , 'points']


class Hostel_Serializer(serializers.ModelSerializer):
    class Meta:
        model = GC_Hostel_Points
        fields = ["points"]
