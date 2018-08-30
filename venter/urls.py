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

from .views import ComplaintViewSet
from .views import ComplaintPostViewSet

urlpatterns = [

    path('get_complaints/', ComplaintViewSet.as_view()),

    path('get_complaints/<created_by__ldap_id>', ComplaintViewSet.as_view()),

    path('complaint/<created_by__ldap_id>', ComplaintPostViewSet.as_view(
        {'post': 'create'}
    )),

    # path('complaint_search', ComplaintViewSet.as_view(
    #     {'get': 'search'}
    # )),
    #
    # path('analyze_complaint', ComplaintViewSet.as_view(
    #     {'get': 'analyze'}
    # )),
    #
    # path('analyze_complaint_with_text', ComplaintViewSet.as_view(
    #     {'get': 'analyze_text'}
    # )),
    #
    # path('uploadFile', UploadViewSet.as_view(
    #     {'post': 'create'}
    # )),
    #
    # path('uploadFile/<pk>', UploadViewSet.as_view(
    #     {'get': 'retrieve'}
    # )),

]
