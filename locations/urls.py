"""URLs for locations."""
from django.urls import path
<<<<<<< HEAD
from locations.views import LocationViewSet, get_shortest_path, nearest_points, checkerrors,allnodes
=======
from locations.views import LocationViewSet, get_shortest_path, nearest_points,checkerrors
>>>>>>> d37a317f27876414b3a0614a67daac982c6e9ce3

urlpatterns = [
    path('locations', LocationViewSet.as_view({
        'get': 'list', 'post': 'create'
    })),

    path('locations/<pk>', LocationViewSet.as_view({
        'get': 'retrieve', 'put': 'update', 'delete': 'destroy'
    })),
<<<<<<< HEAD
    path('nearest/', nearest_points),
    path('check/', checkerrors),
    path('shortestpath/', get_shortest_path),
    # path('shortestpath/',allnodes)
=======
    path('shortestpath/', get_shortest_path),
    path('nearest/', nearest_points),
    path('check/', checkerrors)
>>>>>>> d37a317f27876414b3a0614a67daac982c6e9ce3
]
