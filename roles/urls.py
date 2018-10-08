"""URLs for roles."""
from django.urls import path
from roles.views import BodyRoleViewSet

urlpatterns = [
    path('roles', BodyRoleViewSet.as_view({
        'post': 'create'
    })),

    path('roles/<pk>', BodyRoleViewSet.as_view({
        'get': 'retrieve', 'put': 'update', 'delete': 'destroy'
    })),
]
