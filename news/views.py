from rest_framework.response import Response
from rest_framework import viewsets
from news.models import NewsEntry
from news.serializers import NewsEntrySerializer
from helpers.misc import query_from_num

class NewsFeedViewset(viewsets.ViewSet):

    @staticmethod
    def news_feed(request):
        """Get News feed."""
        # Paging parameters
        from_i, num = query_from_num(request, 30)

        # Filter for body
        body = request.GET.get('body')
        if body is not None:
            queryset = NewsEntry.objects.filter(body__id=body)
        else:
            queryset = NewsEntry.objects.all()

        # Eagerly load data
        queryset = NewsEntrySerializer.setup_eager_loading(queryset)

        # Get sliced news items
        return Response(NewsEntrySerializer(
            queryset[from_i : from_i + num], many=True,
            context={'request': request}).data)
