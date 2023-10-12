"""URLs for placments."""
from django.urls import path
from external.views import ExternalBlogViewset

urlpatterns = [
    path("external-blog", ExternalBlogViewset.as_view({"get": "external_blog"})),
]
