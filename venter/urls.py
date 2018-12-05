"""URLs for venter."""
from django.urls import path
from venter.views import ComplaintViewSet
from venter.views import TagViewSet
from venter.views import CommentViewSet

urlpatterns = [
    path('complaints', ComplaintViewSet.as_view({
        'post': 'create', 'get': 'list'
    })),

    path('complaints/<pk>', ComplaintViewSet.as_view({
        'get': 'retrieve'
    })),

    path('complaints/<pk>/upvote', ComplaintViewSet.as_view({
        'get': 'up_vote'
    })),

    path('complaints/<pk>/subscribe', ComplaintViewSet.as_view({
        'get': 'subscribe'
    })),

    path('complaints/<pk>/comments', CommentViewSet.as_view({
        'post': 'create'
    })),

    path('comments/<pk>', CommentViewSet.as_view({
        'put': 'update', 'delete': 'destroy', 'get': 'retrieve'
    })),

    path('tags', TagViewSet.as_view({
        'get': 'list'
    })),
]
