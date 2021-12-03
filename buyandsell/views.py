"""Views for BuyAndSell."""
from uuid import UUID
from rest_framework.response import Response
from rest_framework import viewsets
from django.shortcuts import get_object_or_404
from buyandsell.models import Product
from buyandsell.serializers import ProductSerializer
class BuyAndSellViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    def list(self, request):
        ##introduce tags?
        data = ProductSerializer(Product.objects.all(), many=True).data
        return Response({'data':data, 'count':len(data)})