"""URLs for news."""
from django.urls import path
from news.views import NewsFeedViewset

urlpatterns = [
    path('news', NewsFeedViewset.as_view({
        'get': 'news_feed'
    })),
]
