from rest_framework.response import Response
from rest_framework import viewsets
from news.models import NewsEntry
from news.serializers import NewsEntrySerializer

class NewsFeedViewset(viewsets.ViewSet):

    @staticmethod
    def news_feed(request):
        """Get Feed."""
        return Response(NewsEntrySerializer(NewsEntry.objects.all()[0:30], many=True).data)
