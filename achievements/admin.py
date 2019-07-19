from django.contrib import admin
from achievements.models import Achievement

class AchievementAdmin(admin.ModelAdmin):
    list_filter = ('body','verified','dismissed')
    list_display = ('user', 'body', 'description', 'verified', 'dismissed')
    ordering = ('-time_of_creation',)
    raw_id_fields = ('user', 'verified_by')

admin.site.register(Achievement, AchievementAdmin)
