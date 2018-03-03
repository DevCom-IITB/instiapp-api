from django.contrib import admin
from events.models import Event, UserEventStatus

admin.site.register(Event)
admin.site.register(UserEventStatus)
