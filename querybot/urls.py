"""URLs for querybot."""
from django.urls import path
from querybot.views import QueryBotViewset

urlpatterns = [
    path('query', QueryBotViewset.as_view({
        'get': 'search',
        'post': 'ask_question'
    })),
    path('query/add-answer', QueryBotViewset.as_view({
        'post': 'add_answer'
    })),
]
