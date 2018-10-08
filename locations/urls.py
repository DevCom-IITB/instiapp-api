"""URLs for locations."""
from django.urls import path
from locations.views import LocationViewSet

urlpatterns = [
    path('locations', LocationViewSet.as_view({
        'get': 'list', 'post': 'create'
    })),

    path('locations/<pk>', LocationViewSet.as_view({
        'get': 'retrieve', 'put': 'update', 'delete': 'destroy'
    })),
]
