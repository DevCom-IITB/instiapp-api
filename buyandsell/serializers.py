"""Serializers for Event."""
from rest_framework import serializers
from django.db.models import Count
from django.db.models import Prefetch
from django.db.models import Q
from buyandsell.models import Category, Product, ImageURL
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'
    def to_representation(self, instance):
        repre = super().to_representation(instance)
        repre['image_urls'] = [str(url) for url in ImageURL.objects.filter(product=instance)]
        repre['category'] = Category.objects.get(id=repre['category']).name
        return repre