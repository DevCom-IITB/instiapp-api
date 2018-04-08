from datetime import timedelta
from django.utils import timezone
from rest_framework.response import Response
from rest_framework import viewsets
from placements.models import BlogEntry
from placements.serializers import BlogEntrySerializer
from roles.helpers import login_required_ajax

class PlacementBlogViewset(viewsets.ViewSet):

    @classmethod
    @login_required_ajax
    def list(cls, request):
        return Response(BlogEntrySerializer(BlogEntry.objects.filter(
            published__gte=timezone.now() - timedelta(days=15)), many=True).data)
