"""URLs for placments."""
from django.urls import path
from placements.views import PlacementBlogViewset

urlpatterns = [
    path('placement-blog', PlacementBlogViewset.as_view({'get': 'placement_blog'})),
    path('training-blog', PlacementBlogViewset.as_view({'get': 'training_blog'})),
]
