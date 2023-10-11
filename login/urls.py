"""URLs for login."""
from django.urls import path
from login.views import LoginViewSet

urlpatterns = [
    path("login", LoginViewSet.as_view({"get": "login"})),
    path("pass-login", LoginViewSet.as_view({"get": "pass_login"})),
    path("login/get-user", LoginViewSet.as_view({"get": "get_user"})),
    path("logout", LoginViewSet.as_view({"get": "logout"})),
    path("alumniLogin", LoginViewSet.as_view({"get": "alumni_login"})),
    path("alumniOTP", LoginViewSet.as_view({"get": "alumni_otp_conf"})),
    path("resendAlumniOTP", LoginViewSet.as_view({"get": "resend_alumni_otp"})),
]
