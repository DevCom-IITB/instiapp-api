from django.contrib import admin
from roles.models import BodyRole, InstituteRole


class BodyRoleAdmin(admin.ModelAdmin):
    list_filter = ["body"]
    list_display = ("name", "body", "display_permissions")
    search_fields = ("body__name", "name")

    @admin.display(description="Permissions")
    def display_permissions(self, obj):
        return ", ".join(obj.permissions)


class InstittuteRoleAdmin(admin.ModelAdmin):
    list_display = ("name", "display_permissions")
    search_fields = ["name"]

    @admin.display(description="Permissions")
    def display_permissions(self, obj):
        return ", ".join(obj.permissions)


admin.site.register(BodyRole, BodyRoleAdmin)
admin.site.register(InstituteRole, InstittuteRoleAdmin)