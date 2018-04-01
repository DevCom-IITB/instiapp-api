from datetime import timedelta
from django.utils import timezone
from rest_framework.response import Response
from rest_framework import viewsets
from placements.models import PlacementBlogEntry
from placements.serializers import PlacementBlogEntrySerializer
from roles.helpers import login_required_ajax

class PlacementBlogViewset(viewsets.ViewSet):

    @login_required_ajax
    def list(self, request):
        return Response(PlacementBlogEntrySerializer(PlacementBlogEntry.objects.filter(
            published__gte=timezone.now() - timedelta(days=15)), many=True).data)
