from django.contrib import admin
from other.models import Device

class DeviceAdmin(admin.ModelAdmin):
    list_filter = ('application', 'last_ping', 'platform', 'app_version')
    list_display = ('user', 'application', 'platform', 'last_ping', 'app_version')
    ordering = ('-last_ping',)
    search_fields = ['user__name']
    raw_id_fields = ('user', 'session')


admin.site.register(Device, DeviceAdmin)
