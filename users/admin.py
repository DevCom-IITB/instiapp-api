from django.contrib import admin
from users.models import UserProfile
from users.models import WebPushSubscription

class ProfileAdmin(admin.ModelAdmin):
    search_fields = ['name']

admin.site.register(UserProfile, ProfileAdmin)
admin.site.register(WebPushSubscription)
