from django.urls import path
from .views import PlacementThreadListView, PlacementThreadDetailView, PlacementBlogPostListView, PlacementLatestCompanyPostListView, FilterOptionsView

urlpatterns = [
    path('filters/', FilterOptionsView.as_view(), name='filter-options'),
    path('threads/', PlacementThreadListView.as_view(), name='placement-thread-list'),
    path('threads/<slug:company_slug>/', PlacementThreadDetailView.as_view(), name='placement-thread-detail'),
    path('posts/', PlacementBlogPostListView.as_view(), name='placement-post-list'),
    path('posts/latest/', PlacementLatestCompanyPostListView.as_view(), name='placement-latest-company-posts'),
]