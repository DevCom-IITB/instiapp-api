"""URLs for popup_notification app."""
from django.urls import path
from .views import PopUpViewSet, PopUpMarkReadView

urlpatterns = [
    path("popup-notification/", PopUpViewSet.as_view(), name="popup-notification-list"),
    # path("popup-notification/<int:popup_id>/", PopUpViewSet.as_view(), name="popup-notification-detail"),#{
    #"heading": "",
   # "is_active":
   #} this is the json needed to be sent
    path("popup-notification/<int:popup_id>/mark-as-read/", PopUpMarkReadView.as_view(), name="mark-popup-as-read"),
    #{
    #"name": "Pop Up Mark Read",
    #} this is the json needed to be sent
]