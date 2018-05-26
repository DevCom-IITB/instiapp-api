from rest_framework.response import Response
from rest_framework import viewsets
from news.models import NewsEntry
from news.serializers import NewsEntrySerializer

class NewsFeedViewset(viewsets.ViewSet):

    @staticmethod
    def news_feed(request):
        """Get Feed."""
        # Initialize defaults
        from_i = 0
        num = 30

        # Set values from query paramters if available and valid
        from_q = request.GET.get('from')
        num_q = request.GET.get('num')
        if from_q is not None and str.isdigit(from_q):
            from_i = int(from_q)
        if num_q is not None and str.isdigit(num_q) and int(num_q) <= 100:
            num = int(num_q)

        return Response(NewsEntrySerializer(
            NewsEntry.objects.all()[from_i : from_i + num], many=True).data)
