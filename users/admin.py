from django.contrib import admin
from users.models import UserProfile
from users.models import WebPushSubscription
from users.models import UserTagCategory
from users.models import UserTag

class ProfileAdmin(admin.ModelAdmin):
    search_fields = ['name', 'roll_no']
    list_display = ('name', 'roll_no', 'department', 'degree')
    list_filter = ('join_year', 'department', 'degree')


admin.site.register(UserProfile, ProfileAdmin)
admin.site.register(WebPushSubscription)
admin.site.register(UserTagCategory)
admin.site.register(UserTag)
