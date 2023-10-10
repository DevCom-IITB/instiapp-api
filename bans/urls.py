"""URLs for Bans"""
from django.urls import path
from bans.views import SSOBansViewSet

urlpatterns =[
    path('bans/', SSOBansViewSet.as_view(
        {'get':'list', 'post':'create'}
    )), 
    path('bans/<pk>/', SSOBansViewSet.as_view({
        'put': 'update', 'delete': 'destroy', 'get': 'retrieve', 'patch': 'update'
    }))
]