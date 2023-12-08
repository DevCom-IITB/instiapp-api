from rest_framework.response import Response
from rest_framework import viewsets

from roles.helpers import login_required_ajax
from helpers.misc import query_from_num
from helpers.misc import query_search

from external.serializers import ExternalBlogEntrySerializer
from external.models import ExternalBlogEntry


class ExternalBlogViewset(viewsets.ViewSet):
    @classmethod
    @login_required_ajax
    def external_blog(cls, request):
        """Get External Blog."""
        queryset = ExternalBlogEntry.objects.filter()
        queryset = query_search(
            request, 3, queryset, ["title", "content", "body"], "external"
        )
        queryset = query_from_num(request, 20, queryset)

        return Response(ExternalBlogEntrySerializer(queryset, many=True).data)
