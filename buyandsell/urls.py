"""URLs for buyandsell."""
from django.urls import path
from buyandsell.views import BuyAndSellViewSet

urlpatterns = [
    # use list for search too to make use of pagination.
    path("buy/products", BuyAndSellViewSet.as_view({"get": "list", "post": "create"})),
    path(
        "buy/products/<pk>",
        BuyAndSellViewSet.as_view(
            {"get": "retrieve", "put": "update", "delete": "destroy"}
        ),
    ),
    path("buy/report/<pk>", BuyAndSellViewSet.as_view({"post": "report"})),
    path("buy/categories", BuyAndSellViewSet.as_view({"get": "get_categories"})),
]
