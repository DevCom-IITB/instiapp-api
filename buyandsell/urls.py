"""URLs for buyandsell."""
from django.urls import path
from buyandsell.views import BuyAndSellViewSet

urlpatterns = [
    #use list for search too to make use of pagination.
    path('buy', BuyAndSellViewSet.as_view({
        'get': 'list', 'post': 'create'
    })),

    path('buy/<pk>', BuyAndSellViewSet.as_view({
        'get':'retrieve','put': 'update', 'delete': 'destroy'
    })),
    path('report/<pk>', BuyAndSellViewSet.as_view({
        'post':'report'
    }))
]
