"""URLs for events."""
from django.urls import path
from events.views import EventViewSet

urlpatterns = [
    path('events', EventViewSet.as_view({
        'get': 'list', 'post': 'create'
    })),

    path('events/<pk>', EventViewSet.as_view({
        'get': 'retrieve', 'put': 'update', 'delete': 'destroy'
    })),
]
