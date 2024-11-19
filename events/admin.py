from django.contrib import admin
from events.models import Event, UserEventStatus


class EventAdmin(admin.ModelAdmin):
    list_filter = (
        "start_time",
        "bodies",
        "venues",
    )
    list_display = (
        "name",
        "all_bodies",
        "start_time",
        "end_time",
    )
    search_fields = ["name"]
    ordering = ("-start_time",)
    raw_id_fields = ("created_by",)


class UESAdmin(admin.ModelAdmin):
    list_filter = ("event__start_time",)
    list_display = ("event", "user", "status")
    ordering = ("-event__start_time",)
    raw_id_fields = ("user", "event")


admin.site.register(Event, EventAdmin)
admin.site.register(UserEventStatus, UESAdmin)
