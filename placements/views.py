from django.conf import settings
from rest_framework.response import Response
from rest_framework import viewsets
from placements.models import BlogEntry
from placements.serializers import BlogEntrySerializer
from roles.helpers import login_required_ajax
from helpers.misc import query_from_num
from helpers.misc import query_search

class PlacementBlogViewset(viewsets.ViewSet):

    @classmethod
    @login_required_ajax
    def placement_blog(cls, request):
        """Get Placement Blog."""
        queryset = BlogEntry.objects.filter(blog_url=settings.PLACEMENTS_URL)
        queryset = query_search(request, 3, queryset, ['title', 'content'], 'placement')
        queryset = query_from_num(request, 20, queryset)

        return Response(BlogEntrySerializer(queryset, many=True).data)

    @classmethod
    @login_required_ajax
    def training_blog(cls, request):
        """Get Training Blog."""
        queryset = BlogEntry.objects.filter(blog_url=settings.TRAINING_BLOG_URL)
        queryset = query_search(request, 3, queryset, ['title', 'content'], 'training')
        queryset = query_from_num(request, 20, queryset)
        return Response(BlogEntrySerializer(queryset, many=True).data)
