"""Admin models for venter."""
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
    verbose_name = 'Tag'
    verbose_name_plural = 'Tags'

class UserLikedTabularInline(admin.TabularInline):
    model = Complaints.users_up_voted.through
    readonly_fields = ('userprofile',)
    verbose_name = 'User up Voted'
    verbose_name_plural = 'Users up voted'

class ComplaintMediaTabularInline(admin.TabularInline):
    model = ComplaintMedia
    readonly_fields = ('image_url',)

class ComplaintMediaModelAdmin(admin.ModelAdmin):
    list_display = ['image_url', 'complaint']
    model = ComplaintMedia

class CommentModelAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'complaint', 'time']
    model = Comment

class ComplaintModelAdmin(admin.ModelAdmin):
    readonly_fields = ['created_by']
    list_display = ['report_date', 'status']
    list_editable = ['status']
    list_filter = ['status']
    inlines = [CommentTabularInline, TagTabularInline, UserLikedTabularInline, ComplaintMediaTabularInline]
    exclude = ('tags', 'users_up_voted', 'media',)
    search_fields = ['status', 'description', 'created_by__name']

    class Meta:
        model = Complaints


admin.site.register(Complaints, ComplaintModelAdmin)
admin.site.register(Comment, CommentModelAdmin)
admin.site.register(TagUris)
admin.site.register(ComplaintMedia, ComplaintMediaModelAdmin)
