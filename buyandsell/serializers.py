"""Serializers for Event."""
from rest_framework import serializers
from buyandsell.models import Product
from users.serializers import UserProfileSerializer
class ProductSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer(read_only=True)
    category = serializers.SerializerMethodField()

    def get_category(self, obj):
        return obj.name

    class Meta:
        model = Product
        fields = '__all__'

    # def to_representation(self, instance):
    #     repre = super().to_representation(instance)
    #     repre['image_urls'] = [str(url) for url in ImageURL.objects.filter(product=instance)]
    #     # repre['category'] = Category.objects.get(id=repre['category']).name
    #     return repre

    def create(self, validated_data):
        data = self.context["request"].data
        validated_data['status'] = True
        validated_data['deleted'] = False
        validated_data['user'] = self.context['request'].user.profile
        validated_data['product_image'] = ",".join(data["product_image"]) if 'product_image' in data else ""
        if validated_data['action'] == 'giveaway':
            validated_data['price'] = 0
        return super().create(validated_data)
