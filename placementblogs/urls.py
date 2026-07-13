from django.urls import path
from .views import PlacementThreadListView, PlacementThreadDetailView, PlacementBlogPostListView, PlacementLatestCompanyPostListView, FilterOptionsView

urlpatterns = [
    path('placementblogs/filters/', FilterOptionsView.as_view(), name='filter-options'),
    path('placementblogs/threads/', PlacementThreadListView.as_view(), name='placement-thread-list'),
    path('placementblogs/threads/<slug:company_slug>/', PlacementThreadDetailView.as_view(), name='placement-thread-detail'),
    path('placementblogs/posts/', PlacementBlogPostListView.as_view(), name='placement-post-list'),
    path('placementblogs/posts/latest/', PlacementLatestCompanyPostListView.as_view(), name='placement-latest-company-posts'),
]