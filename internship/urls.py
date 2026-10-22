from django.urls import path
from .views import ThreadListView, BlogPostListView, FilterOptionsView

urlpatterns = [
    path('internship/filters/', FilterOptionsView.as_view(), name='filter-options'),
    path('internship/threads/', ThreadListView.as_view(), name='thread-list'),
    path('internship/posts/', BlogPostListView.as_view(), name='post-list'),
]