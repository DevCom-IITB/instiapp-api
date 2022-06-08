from django.contrib import admin
from messmenu.models import Hostel, MessCalEvent
from messmenu.models import MenuEntry

# Register your models here.
admin.site.register(Hostel)
admin.site.register(MenuEntry)
admin.site.register(MessCalEvent)
