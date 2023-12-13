"""URLs for events."""
from django.urls import path
from events.views import EventViewSet, EventMailVerificationViewSet

urlpatterns = [
    path("events", EventViewSet.as_view({"get": "list", "post": "create"})),
    path(
        "events/<pk>",
        EventViewSet.as_view({"get": "retrieve", "put": "update", "delete": "destroy"}),
    ),
    path(
        "events/<pk>/verify-and-send-mail",
        EventMailVerificationViewSet.as_view({"post": "verify_and_send_mail"})
    ),
]
