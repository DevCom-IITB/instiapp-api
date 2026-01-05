"""Serializers for Event."""
from rest_framework import serializers
from buyandsell.models import Product
from users.serializers import UserProfileSerializer

class CommaSeparatedStringsField(serializers.Field):
    def to_representation(self, value):
        """Convert DB string to API list."""
        if not value:
            return []
        return value.split(",")

    def to_internal_value(self, data):
        """Convert API input to DB string."""
        if isinstance(data, list):
            # Filter out empty URLs and strip whitespace
            return ",".join([url.strip() for url in data if url.strip()])
        if isinstance(data, str):
            return data
        return ""

class ProductSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer(read_only=True)
    product_image = CommaSeparatedStringsField(required=False)

    class Meta:
        model = Product
        fields = "__all__"
        read_only_fields = ('time_inactive',)

    def create(self, validated_data):
        validated_data["status"] = True
        validated_data["deleted"] = False
        validated_data["user"] = self.context["request"].user.profile

        if validated_data["action"] == "giveaway":
            validated_data["price"] = 0

        if 'original_price' not in validated_data:
            validated_data['original_price'] = None

        return super().create(validated_data)
