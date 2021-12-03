"""URLs for buyandsell."""
from django.urls import path
from buyandsell.views import BuyAndSellViewSet

urlpatterns = [
    path('buyandsell', BuyAndSellViewSet.as_view({
        'get': 'list', 'post': 'create'
    })),

    path('buyandsell/<pk>', BuyAndSellViewSet.as_view({
        'get': 'retrieve', 'put': 'update', 'delete': 'destroy'
    })),
]
