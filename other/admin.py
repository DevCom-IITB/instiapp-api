from django.contrib import admin
from notifications.models import Notification
from notifications.admin import NotificationAdmin
from other.models import Device

class DeviceAdmin(admin.ModelAdmin):
    list_filter = ('application', 'last_ping', 'platform', 'app_version')
    list_display = ('user', 'application', 'platform', 'last_ping', 'app_version')
    ordering = ('-last_ping',)
    search_fields = ['user__name']
    raw_id_fields = ('user', 'session')

class CustomNotificationAdmin(NotificationAdmin):
    list_display = ('recipient', 'actor', 'level', 'unread', 'deleted', 'emailed')
    list_filter = ('level', 'unread', 'deleted', 'emailed', 'timestamp',)


admin.site.register(Device, DeviceAdmin)

admin.site.unregister(Notification)
admin.site.register(Notification, CustomNotificationAdmin)
