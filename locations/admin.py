from django.contrib import admin
from locations.models import Location

class LocationAdmin(admin.ModelAdmin):
    list_filter = ('reusable',)
    list_display = ('short_name', 'name', 'reusable')
    search_fields = ['short_name', 'name']


admin.site.register(Location, LocationAdmin)
