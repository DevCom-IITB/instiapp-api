from django.contrib import admin
from roles.models import BodyRole
from roles.models import InstituteRole, CommunityRole

class BodyRoleAdmin(admin.ModelAdmin):
    list_filter = ['body']
    list_display = ('name', 'body', 'permissions')
    search_fields = ('body__name', 'name')

class CommunityRoleAdmin(admin.ModelAdmin):
    list_filter = ['community']
    list_display = ('name', 'community', 'permissions')
    search_fields = ('community__name', 'name')
class InstittuteRoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'permissions')
    search_fields = ['name']


admin.site.register(BodyRole, BodyRoleAdmin)
admin.site.register(CommunityRole, CommunityRoleAdmin)
admin.site.register(InstituteRole, InstittuteRoleAdmin)
