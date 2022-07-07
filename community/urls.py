"""URLs for placments."""
from django.urls import path
from community.views import CommunityViewSet,PostViewSet

urlpatterns = [
    path('communities', CommunityViewSet.as_view({
        'get': 'list',
    })),

    path('communities/<pk>', CommunityViewSet.as_view({
        'get': 'retrieve',
    })),

    path('communityposts', PostViewSet.as_view({
        'get': 'list',
    })),

    path('communitiesposts/<pk>', PostViewSet.as_view({
        'get': 'retrieve_full',
    })),
]
