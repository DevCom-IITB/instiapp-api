from django.contrib import admin
from roles.models import BodyRole
from roles.models import InstituteRole


class BodyRoleAdmin(admin.ModelAdmin):
    list_filter = ["body"]
    list_display = ("name", "body", "permissions")
    search_fields = ("body__name", "name")


class InstittuteRoleAdmin(admin.ModelAdmin):
    list_display = ("name", "permissions")
    search_fields = ["name"]


admin.site.register(BodyRole, BodyRoleAdmin)
admin.site.register(InstituteRole, InstittuteRoleAdmin)
