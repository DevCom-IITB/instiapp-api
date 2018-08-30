from django.contrib import admin
from bodies.models import Body, BodyChildRelation
from roles.models import BodyRole

class RoleInline(admin.StackedInline):
    model = BodyRole
    fields = ('name',)
    readonly_fields = ('name',)
    show_change_link = True

class BodyAdmin(admin.ModelAdmin):
    inlines = [RoleInline]

admin.site.register(Body, BodyAdmin)
admin.site.register(BodyChildRelation)
