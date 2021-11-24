from rest_framework.response import Response
from rest_framework import viewsets
from querybot.models import Query, UnresolvedQuery
from querybot.serializers import QuerySerializer, UnresolvedQuerySerializer
from roles.helpers import login_required_ajax
from .documents import QueryDocument
from elasticsearch_dsl import Q


class QueryBotViewset(viewsets.ViewSet):

    @classmethod
    @login_required_ajax
    def search(cls, request):
        """Get Search Results."""
        query = request.GET.get('query', '')
        categories = request.GET.get('category', '')
        categories = [x for x in categories.split("\'")]
        # print(request.data)
        # print(query)
        # print(request.GET)
        if query == '' and categories[0] == '':
            queryset = Query.objects.all()
            return Response(QuerySerializer(queryset, many=True).data)

        category_dic = {}
        querydic = {"match": {"question": {"query": query, "fuzziness": "AUTO"}}}
        if categories[0] == '':
            res = QueryDocument.search().query(Q(querydic))[:20]
        elif query == '':
            category_dic = [Q('match', category=category_id) for category_id in categories]
            query = category_dic.pop()
            for x in category_dic:
                query |= x
            res = QueryDocument.search().query(query)
        else:
            category_dic = [Q('match', category=category_id) for category_id in categories]
            query = category_dic.pop()
            for x in category_dic:
                query |= x
            res = QueryDocument.search().query(query)
            res = res.query(Q(querydic))
        queryset = res.to_queryset()
        return Response(QuerySerializer(queryset[0:20], many=True).data)

    @classmethod
    @login_required_ajax
    def ask_question(cls, request):
        """New Question Asked."""
        ques = request.data.get('question', '')
        cat = request.data.get('category', 'Others')
        if ques == '':
            return Response({'error': 'Question cannot be blank.'})

        user = request.user

        new_q = UnresolvedQuery.objects.create(question=ques, category=cat, user=user.profile)
        return Response(UnresolvedQuerySerializer(new_q).data)
