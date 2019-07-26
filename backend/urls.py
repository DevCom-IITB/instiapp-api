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
from django.urls import path, include
from django.contrib.sitemaps.views import sitemap
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from backend.sitemap import sitemaps

def api_base(prefix=None):
    """Get the base URL for an endpoint set."""
    if prefix is None:
        return 'api/'
    return 'api/%s/' % prefix


# Set admin site titles
admin.site.site_header = 'InstiApp admin'
admin.site.site_title = 'InstiApp admin'

# Swagger schema view
schema_view = get_schema_view(
    openapi.Info(
        title="InstiApp API",
        default_version='v1',
        description="InstiApp IIT Bombay API",
        terms_of_service="https://insti.app/tos.html",
        contact=openapi.Contact(email="support@insti.app"),
        license=openapi.License(name="AGPLv3"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # Admin site
    path('admin/', admin.site.urls),

    # API
    path(api_base(), include('achievements.urls')),
    path(api_base(), include('bodies.urls')),
    path(api_base(), include('events.urls')),
    path(api_base(), include('locations.urls')),
    path(api_base(), include('users.urls')),
    path(api_base(), include('upload.urls')),
    path(api_base(), include('roles.urls')),
    path(api_base(), include('messmenu.urls')),
    path(api_base(), include('news.urls')),
    path(api_base(), include('login.urls')),
    path(api_base(), include('placements.urls')),
    path(api_base(), include('other.urls')),
    path(api_base('venter'), include("venter.urls")),

    # Non-API
    path('', include('prerender.urls')),
    path(api_base('docs'), schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('sitemap.xml', sitemap, {
        'sitemaps': sitemaps()
    }, name='django.contrib.sitemaps.views.sitemap')
]
