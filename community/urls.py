"""URLs for communities."""
from django.urls import path
from community.views import CommunityViewSet,PostViewSet,ModeratorViewSet

urlpatterns = [
    path('communities', CommunityViewSet.as_view({
        'get': 'list',
    })),#viewing the list of communities
    
    path('communitymoderators',ModeratorViewSet.as_view({
        'put':'update','delete':'delete'
    })),#verification by moderators

    path('communities/<pk>', CommunityViewSet.as_view({
        'get': 'retrieve',
    })),#viewing a particular community

    path('communityposts', PostViewSet.as_view({
        'get': 'list','post': 'create','put': 'update','delete': 'destroy','get':'featured_posts'
    })),#viewing the list of posts in their minimum view

    path('communityposts/<pk>', PostViewSet.as_view({
        'get': 'retrieve_full','delete': 'destroy'
    })),#to get the full view of a post

]
