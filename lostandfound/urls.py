from django.urls import path
from lostandfound.views import LostandFoundViewset
from lostandfound.admin import cso_admin_site


urlpatterns = [
    path("cso_admin_login/", cso_admin_site.urls, name="cso_admin_login"),
    path(
        "lnf/products/", LostandFoundViewset.as_view({"get": "list"}), name="products"
    ),
    path(
        "lnf/products/<str:pk>/",
        LostandFoundViewset.as_view({"get": "retrieve"}),
        name="product",
    ),
    # path('lnf/products/claim/', LostandFoundViewset.as_view({'post': 'claim'}), name='claim'),
]
