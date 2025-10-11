from django.contrib import admin
from messmenu.models import Hostel, MessCalEvent
from messmenu.models import MenuEntry


class HostelAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ["name"]


class MessCalEventAdmin(admin.ModelAdmin):
    list_filter = (
        "datetime",
        "hostel",
    )
    list_display = (
        "user",
        "hostel",
        "title",
        "datetime",
    )


# Register your models here.
admin.site.register(Hostel, HostelAdmin)
admin.site.register(MenuEntry)
admin.site.register(MessCalEvent, MessCalEventAdmin)
