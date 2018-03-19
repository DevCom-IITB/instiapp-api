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

from bodies.views import BodyViewSet
from bodies.views import BodyFollowersViewSet
from events.views import EventViewSet
from events.views import UserEventStatusViewSet
from locations.views import LocationViewSet
from upload.views import UploadViewSet
from users.views import UserProfileViewSet
from login.views import LoginViewSet
from roles.views import BodyRoleViewSet

urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/bodies', BodyViewSet.as_view({'get':'list', 'post':'create'})),
    path('api/bodies/<pk>', BodyViewSet.as_view(
        {'get':'retrieve', 'put':'update', 'delete':'destroy'}
    ), name='body-detail'),
    path('api/bodies/<pk>/followers', BodyFollowersViewSet.as_view(
        {'get':'retrieve'}
    ), name='body-followers'),

    path('api/events', EventViewSet.as_view(
        {'get':'list', 'post':'create'}
    )),
    path('api/events/<pk>', EventViewSet.as_view(
        {'get':'retrieve', 'put':'update', 'delete':'destroy'}
    ), name='event-detail'),
    path('api/events-locations', EventViewSet.as_view(
        {'post':'locations'}
    )),

    path('api/events-users', UserEventStatusViewSet.as_view(
        {'get':'list', 'post':'create'}
    )),
    path('api/events-users/<pk>', UserEventStatusViewSet.as_view(
        {'get':'retrieve', 'put':'update', 'delete':'destroy'}
    )),

    path('api/locations', LocationViewSet.as_view(
        {'get':'list', 'post':'create'}
    )),
    path('api/locations/<pk>', LocationViewSet.as_view(
        {'get':'retrieve', 'put':'update', 'delete':'destroy'}
    ), name='location-detail'),

    path('api/users/<pk>', UserProfileViewSet.as_view(
        {'get':'retrieve', 'put':'update', 'delete':'destroy'}
    ), name='userprofile-detail'),
    path('api/users/<pk>/followed_bodies_events', UserProfileViewSet.as_view(
        {'get':'followed_bodies_events'}
    )),
    path('api/users', UserProfileViewSet.as_view(
        {'get':'list', 'post':'create'}
    )),

    path('api/upload', UploadViewSet.as_view(
        {'get':'list', 'post':'create'}
    )),
    path('api/upload/<pk>', UploadViewSet.as_view(
        {'get':'retrieve', 'delete':'destroy'}
    )),

    path('api/login', LoginViewSet.as_view({'get':'login'})),
    path('api/login/get-user', LoginViewSet.as_view({'get':'get_user'})),
    path('api/logout', LoginViewSet.as_view({'get':'logout'})),
    path('api/login-page', LoginViewSet.as_view({'get':'login_page'})),

    path('api/roles', BodyRoleViewSet.as_view(
        {'get':'list', 'post':'create'}
    )),
    path('api/roles/<pk>', BodyRoleViewSet.as_view(
        {'get':'retrieve', 'put':'update', 'delete':'destroy'}
    )),
]
