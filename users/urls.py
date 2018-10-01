"""URLs for users."""
from django.urls import path
from users.views import UserProfileViewSet
from roles.views import BodyRoleViewSet

urlpatterns = [
    path('users/<pk>', UserProfileViewSet.as_view({
        'get': 'retrieve'
    })),

    path('user-me', UserProfileViewSet.as_view({
        'get': 'retrieve_me', 'put': 'update_me', 'patch': 'update_me'
    })),

    path('user-me/ues/<event_pk>', UserProfileViewSet.as_view({'get': 'set_ues_me'})),
    path('user-me/unr/<news_pk>', UserProfileViewSet.as_view({'get': 'set_unr_me'})),
    path('user-me/subscribe-wp', UserProfileViewSet.as_view({'post': 'subscribe_web_push'})),
    path('user-me/events', UserProfileViewSet.as_view({'get': 'get_my_events'})),
    path('user-me/roles', BodyRoleViewSet.as_view({'get': 'get_my_roles'})),
]
