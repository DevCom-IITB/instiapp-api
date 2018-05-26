from datetime import timedelta
from django.utils import timezone
from django.conf import settings
from rest_framework.response import Response
from rest_framework import viewsets
from placements.models import BlogEntry
from placements.serializers import BlogEntrySerializer
from roles.helpers import login_required_ajax

class PlacementBlogViewset(viewsets.ViewSet):

    @classmethod
    @login_required_ajax
    def placement_blog(cls, request):
        """Get Placement Blog."""
        return Response(BlogEntrySerializer(BlogEntry.objects.filter(
            published__gte=timezone.now() - timedelta(days=15),
            blog_url=settings.PLACEMENTS_URL)[0:100], many=True).data)

    @classmethod
    @login_required_ajax
    def training_blog(cls, request):
        """Get Training Blog."""
        return Response(BlogEntrySerializer(BlogEntry.objects.filter(
            published__gte=timezone.now() - timedelta(days=15),
            blog_url=settings.TRAINING_BLOG_URL)[0:100], many=True).data)
