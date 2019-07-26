from django.contrib import admin
from users.models import UserProfile
from users.models import UserFormerRole
from users.models import WebPushSubscription
from users.models import UserTagCategory
from users.models import UserTag

class ProfileAdmin(admin.ModelAdmin):
    search_fields = ['name', 'roll_no', 'ldap_id']
    list_display = ('name', 'roll_no', 'department', 'degree', 'last_ping')
    list_filter = ('last_ping', 'join_year', 'department', 'degree')
    raw_id_fields = ('user',)

class UserFormerRoleAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'year')
    raw_id_fields = ('user',)
    ordering = ('-year', 'role')

class WebPushSubscriptionAdmin(admin.ModelAdmin):
    raw_id_fields = ('user',)

class UserTagAdmin(admin.ModelAdmin):
    list_display = ('category', 'name', 'target', 'secondary_target')
    ordering = ('category', 'name')


admin.site.register(UserProfile, ProfileAdmin)
admin.site.register(UserFormerRole, UserFormerRoleAdmin)
admin.site.register(WebPushSubscription, WebPushSubscriptionAdmin)
admin.site.register(UserTagCategory)
admin.site.register(UserTag, UserTagAdmin)
