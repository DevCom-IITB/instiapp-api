"""Admin models for venter."""
from django.contrib import admin
from django.core.mail import send_mass_mail

from django.conf import settings
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
    list_display = ['name', 'email']
    model = Authorities

class ComplaintModelAdmin(admin.ModelAdmin):
    readonly_fields = ['created_by']
    list_display = ['description', 'report_date', 'status', 'email_status', 'email_list']
    list_editable = ['status']
    list_filter = ['status']
    filter_horizontal = ('authorities',)
    inlines = [CommentTabularInline, TagTabularInline, UserLikedTabularInline, ComplaintMediaTabularInline]
    exclude = ('tags', 'users_up_voted', 'media',)
    search_fields = ['status', 'description', 'created_by__name']
    actions = ['mark_as_resolved', 'mark_as_in_progress', 'mark_as_deleted', 'send_emails']

    @staticmethod
    def mark_as_resolved(modeladmin, request, queryset):
        """
        Admin action to change complaint status to 'Resolved'
        Queryset contains the selected complaints and this is a batch SQL UPDATE process for the complaint status
        """
        queryset.update(status='Resolved')

    @staticmethod
    def mark_as_in_progress(modeladmin, request, queryset):
        """
        Admin action to change complaint status to 'In Progress'
        Queryset contains the selected complaints, and this is a batch SQL UPDATE process for the complaint status
        """
        queryset.update(status='In Progress')

    @staticmethod
    def mark_as_deleted(modeladmin, request, queryset):
        """
        Admin action to change complaint status to 'In Progress'
        Queryset contains the selected complaints, and this is a batch SQL UPDATE process for the complaint status
        """
        queryset.update(status='Deleted')

    @staticmethod
    def send_emails(modeladmin, request, queryset):
        """
        Admin action to compose a preformatted email message and to send it to the selected authority's email ID
        Queryset contains selected complaints. This is a process to send a preformatted batch of emails to authorities
        For every complaint, the relevant information is extracted and turned into elements of the email as follows:

        Subject: Complaint from <User> on <DateTime object format> where datetime format is hardcoded

        Message: Multiline string containing variables stored within the complaint, along with a list of attached images

        Sender ID: Used for sending mails in accordance with the send_mass_mail function

        Recipient List: A list containing authorities to whom the email is to be sent

        The email messages are composed for all the selected complaints and appended to the mailing list.
        After this, send_mass_mail is used to send a tuple of the stored messages using django's default email backend
        """
        # List containing all the email messages to be sent, is being converted to tuple and sent using "send_mass_mail"
        mailing_list = []

        for item in queryset:
            input_list = [i for i in ComplaintMedia.objects.filter(complaint=item.id).values('image_url')]
            output_list = [images[key] for images in input_list for key in images]

            subject = f'Complaint from {item.created_by} on {item.report_date:%A, %d %b %Y at %I:%M %p}'

            # Checks for attachments and modifies the email message based on that

            message = (
                f'Complaint Description: {item.description}\n'
                f'Location Description: {item.location_description}\n'
                f'Status: {item.status}\n'
                f'Images: {", ".join(output_list)}'
            )

            # The 'DEFAULT_FROM_EMAIL' setting is recommended by django when the site has an independent mailing server
            sender_id = settings.DEFAULT_FROM_EMAIL

            # Retrieves the authority body's email id
            recipient_list = list(queryset.values_list('authorities__email', flat=True))

            # Composes the email to be sent to the authorities and stores it in the mailing list
            mailing_list.append((subject, message, sender_id, recipient_list))
        # Sends the e-mails stored in the mailing list to the respective authorities via send_mass_mail method in django
        send_mass_mail(tuple(mailing_list))
        queryset.update(email_status=True)

    class Meta:
        model = Complaints


admin.site.register(Complaints, ComplaintModelAdmin)
admin.site.register(Comment, CommentModelAdmin)
admin.site.register(TagUris)
admin.site.register(ComplaintMedia, ComplaintMediaModelAdmin)
admin.site.register(Authorities, AuthoritiesModelAdmin)
