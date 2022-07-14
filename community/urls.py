"""URLs for communities."""
from django.urls import path
from community.views import CommunityViewSet,PostViewSet,ModeratorViewSet

urlpatterns = [
    path('communities', CommunityViewSet.as_view({
        'get': 'list',
    })),#viewing the list of communities
    
    path('communitymoderators',ModeratorViewSet.as_view({
        'put':'update','delete':'delete',
    })),#verification by moderators
    path('communitypending_posts',ModeratorViewSet.as_view({
        'get':'pending_posts',
    })),#viewing pending posts
    path('communityreported_content',ModeratorViewSet.as_view({
        'get':'reported_content',
    })),#viewing reported content
    path('communityhidden_posts',ModeratorViewSet.as_view({
        'get':'hidden_posts',
    })),
    path('communities/<pk>', CommunityViewSet.as_view({
        'get': 'retrieve',
    })),#viewing a particular community
    path('communityfeatured_posts',PostViewSet.as_view({
        'get':'featured_posts',
    })),#for viewing featured posts
    path('communityposts', PostViewSet.as_view({
        'get': 'list','post': 'create','put': 'update','delete': 'destroy',
    })),#viewing the list of posts in their minimum view

    path('communityposts/<pk>', PostViewSet.as_view({
        'get': 'retrieve_full','delete': 'destroy'
    })),#to get the full view of a post

]
