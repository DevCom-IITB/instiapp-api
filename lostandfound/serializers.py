from rest_framework import serializers
from lostandfound.models import ProductFound

class ProductFoundSerializer(serializers.ModelSerializer):
    product_image = serializers.SerializerMethodField()
    claimed_by = serializers.SerializerMethodField()
    claimed = serializers.SerializerMethodField()
    class Meta:
        model = ProductFound
        fields = ('id', 'name', 'description', 'product_image', 'category', 'found_at', 'claimed', 'contact_details', 'time_of_creation', 'claimed_by')

    def get_product_image(self, obj):
        return obj.product_image.split(',') if obj.product_image else None
    
    def get_claimed_by(self, obj):
        return obj.claimed_by.user.username if obj.claimed_by else None
    def get_claimed(self, obj):
        return obj.claimed
    