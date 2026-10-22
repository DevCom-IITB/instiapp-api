from django.urls import path
from .views import PlacementThreadListView, PlacementBlogPostListView, FilterOptionsView

urlpatterns = [
    path('placementblogs/filters/', FilterOptionsView.as_view(), name='filter-options'),
    path('placementblogs/threads/', PlacementThreadListView.as_view(), name='placement-thread-list'),
    path('placementblogs/posts/', PlacementBlogPostListView.as_view(), name='placement-post-list'),
]