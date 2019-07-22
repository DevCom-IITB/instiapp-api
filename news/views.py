from rest_framework.response import Response
from rest_framework import viewsets
from news.models import NewsEntry
from news.serializers import NewsEntrySerializer
from helpers.misc import query_from_num
from helpers.misc import query_search

class NewsFeedViewset(viewsets.ViewSet):

    @staticmethod
    def news_feed(request):
        """Get News feed."""
        # Filter for body
        body = request.GET.get('body')
        if body is not None:
            queryset = NewsEntry.objects.filter(body__id=body)
        else:
            queryset = NewsEntry.objects.all()

        # Paging and search
        queryset = query_search(request, 3, queryset, ['title', 'content'], 'news')
        queryset = query_from_num(request, 20, queryset)

        # Eagerly load data
        queryset = NewsEntrySerializer.setup_eager_loading(queryset)

        # Get sliced news items
        return Response(NewsEntrySerializer(
            queryset, many=True,
            context={'request': request}).data)
