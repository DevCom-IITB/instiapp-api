from django.conf import settings
from rest_framework.response import Response
from rest_framework import viewsets
from placements.models import BlogEntry
from placements.serializers import BlogEntrySerializer
from roles.helpers import login_required_ajax
from helpers.misc import query_from_num

class PlacementBlogViewset(viewsets.ViewSet):

    @classmethod
    @login_required_ajax
    def placement_blog(cls, request):
        """Get Placement Blog."""
        from_i, num = query_from_num(request, 20)
        return Response(BlogEntrySerializer(BlogEntry.objects.filter(
            blog_url=settings.PLACEMENTS_URL)[from_i : from_i + num], many=True).data)

    @classmethod
    @login_required_ajax
    def training_blog(cls, request):
        """Get Training Blog."""
        from_i, num = query_from_num(request, 20)
        return Response(BlogEntrySerializer(BlogEntry.objects.filter(
            blog_url=settings.TRAINING_BLOG_URL)[from_i : from_i + num], many=True).data)
