"""URLs for upload."""
from django.urls import path
from upload.views import UploadViewSet

urlpatterns = [
    path('upload', UploadViewSet.as_view({
        'post': 'create'
    })),

    path('upload/<pk>', UploadViewSet.as_view({
        'get': 'retrieve', 'delete': 'destroy'
    })),
]
