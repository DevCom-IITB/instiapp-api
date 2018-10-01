"""URLs for other app."""
from django.urls import path
from other.views import OtherViewset

urlpatterns = [
    path('search', OtherViewset.as_view({'get': 'search'})),
    path('notifications', OtherViewset.as_view({'get': 'get_notifications'})),
    path('notifications/read', OtherViewset.as_view({'get': 'mark_all_notifications_read'})),
    path('notifications/read/<pk>', OtherViewset.as_view({'get': 'mark_notification_read'})),
]
