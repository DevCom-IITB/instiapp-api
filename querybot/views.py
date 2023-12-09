from rest_framework.response import Response
from rest_framework import viewsets
from querybot.helpers import query_search
from querybot.models import Query, UnresolvedQuery
from querybot.serializers import QuerySerializer, UnresolvedQuerySerializer
from roles.helpers import login_required_ajax


class QueryBotViewset(viewsets.ViewSet):
    @classmethod
    @login_required_ajax
    def search(cls, request):
        """Get Search Results."""
        query = request.GET.get("query", "")
        categories = request.GET.get("category", "")
        categories = [x for x in categories.split("'")]
        queryset = query_search(query, categories)
        return Response(QuerySerializer(queryset, many=True).data)

    @classmethod
    @login_required_ajax
    def ask_question(cls, request):
        """New Question Asked."""
        ques = request.data.get("question", "")
        cat = request.data.get("category", "Others")
        if ques == "":
            return Response({"error": "Question cannot be blank."}, status=403)

        user = request.user

        new_q = UnresolvedQuery.objects.create(
            question=ques, category=cat, user=user.profile
        )
        return Response(UnresolvedQuerySerializer(new_q).data)

    @classmethod
    @login_required_ajax
    def get_categories(cls, request):
        """Method to get all categories"""
        queryset = Query.objects.all().values("category").distinct()
        values = [x["category"] for x in queryset]
        return Response(values)
