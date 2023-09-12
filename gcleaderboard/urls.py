from django.urls import path
from . import views
from gcleaderboard.views import InstiViewSet, PostViewSet, UpdateViewSet

urlpatterns = [
    path(
        "gcleaderboard/typesofGC",
        InstiViewSet.as_view(
            {
                "get": "Types_Of_GCs",
            }
        ),
    ),
    path(
        "gcleaderboard/whichGC/<Type>/",
        InstiViewSet.as_view(
            {
                "get": "X_GC",
            }
        ),
    ),
    path(
        "gcleaderboard/subgclb/<gcuuid>",
        InstiViewSet.as_view(
            {
                "get": "Sub_GC_LB",
            }
        ),
    ),
    path(
        "gcleaderboard/typegclb/<Type>",
        InstiViewSet.as_view(
            {
                "get": "Type_GC_LB",
            }
        ),
    ),
    path(
        "gcleaderboard/gclb/",
        InstiViewSet.as_view(
            {
                "get": "GC_LB",
            }
        ),
    ),
    path(
        "gcleaderboard/postGC",
        PostViewSet.as_view(
            {
                "post": "add_GC",
            }
        ),
    ),
    path(
        "gcleaderboard/updateGC/<pk>/",
        UpdateViewSet.as_view(
            {
                "put": "update_Points",
            }
        ),
    ),
]

