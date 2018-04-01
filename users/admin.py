from django.contrib import admin
from users.models import UserProfile

class ProfileAdmin(admin.ModelAdmin):
    search_fields = ['name']

admin.site.register(UserProfile, ProfileAdmin)
