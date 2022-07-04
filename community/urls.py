"""URLs for placments."""
from django.urls import path
from community.views import CommunityViewSet
from community.serializers import CommunitySerializers
from . import views

urlpatterns = [
    path('communities', CommunityViewSet.as_view({
        'get': 'list',
    })),

    path('communities/<pk>', CommunityViewSet.as_view({
        'get': 'retrieve',
    })),
]
