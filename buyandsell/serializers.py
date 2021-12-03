"""Serializers for Event."""
from rest_framework import serializers
from django.db.models import Count
from django.db.models import Prefetch
from django.db.models import Q
from buyandsell.models import Product
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'
    