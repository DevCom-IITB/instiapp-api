from django.urls import path
from .views import ThreadListView, ThreadDetailView, BlogPostListView, LatestCompanyPostListView, FilterOptionsView

urlpatterns = [
    path('internship/filters/', FilterOptionsView.as_view(), name='filter-options'),
    path('internship/threads/', ThreadListView.as_view(), name='thread-list'),
    path('internship/threads/<slug:company_slug>/', ThreadDetailView.as_view(), name='thread-detail'),
    path('internship/posts/', BlogPostListView.as_view(), name='post-list'),
    path('internship/posts/latest/', LatestCompanyPostListView.as_view(), name='latest-company-posts'),
]