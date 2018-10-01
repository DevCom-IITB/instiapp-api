"""URLs for bodies."""
from django.urls import path
from bodies.views import BodyViewSet
from bodies.views import BodyFollowersViewSet

urlpatterns = [
    path('bodies', BodyViewSet.as_view({
        'get': 'list', 'post': 'create'
    })),

    path('bodies/<pk>', BodyViewSet.as_view({
        'get': 'retrieve', 'put': 'update', 'delete': 'destroy'
    })),

    path('bodies/<pk>/followers', BodyFollowersViewSet.as_view(
        {'get': 'retrieve'}
    )),

    path('bodies/<pk>/follow', BodyViewSet.as_view({
        'get': 'follow'
    })),
]
