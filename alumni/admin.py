from django.contrib import admin
from alumni.models import AlumniUser


class AlumniUserAdmin(admin.ModelAdmin):
    list_display = ("ldap", "keyStored", "timeLoginRequest")
    search_fields = ["ldap"]
i

admin.site.register(AlumniUser, AlumniUserAdmin)
