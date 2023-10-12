from elasticsearch_dsl import Q
from django.conf import settings
from querybot.models import Query
from .documents import QueryDocument


def query_search(query, categories):  # pragma: no cover
    if settings.USE_ELASTIC:
        querydic = {"match": {"question": {"query": query, "fuzziness": "AUTO"}}}
        if query == "" and categories[0] == "":
            queryset = Query.objects.all()
        elif categories[0] == "":
            res = QueryDocument.search().query(Q(querydic))[:20]
            queryset = res.to_queryset()
        elif query == "":
            category_dic = [
                Q("match", category=category_id) for category_id in categories
            ]
            query = category_dic.pop()
            for x in category_dic:
                query |= x
            res = QueryDocument.search().query(query)
            queryset = res.to_queryset()
        else:
            category_dic = [
                Q("match", category=category_id) for category_id in categories
            ]
            query = category_dic.pop()
            for x in category_dic:
                query |= x
            res = QueryDocument.search().query(query)
            res = res.query(Q(querydic))[:20]
            queryset = res.to_queryset()
        return queryset
    queryset = Query.objects.all()
    return queryset
