"""URLs for communities."""
from django.urls import path
from community.views import CommunityViewSet, PostViewSet, ModeratorViewSet

urlpatterns = [
    path(
        "communities", CommunityViewSet.as_view({"get": "list", "post": "create"})
    ),  # viewing the list of communities
    path(
        "communities/<pk>",
        CommunityViewSet.as_view(
            {
                "get": "retrieve",
            }
        ),
    ),  # viewing a particular community
    path(
        "communityposts", PostViewSet.as_view({"get": "list", "post": "create"})
    ),  # viewing, creating, updating and deleting the list of posts in their minimum view
    path(
        "communityposts/<pk>",
        PostViewSet.as_view({"get": "retrieve_full", "put": "update"}),
    ),  # to get the full view of a post
    path(
        "communityposts/moderator/<pk>",
        ModeratorViewSet.as_view({"put": "change_status"}),
    ),  # manages all the privileges of a moderator.. changes status
    path(
        "communityposts/<action>/<pk>", PostViewSet.as_view({"put": "perform_action"})
    ),  # setting featured posts
]
