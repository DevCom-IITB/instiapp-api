"""URLs for mess menu."""
from django.urls import path
from messmenu.views import get_mess, getUserMess

urlpatterns = [
    path('mess', get_mess),
    path('getUserMess', getUserMess),
]
