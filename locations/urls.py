"""URLs for locations."""
from django.urls import path
from locations.views import (
    LocationViewSet,
    get_shortest_path,
    nearest_points,
    checkerrors,
)

urlpatterns = [
    path("locations", LocationViewSet.as_view({"get": "list", "post": "create"})),
    path(
        "locations/<pk>",
        LocationViewSet.as_view(
            {"get": "retrieve", "put": "update", "delete": "destroy"}
        ),
    ),
    path("nearest/", nearest_points),
    path("check/", checkerrors),
    path("shortestpath/", get_shortest_path),
    # path('shortestpath/',allnodes)
]
