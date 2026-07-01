from django.urls import path
from .views import ThreadListView, ThreadDetailView

urlpatterns = [
    path('threads/', ThreadListView.as_view(), name='thread-list'),
    path('threads/<slug:company_slug>/', ThreadDetailView.as_view(), name='thread-detail'),
]