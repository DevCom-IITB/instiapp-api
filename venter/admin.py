from django.contrib import admin
from django.contrib.admin import SimpleListFilter

from .models import complaints
from .models import comment
from .models import tag_uris


class CommentTabularInline(admin.TabularInline):
    model = comment
    readonly_fields = ('text', 'time', 'user',)


class TagTabularInline(admin.TabularInline):
    model = complaints.tags.through
    verbose_name = "Tag"
    verbose_name_plural = "Tags"


class UserLikedTabularInline(admin.TabularInline):
    model = complaints.users_up_voted.through
    verbose_name = "User up Voted"
    verbose_name_plural = "Users up voted"


class MediaTabularInline(admin.TabularInline):
    model = complaints.media.through
    verbose_name = "Media"
    verbose_name_plural = "Medias"


class CommentModelAdmin(admin.ModelAdmin):
    list_display = ["__str__", "user", "complaint", "time"]
    model = comment


class ComplaintModelAdmin(admin.ModelAdmin):
    list_display = ["__str__", "created_by", "report_date", "status"]
    list_editable = ["status"]
    list_filter = ["status"]
    inlines = [CommentTabularInline, TagTabularInline, UserLikedTabularInline, MediaTabularInline]
    exclude = ('tags', 'users_up_voted', 'media',)
    search_fields = ["status", "description", "created_by__name"]

    class Meta:
        model = complaints


admin.site.register(complaints, ComplaintModelAdmin)
admin.site.register(comment, CommentModelAdmin)
admin.site.register(tag_uris)
