"""URLs for events."""
from django.urls import path
from achievements.views import AchievementViewSet

urlpatterns = [
    path('achievements', AchievementViewSet.as_view({
        'get': 'list', 'post': 'create'
    })),
    path('achievements/<pk>', AchievementViewSet.as_view({
        'put': 'update', 'delete': 'destroy', 'get': 'retrieve'
    })),
    path('achievements-body/<pk>', AchievementViewSet.as_view({
        'get': 'list_body'
    })),
]
