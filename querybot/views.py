from django.conf import settings
from rest_framework.response import Response
from rest_framework import viewsets
from querybot.models import Query, UnresolvedQuery
from querybot.serializers import QuerySerializer, UnresolvedQuerySerializer
from roles.helpers import login_required_ajax
from .documents import QueryDocument
from elasticsearch_dsl import Q
import operator


class QueryBotViewset(viewsets.ViewSet):

    @classmethod
    # @login_required_ajax
    def search(cls, request):
        """Get Search Results."""
        query = request.GET.get('query', '')
        categories = request.GET.get('category', [])
        categories = [x for x in categories.split("\'")]
        # print(request.data)
        # print(query)
        # print(request.GET)
        if query == '':
            queryset = Query.objects.all()
            return Response(QuerySerializer(queryset, many=True).data)
        
        category_dic = {}
        querydic = { \
            "match": { \
                "question": { \
                    "query": query, \
                    "fuzziness": "AUTO" \
                    } \
                }, \
            }
        if len(categories) == 0:
            res = QueryDocument.search().query(Q(querydic))[:20]
        else:
            category_dic = [Q('match', category=category_id) for category_id in categories ]
            query = category_dic.pop()
            for x in category_dic:
                query |= x
            res = QueryDocument.search().query(query & Q(querydic))[:20]
        queryset = res.to_queryset()
        return Response(QuerySerializer(queryset, many=True).data)

    @classmethod
    # @login_required_ajax
    def ask_question(cls, request):
        """New Question Asked."""
        ques = request.data.get('question', '')
        cat = request.data.get('category', '')
        if ques == '':
            return Response({'error': 'Question cannot be blank.'})

        new_q = UnresolvedQuery(question = ques, category = cat, user = request.user)
        new_q.save()
        return Response(UnresolvedQuerySerializer(new_q).data)

    @classmethod
    # @login_required_ajax
    def add_answer(cls, request):
        """New Answer Added."""
        ques = request.data.get('question', '')
        ans = request.data.get('answer', '')
        cat = request.data.get('category', '')
        s_cat = request.data.get('sub_category', '')
        s_s_cat = request.data.get('sub_sub_category', '')

        if '' in [ques, ans, cat]:
            return Response({'error': 'question, answer and category fields are required.'})
        
        new_q = Query(question = ques, answer = ans, category = cat, sub_category = s_cat, sub_sub_category = s_s_cat)
        new_q.save()
        return Response(QuerySerializer(new_q).data)