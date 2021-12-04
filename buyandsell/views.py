"""Views for BuyAndSell."""
from uuid import UUID
from rest_framework.response import Response
from rest_framework import viewsets
from django.shortcuts import get_object_or_404

from buyandsell.models import Product
from buyandsell.serializers import ProductSerializer
from helpers.misc import query_from_num, query_search
class BuyAndSellViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    RESULTS_PER_PAGE = 1#testing purposes.
    queryset = Product.objects
    def list(self, request):
        ##introduce tags?
        queryset = self.queryset.filter(status=True)
        queryset = query_search(request, 3, queryset, ['name', 'description'], 'buyandsell')
        queryset = query_from_num(request, self.RESULTS_PER_PAGE, queryset)
        data = ProductSerializer(queryset, many=True).data
        return Response(data)
    def create(self, request, *args, **kwargs):
        """Creates product if the user isn't banned and form is filled
        correctly. Ban checking is yet to be incorporated.
        """
        if (request.user.is_authenticated):
            request.data._mutable = True
            request.data['status'] = True
            from users.models import UserProfile
            request.data['user'] = UserProfile.objects.get(user=request.user).id
            return super().create(request, *args, **kwargs)
        else:
            return Response({'msg':'Authentication Failed'})