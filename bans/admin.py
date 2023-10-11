from django.contrib import admin
from bans.models import SSOBan

# Register your models here.


class SSOBansAdmin(admin.ModelAdmin):
    list_display = ("banned_user", "banned_by", "id")


admin.site.register(SSOBan, SSOBansAdmin)
