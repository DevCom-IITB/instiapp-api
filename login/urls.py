"""URLs for login."""
from django.urls import path
from login.views import LoginViewSet

urlpatterns = [
    path('login', LoginViewSet.as_view({'get': 'login'})),
    path('g-login', LoginViewSet.as_view({'get': 'g_login'})),
    path('pass-login', LoginViewSet.as_view({'get': 'pass_login'})),
    path('login/get-user', LoginViewSet.as_view({'get': 'get_user'})),
    path('logout', LoginViewSet.as_view({'get': 'logout'})),
]
