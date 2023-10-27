from django.contrib import admin
from bodies.models import Body, BodyChildRelation


class BodyAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ["name"]
    ordering = ("-time_of_creation",)


admin.site.register(Body, BodyAdmin)
admin.site.register(BodyChildRelation)
