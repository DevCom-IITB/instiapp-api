from django.contrib import admin
from locations.models import Location

class LocationAdmin(admin.ModelAdmin):
    list_filter = ('reusable',)
    list_display = ('short_name', 'name', 'reusable')
    search_fields = ['short_name', 'name']
    raw_id_fields = ('parent',)


admin.site.register(Location, LocationAdmin)
