"""URLs for querybot."""
from django.urls import path
from querybot.views import QueryBotViewset

urlpatterns = [
    path("query", QueryBotViewset.as_view({"get": "search"})),
    path("query/add", QueryBotViewset.as_view({"post": "ask_question"})),
    path("query/categories", QueryBotViewset.as_view({"get": "get_categories"})),
]
