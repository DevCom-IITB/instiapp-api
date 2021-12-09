"""Views for BuyAndSell."""
from uuid import UUID
from django.db.models.query import QuerySet
from rest_framework.generics import UpdateAPIView
from rest_framework.response import Response
from rest_framework import viewsets
from django.shortcuts import get_object_or_404
from roles.helpers import login_required_ajax
from buyandsell.models import ImageURL, Product
from buyandsell.serializers import ProductSerializer
from helpers.misc import query_from_num, query_search
from users.models import UserProfile
import json
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
    @login_required_ajax
    def create(self, request, *args, **kwargs):
        """Creates product if the user isn't banned and form is filled
        correctly. Ban checking is yet to be incorporated.
        """
        from users.models import UserProfile
        userpro = UserProfile.objects.get(user=request.user)
        userpro:UserProfile
        request.data._mutable = True
        request.data['status'] = True
        image_urls = json.loads(request.data['image_urls'])
        request.data['contact_details'] = f"""
 Phone: {userpro.contact_no}
 Email: {userpro.email}"""
        request.data['user'] = userpro.id
        new_product_data = super().create(request, *args, **kwargs)
        for url in image_urls:
            ImageURL.objects.create(product=Product.objects.get(id=new_product_data.data['id']), url=url)
        return Response(ProductSerializer(Product.objects.get(id=new_product_data.data['id'])).data)
    @login_required_ajax
    def destroy(self, request, pk):
            product = self.get_product(pk)
            if(UserProfile.objects.get(request.user)==product.user):
                return super().destroy(request, pk)
    def get_product(self, pk):
        UUID(pk, version=4)
        return get_object_or_404(self.queryset, id=pk)

    @login_required_ajax
    def update(self, request, pk):
        product = self.get_product(pk)
        if(product.user == UserProfile.objects.get(id=request.user)):
            return super().update(request, pk)

    def retrieve(self, request, *args, **kwargs):
        #query handler
        return super().retrieve(request, *args, **kwargs)