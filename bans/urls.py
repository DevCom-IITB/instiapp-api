"""URLs for Bans"""
from django.urls import path
from bans.views import SSOBanViewSet

urlpatterns = [
    path("bans/", SSOBanViewSet.as_view({"get": "list", "post": "create"})),
    path(
        "bans/<pk>/",
        SSOBanViewSet.as_view(
            {"put": "update", "delete": "destroy", "get": "retrieve", "patch": "update"}
        ),
    ),
]
