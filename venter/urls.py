"""URLs for venter."""
from django.urls import path
from venter.views import ComplaintViewSet
from venter.views import CommentViewSet

urlpatterns = [
    path('complaints', ComplaintViewSet.as_view({
        'post': 'create', 'get': 'list'
    })),

    path('complaints/<pk>', ComplaintViewSet.as_view({
        'get': 'retrieve', 'put': 'update'
    })),

    path('complaints/<pk>/comments', CommentViewSet.as_view({
        'post': 'create'
    })),

    path('comments/<pk>', CommentViewSet.as_view({
        'put': 'update', 'delete': 'destroy', 'get': 'retrieve'
    })),
]
