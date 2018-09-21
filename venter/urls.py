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

from django.urls import path

from venter.views import ComplaintViewSet, CommentViewSet

urlpatterns = [

    path('complaints', ComplaintViewSet.as_view(
        {'post': 'create','get':'list'}
    )),

    path('complaints/<pk>', ComplaintViewSet.as_view(
        {'get': 'retrieve', 'put': 'update'}
    )),

    path('complaints/<pk>/comments', CommentViewSet.as_view(
        {'post': 'create'}
    )),

    path('comments/<pk>', CommentViewSet.as_view(
        {'put': 'update', 'delete': 'destroy', 'get': 'retrieve'}
    )),
]
