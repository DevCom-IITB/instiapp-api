"""URLs for users."""
from django.urls import path
from users.views import UserProfileViewSet ,UserSignatureViewSet
from roles.views import BodyRoleViewSet

urlpatterns = [
    path("users/<pk>", UserProfileViewSet.as_view({"get": "retrieve"})),
    path(
        "user-me",
        UserProfileViewSet.as_view(
            {"get": "retrieve_me", "put": "update_me", "patch": "update_me"}
        ),
    ),
    path("user-me/ues/<event_pk>", UserProfileViewSet.as_view({"get": "set_ues_me"})),
    path("user-me/unr/<news_pk>", UserProfileViewSet.as_view({"get": "set_unr_me"})),
    path("user-me/ucr/", UserProfileViewSet.as_view({"post": "set_ucr_me"})),
    path("user-me/ucpr/<post_pk>", UserProfileViewSet.as_view({"get": "set_upr_me"})),
    path(
        "user-me/subscribe-wp",
        UserProfileViewSet.as_view({"post": "subscribe_web_push"}),
    ),
    path("user-me/events", UserProfileViewSet.as_view({"get": "get_my_events"})),
    path("user-me/roles", BodyRoleViewSet.as_view({"get": "get_my_roles"})),
    path(
        "user-me/signatures",
        UserSignatureViewSet.as_view(
            {
                "get": "get_signatures",
                "post": "add_signature",
            }
        ),
        name="user-signatures",
    ),
    path(
        "user-me/signatures/<pk>",
        UserSignatureViewSet.as_view({"delete": "delete_signature"}),
        name="user-signature-detail",
    ),
]
