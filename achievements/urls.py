"""URLs for events."""
from django.urls import path
from achievements.views import AchievementViewSet
from achievements.views import OfferedAchievementViewSet

urlpatterns = [
    path('achievements', AchievementViewSet.as_view({
        'get': 'list', 'post': 'create'
    })),
    path('achievements/<pk>', AchievementViewSet.as_view({
        'put': 'update', 'delete': 'destroy', 'get': 'retrieve', 'patch': 'update'
    })),
    path('achievements-body/<pk>', AchievementViewSet.as_view({
        'get': 'list_body'
    })),
    path('achievements-offer', OfferedAchievementViewSet.as_view({
        'post': 'create'
    })),
    path('achievements-offer/<pk>', OfferedAchievementViewSet.as_view({
        'get': 'retrieve', 'put': 'update', 'delete': 'destroy', 'post': 'claim_secret'
    })),
]
