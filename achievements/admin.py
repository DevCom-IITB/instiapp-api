from django.contrib import admin
from achievements.models import Achievement, Skill
from achievements.models import OfferedAchievement

class AchievementAdmin(admin.ModelAdmin):
    list_filter = ('body', 'verified', 'dismissed')
    list_display = ('user', 'body', 'title', 'verified', 'dismissed')
    ordering = ('-time_of_creation',)
    raw_id_fields = ('user', 'verified_by')


class OfferedAchievementAdmin(admin.ModelAdmin):
    list_filter = ('body',)
    list_display = ('event', 'body', 'title')
    ordering = ('-time_of_creation',)
    raw_id_fields = ('event',)

class SkillAdmin(admin.ModelAdmin):
    # list_filter = ('body', 'verified', 'dismissed')
    list_display = ('title', 'body')
    # ordering = ('-time_of_creation',)
    # raw_id_fields = ('user', 'verified_by')


admin.site.register(Achievement, AchievementAdmin)
admin.site.register(OfferedAchievement, OfferedAchievementAdmin)
admin.site.register(Skill, SkillAdmin)
