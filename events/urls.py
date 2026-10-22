"""URLs for events."""
from django.urls import path
from events.views import EventViewSet, EventMailVerificationViewSet, BodiesWithPrivilegeView

urlpatterns = [
    path("events", EventViewSet.as_view({"get": "list", "post": "create"})),
    path("events-all", EventViewSet.as_view({"get": "list_all"})),
    path(
        "events/<pk>",
        EventViewSet.as_view({"get": "retrieve", "put": "update", "delete": "destroy"}),
    ),

    # NEW: pending events visible to verifiers
    path(
        "verifier-events",
        EventViewSet.as_view({"get": "verifier_events"}),
        name="verifier-events",
    ),

    # NEW: creator dashboard
    path(
        "my-events",
        EventViewSet.as_view({"get": "my_events"}),
        name="my-events",
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

    # NEW: resubmit rejected event
    path(
        "events/<pk>/resubmit",
        EventMailVerificationViewSet.as_view({"post": "resubmit"}),
        name="event-resubmit",
    ),

    path(
        "bodies-with-privilege",
        BodiesWithPrivilegeView.as_view({"get": "get_bodies"}),
        name="bodies-with-privilege",
    ),
    path(
        "bodies-with-privilege/",
        BodiesWithPrivilegeView.as_view({"get": "get_bodies"}),
        name="bodies-with-privilege-slash",
    ),
]
