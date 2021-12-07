from elasticsearch_dsl import Q
from querybot.models import Query
from .documents import QueryDocument

def query_search(query, categories):
    if query == '' and categories[0] == '':
        queryset = Query.objects.all()
        return queryset

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
    return queryset[0:20]
