from django.contrib import admin
from locations.models import Location

class LocationAdmin(admin.ModelAdmin):
    list_filter = ('reusable',)
    search_fields = ['name']


admin.site.register(Location, LocationAdmin)
