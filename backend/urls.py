"""backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from rest_framework_swagger.views import get_swagger_view

from bodies.views import BodyViewSet
from bodies.views import BodyFollowersViewSet
from events.views import EventViewSet
from locations.views import LocationViewSet
from upload.views import UploadViewSet
from users.views import UserProfileViewSet
from login.views import LoginViewSet
from roles.views import BodyRoleViewSet
from placements.views import PlacementBlogViewset
from news.views import NewsFeedViewset
from messmenu.views import get_mess
from other.views import OtherViewset
import prerender.views as pr

urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/bodies', BodyViewSet.as_view({'get':'list', 'post':'create'})),
    path('api/bodies/<pk>', BodyViewSet.as_view(
        {'get':'retrieve', 'put':'update', 'delete':'destroy'}
    ), name='body-detail'),
    path('api/bodies/<pk>/followers', BodyFollowersViewSet.as_view(
        {'get':'retrieve'}
    ), name='body-followers'),
    path('api/bodies/<pk>/follow', BodyViewSet.as_view(
        {'get':'follow'}
    )),

    path('api/events', EventViewSet.as_view(
        {'get':'list', 'post':'create'}
    )),
    path('api/events/<pk>', EventViewSet.as_view(
        {'get':'retrieve', 'put':'update', 'delete':'destroy'}
    ), name='event-detail'),

    path('api/locations', LocationViewSet.as_view(
        {'get':'list', 'post':'create'}
    )),
    path('api/locations/<pk>', LocationViewSet.as_view(
        {'get':'retrieve', 'put':'update', 'delete':'destroy'}
    ), name='location-detail'),

    path('api/users/<pk>', UserProfileViewSet.as_view(
        {'get':'retrieve'}
    )),

    path('api/upload', UploadViewSet.as_view(
        {'post':'create'}
    )),
    path('api/upload/<pk>', UploadViewSet.as_view(
        {'get':'retrieve', 'delete':'destroy'}
    )),

    path('api/login', LoginViewSet.as_view({'get':'login'})),
    path('api/login/get-user', LoginViewSet.as_view({'get':'get_user'})),
    path('api/logout', LoginViewSet.as_view({'get':'logout'})),

    path('api/user-me', UserProfileViewSet.as_view(
        {'get':'retrieve_me', 'put':'update_me', 'patch':'update_me'}
    )),
    path('api/user-me/ues/<event_pk>', UserProfileViewSet.as_view({'get':'set_ues_me'})),
    path('api/user-me/unr/<news_pk>', UserProfileViewSet.as_view({'get':'set_unr_me'})),
    path('api/user-me/events', UserProfileViewSet.as_view({'get':'get_my_events'})),
    path('api/user-me/roles', BodyRoleViewSet.as_view({'get':'get_my_roles'})),

    path('api/roles', BodyRoleViewSet.as_view(
        {'post':'create'}
    )),
    path('api/roles/<pk>', BodyRoleViewSet.as_view(
        {'get':'retrieve', 'put':'update', 'delete':'destroy'}
    )),

    path('api/placement-blog', PlacementBlogViewset.as_view({'get':'placement_blog'})),
    path('api/training-blog', PlacementBlogViewset.as_view({'get':'training_blog'})),

    path('api/news', NewsFeedViewset.as_view({'get':'news_feed'})),

    path('api/mess', get_mess),

    path('api/search', OtherViewset.as_view({'get':'search'})),

    # -------------- PRERENDER --------------- #
    path('', pr.root),
    path('feed', pr.root),
    path('news', pr.news),
    path('explore', pr.explore),
    path('user/<pk>', pr.user_details),
    path('event/<pk>', pr.event_details),
    path('org/<pk>', pr.body_details),
    path('body-tree/<pk>', pr.body_tree),

    # -------------- DOCS -------------------- #
    path('docs/', get_swagger_view(title='InstiApp API')),
]
