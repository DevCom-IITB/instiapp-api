"""Serializers for Event."""
from rest_framework import serializers
from buyandsell.models import Product
from users.serializers import UserProfileSerializer


class ProductSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer(read_only=True)
    category = serializers.SerializerMethodField()
    product_image = serializers.SerializerMethodField()

    def get_product_image(self, obj):
        return obj.product_image.split(",") if obj.product_image else None

    def get_category(self, obj):
        return obj.name

    class Meta:
        model = Product
        fields = "__all__"

    def create(self, validated_data):
        data = self.context["request"].data
        validated_data["status"] = True
        validated_data["deleted"] = False
        validated_data["user"] = self.context["request"].user.profile

        validated_data["product_image"] = (
            ",".join(data["product_image"]) if "product_image" in data else ""
        )

        if validated_data["action"] == "giveaway":
            validated_data["price"] = 0
        return super().create(validated_data)
