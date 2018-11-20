"""Admin models for venter."""
from django.contrib import admin
from django.core.mail import send_mass_mail

from backend import settings_base
from venter.models import Complaints
from venter.models import Comment
from venter.models import TagUris
from venter.models import ComplaintMedia
from venter.models import Authorities

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

class AuthoritiesModelAdmin(admin.ModelAdmin):
    list_display = ['name', '__str__']
    model = Authorities

class ComplaintModelAdmin(admin.ModelAdmin):
    readonly_fields = ['created_by']
    list_display = ['report_date', 'status', 'authority_email']
    list_editable = ['status', 'authority_email']
    list_filter = ['status']
    inlines = [CommentTabularInline, TagTabularInline, UserLikedTabularInline, ComplaintMediaTabularInline]
    exclude = ('tags', 'users_up_voted', 'media',)
    search_fields = ['status', 'description', 'created_by__name']
    actions = ['mark_as_resolved', 'mark_as_in_progress', 'mark_as_deleted', 'send_emails']

    # Admin action to change complaint status to 'Resolved'
    def mark_as_resolved(self, request, queryset):  # pylint: disable=R0201
        queryset.update(status='Resolved')
    mark_as_resolved.short_description = "Mark selected complaints as Resolved"

    # Admin action to change complaint status to 'In Progress'
    def mark_as_in_progress(self, request, queryset):  # pylint: disable=R0201
        queryset.update(status='In Progress')
    mark_as_in_progress.short_description = "Mark selected complaints as In Progress"

    # Admin action to change complaint status to 'Deleted'
    def mark_as_deleted(self, request, queryset):  # pylint: disable=R0201
        queryset.update(status='Deleted')
    mark_as_deleted.short_description = "Mark selected complaints as Deleted"

    # Admin action for composing emails and sending them to the authorities
    def send_emails(self, request, queryset):  # pylint: disable=R0201
        input_list = []
        output_list = []
        mail_list = []

        for object in queryset: # pylint: disable=W0622
            for i in ComplaintMedia.objects.filter(complaint=object.id).values('image_url'):
                input_list.append(i)

            for images in input_list:
                for key in images:
                    output_list.append(images[key])

            subject = f'Complaint from {object.created_by} on {object.report_date.date()}'

            # Checks for attachments and modifies the email message based on that
            if output_list:
                message = (
                    f'Complaint Description: {object.description}\n'
                    f'Location Description: {object.location_description}\n'
                    f'Status: {object.status}\n'
                    f'Attachments: {output_list}'
                )

            elif not output_list:
                message = (
                    f'Complaint Description: {object.description}\n'
                    f'Location Description: {object.location_description}\n'
                    f'Status: {object.status}\n'
                )

            # The 'DEFAULT_FROM_EMAIL' setting is recommended by django when the site has an independent mailing server
            sender_id = settings_base.DEFAULT_FROM_EMAIL

            # Retrieves the authority body's email id
            recipient_list = [f'{object.authority_email}']

            # Composes the email to be sent to the authorities and stores it in the mailing list
            
            mail_list.append((subject, message, sender_id, recipient_list))
        #Sends the e-mails stored in the mailing list to the respective authorities via send_mass_mail method in django
        send_mass_mail(tuple(mail_list))

    send_emails.short_description = "Send emails to the authorities"


    class Meta:
        model = Complaints


admin.site.register(Complaints, ComplaintModelAdmin)
admin.site.register(Comment, CommentModelAdmin)
admin.site.register(TagUris)
admin.site.register(ComplaintMedia, ComplaintMediaModelAdmin)
admin.site.register(Authorities, AuthoritiesModelAdmin)
