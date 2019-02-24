"""URLs for prerender."""
from django.urls import path
import prerender.views as pr

urlpatterns = [
    path('', pr.root),
    path('feed', pr.root),
    path('news', pr.news),
    path('explore', pr.explore),
    path('user/<pk>', pr.user_details),
    path('event/<pk>', pr.event_details),
    path('org/<pk>', pr.body_details),
    path('body-tree/<pk>', pr.body_tree),
    path('map', pr.insti_map),
    path('map/<name>', pr.insti_map),
    path('mstile', pr.mstile),
]
