from django_elasticsearch_dsl import Document

# from django_elasticsearch_dsl.registries import registry
from .models import Query


# Uncomment to run queries
# @registry.register_document
class QueryDocument(Document):
    class Index:
        name = "query"
        settings = {"number_of_shards": 1, "number_of_replicas": 0}

    class Django:
        model = Query

        fields = ["question", "answer", "category", "sub_category", "sub_sub_category"]
