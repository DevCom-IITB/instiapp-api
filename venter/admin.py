"""Admin models for venter."""
from django.contrib import admin
from django.core.mail import send_mass_mail
from backend import settings_base

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
    actions = ['mark_as_resolved', 'mark_as_in_progress', 'mark_as_deleted', 'send_emails']

    def mark_as_resolved(self, request, queryset):
        queryset.update(status='Resolved')

    mark_as_resolved.short_description = "Mark selected complaints as Resolved"

    def mark_as_in_progress(self, request, queryset):
        queryset.update(status='In Progress')

    mark_as_in_progress.short_description = "Mark selected complaints as In Progress"

    def mark_as_deleted(self, request, queryset):
        queryset.update(status='Deleted')

    mark_as_deleted.short_description = "Mark selected complaints as Deleted"

    def send_emails(self, request, queryset):
        mail_list = []
        input_list = []
        output_list = []

        for object in queryset:
            for i in ComplaintMedia.objects.filter(complaint=object.id).values('image_url'):
                input_list.append(i)

            for images in input_list:
                for key in images:
                    output_list.append(images[key])

            subject = 'Complaint from %s on %s' % (object.created_by, object.report_date)
            if output_list:
                message = '%s \nLocation Description: %s \nStatus: %s \nAttachments: %s' % (
                    object.description, object.location_description, object.status, output_list)
            elif not output_list:
                message = '%s \nLocation Description: %s \nStatus: %s' % (
                    object.description, object.location_description, object.status)
            sender_id = settings_base.DEFAULT_FROM_EMAIL
            recipient_list = ['%s' % object.authority_email]
            email_message = (subject, message, sender_id, recipient_list)
            mail_list.append(email_message)
            send_mass_mail(tuple(mail_list))

    send_emails.short_description = "Send emails to the authorities"

    class Meta:
        model = Complaints


admin.site.register(Complaints, ComplaintModelAdmin)
admin.site.register(Comment, CommentModelAdmin)
admin.site.register(TagUris)
admin.site.register(ComplaintMedia, ComplaintMediaModelAdmin)
