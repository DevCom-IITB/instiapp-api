from django.contrib import admin
from locations.models import Location

class LocationAdmin(admin.ModelAdmin):
    list_filter = ('reusable',)

admin.site.register(Location, LocationAdmin)
