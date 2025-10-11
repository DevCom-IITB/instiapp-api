"""Views for BuyAndSell."""
from uuid import UUID
from rest_framework.response import Response
from rest_framework import viewsets
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from roles.helpers import login_required_ajax
from lostandfound.models import ProductFound
from lostandfound.serializers import ProductFoundSerializer

REPORTS_THRES = 3


class LostandFoundViewset(viewsets.ModelViewSet):
    serializer_class = ProductFoundSerializer
    RESULTS_PER_PAGE = 1  # testing purposes.
    queryset = ProductFound.objects

    @login_required_ajax
    def list(self, request, *args, **kwargs):
        """Get list of products."""
        queryset = self.get_queryset()
        data = self.serializer_class(queryset, many=True).data

        return Response(data, status=200)

    @login_required_ajax
    def retrieve(self, request, pk):
        """Get a product from pk uuid or strid."""
        try:
            UUID(pk, version=4)
            product = get_object_or_404(self.queryset, id=pk)
        except ValueError:
            product = get_object_or_404(self.queryset, str_id=pk)
        data = self.serializer_class(product).data
        return Response(data, status=200)

    @login_required_ajax
    def claim(self, request, *args, **kwargs):
        """Claim a product."""
        try:
            product = self.queryset.get(id=request.data["product_id"])
        except ProductFound.DoesNotExist:
            return Response({"message": "Product not found"}, status=404)
        if product.claimed:
            return Response({"message": "Product already claimed"}, status=400)
        product.claimed = True
        product.claimed_by = request.user.profile
        product.save()
        return Response({"message": "Product claimed"}, status=200)


@login_required
def cso_admin_login(request):
    if request.user.is_staff:
        return redirect("CSOAdmin:index")
    return Response({"message": "Not a staff member"}, status=401)
