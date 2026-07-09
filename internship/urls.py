from django.urls import path
from .views import ThreadListView, ThreadDetailView, BlogPostListView, LatestCompanyPostListView, FilterOptionsView

urlpatterns = [
    path('filters/', FilterOptionsView.as_view(), name='filter-options'),
    path('threads/', ThreadListView.as_view(), name='thread-list'),
    path('threads/<slug:company_slug>/', ThreadDetailView.as_view(), name='thread-detail'),
    path('posts/', BlogPostListView.as_view(), name='post-list'),
    path('posts/latest/', LatestCompanyPostListView.as_view(), name='latest-company-posts'),
]