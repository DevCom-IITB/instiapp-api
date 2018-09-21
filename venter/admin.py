from django.contrib import admin

from venter.models import Complaints
from venter.models import Comment
from venter.models import TagUris
from venter.models import ComplaintMedia


class CommentTabularInline(admin.TabularInline):
    model = Comment
    readonly_fields = ('text', 'time', 'commented_by',)


class TagTabularInline(admin.TabularInline):
    model = Complaints.tags.through
    verbose_name = "Tag"
    verbose_name_plural = "Tags"


class UserLikedTabularInline(admin.TabularInline):
    model = Complaints.users_up_voted.through
    verbose_name = "User up Voted"
    verbose_name_plural = "Users up voted"


class ComplaintMediaTabularInline(admin.TabularInline):
    model = ComplaintMedia
    readonly_fields = ('image_url',)


class ComplaintMediaModelAdmin(admin.ModelAdmin):
    list_display = ["image_url", "complaint"]
    model = ComplaintMedia


class CommentModelAdmin(admin.ModelAdmin):
    list_display = ["__str__", "commented_by", "complaint", "time"]
    model = Comment


class ComplaintModelAdmin(admin.ModelAdmin):
    list_display = ["__str__", "created_by", "report_date", "status"]
    list_editable = ["status"]
    list_filter = ["status"]
    inlines = [CommentTabularInline, TagTabularInline, UserLikedTabularInline, ComplaintMediaTabularInline]
    exclude = ('tags', 'users_up_voted', 'media',)
    search_fields = ["status", "description", "created_by__name"]
    actions = ['mark_as_resolved', 'mark_as_in_progress', 'mark_as_deleted']

    def mark_as_resolved(self, request, queryset):
        queryset.update(status='Resolved')
        self.short_description = "Mark selected complaints as Resolved"

    def mark_as_in_progress(self, request, queryset):
        queryset.update(status='In Progress')
        self.short_description = "Mark selected complaints as In Progress"

    def mark_as_deleted(self, request, queryset):
        queryset.update(status='Deleted')
        self.short_description = "Mark selected complaints as Deleted"

    class Meta:
        model = Complaints


admin.site.register(Complaints, ComplaintModelAdmin)
admin.site.register(Comment, CommentModelAdmin)
admin.site.register(TagUris)
admin.site.register(ComplaintMedia, ComplaintMediaModelAdmin)
