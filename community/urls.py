"""URLs for placments."""
from django.urls import path
from community.views import CommunityViewSet,PostViewSet

urlpatterns = [
    path('communities', CommunityViewSet.as_view({
        'get': 'list',
    })),#viewing the list of communities

    path('communities/<pk>', CommunityViewSet.as_view({
        'get': 'retrieve',
    })),#viewing a particular community

    path('communityposts', PostViewSet.as_view({
        'get': 'list','post': 'create_post','put': 'update_post','delete': 'destroy'
    })),#viewing the list of posts in their minimum view

    path('communityposts/<pk>', PostViewSet.as_view({
        'get': 'retrieve_full','delete': 'destroy'
    })),#to get the full view of a post

    path('communitypostcomments', PostViewSet.as_view({
        'get':'list','post': 'create_comment','put': 'update_comment', 'delete': 'destroy_comment'
    })),#updating a comment and creating one

    path('communitiespostcomments/<pk>', PostViewSet.as_view({
        'delete': 'destroy'
    })),#to get the full view of a post
]
