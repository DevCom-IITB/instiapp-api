from rest_framework import serializers
from lostandfound.models import ProductFound
from users.serializers import UserProfileSerializer


class ProductFoundSerializer(serializers.ModelSerializer):
    product_image = serializers.SerializerMethodField()
    claimed_by = serializers.SerializerMethodField()
    claimed = serializers.SerializerMethodField()

    class Meta:
        model = ProductFound
        fields = (
            "id",
            "name",
            "description",
            "product_image",
            "category",
            "found_at",
            "claimed",
            "claimed_by",
            "contact_details",
            "time_of_creation",
        )

    def get_product_image(self, obj):
        return obj.product_image.split(",") if obj.product_image else None

    def get_claimed_by(self, obj):
        if obj.claimed_by:
            return UserProfileSerializer(
                obj.claimed_by, context={"extra": ["contact_no"]}
            ).data

        return None

    def get_claimed(self, obj):
        return obj.claimed
