"""URLs for popup_notification app."""
from django.urls import path
from .views import PopUpViewSet, MarkLatestAsReadView

urlpatterns = [
    path("popup-notification/", PopUpViewSet.as_view(), name="popup-notification"),
    path("popup-notification/mark-as-read/", MarkLatestAsReadView.as_view(), name="mark-popup-as-read"),
]