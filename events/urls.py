"""URLs for events."""
from django.urls import path
from events.views import EventViewSet, EventMailVerificationViewSet, BodiesWithPrivilegeView

urlpatterns = [
    path("events", EventViewSet.as_view({"get": "list", "post": "create"})),
    path(
        "events/<pk>",
        EventViewSet.as_view({"get": "retrieve", "put": "update", "delete": "destroy"}),
    ),
    path(
        "events/<pk>/approve-mail",
        EventMailVerificationViewSet.as_view({"post": "approve_mail"}),
        name="event-approve-mail",
    ),
    path(
        "events/<pk>/reject-mail",
        EventMailVerificationViewSet.as_view({"post": "reject_mail"}),
        name="event-reject-mail",
    ),
    path("bodies-with-privilege/", BodiesWithPrivilegeView.as_view({"get": "get_bodies"}), name='bodies-with-privilege'),

]
