"""URLs for mess menu."""
from django.urls import path
from messmenu.views import get_mess

urlpatterns = [
    path('mess', get_mess),
]
