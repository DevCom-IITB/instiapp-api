from datetime import timedelta
from django.utils import timezone
from rest_framework.response import Response
from rest_framework import viewsets
from placements.models import PlacementBlogEntry
from placements.serializers import PlacementBlogEntrySerializer

class PlacementBlogViewset(viewsets.ViewSet):

    def list(self, request):
        return Response(PlacementBlogEntrySerializer(PlacementBlogEntry.objects.filter(
            published__gte=timezone.now() - timedelta(days=15)), many=True).data)
