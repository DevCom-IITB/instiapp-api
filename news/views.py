from rest_framework.response import Response
from rest_framework import viewsets
from news.models import NewsEntry
from news.serializers import NewsEntrySerializer
from helpers.misc import query_from_num

class NewsFeedViewset(viewsets.ViewSet):

    @staticmethod
    def news_feed(request):
        """Get News feed."""
        from_i, num = query_from_num(request, 30)
        return Response(NewsEntrySerializer(
            NewsEntry.objects.all()[from_i : from_i + num], many=True).data)
