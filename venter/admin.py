"""Admin models for venter."""
from django.contrib import admin
from django.core.mail import send_mail
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

class UserSubscribedTabularInline(admin.TabularInline):
    model = Complaints.subscriptions.through
    readonly_fields = ('userprofile',)
    verbose_name = 'Subscribed User'
    verbose_name_plural = 'Subscribed Users'

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
    list_display = ['report_date', 'status', 'email_status', 'email_list']
    list_editable = ['status']
    list_filter = ['status']
    filter_horizontal = ('authorities',)
    inlines = [
        CommentTabularInline,
        TagTabularInline,
        UserLikedTabularInline,
        ComplaintMediaTabularInline,
        UserSubscribedTabularInline
    ]
    exclude = ('tags', 'users_up_voted', 'media',)
    search_fields = ['status', 'description', 'created_by__name']
    actions = ['mark_as_resolved', 'mark_as_in_progress', 'mark_as_deleted', 'send_emails']

    @staticmethod
    def mark_as_resolved(modeladmin  , request, queryset):
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

        The email messages are sent using the send_mail() method, and use the four parameters listed above
        """

        for item in queryset:
            # Check if the complaint has a valid authority set. If none exists, remove the complaint from the queryset
            if not item.authorities.all().exists():
                continue

            input_list = [i for i in ComplaintMedia.objects.filter(complaint=item.id).values('image_url')]
            output_list = [images[key] for images in input_list for key in images]

            subject = f'Complaint from {item.created_by} on {item.report_date:%A, %d %b %Y at %I:%M %p}'

            message = f'{item.description}\n\n' \
                      f'Location Description: {item.location_description}\n\n' \
                      f'Status: {item.status}\n\n'
            # Adds links to attached images into the message if any
            if output_list:
                message = message + f'Images: {output_list}'

            # The 'DEFAULT_FROM_EMAIL' setting is recommended by django when the site has an independent mailing server
            sender_id = settings.DEFAULT_FROM_EMAIL

            # Retrieves a list of email ids for the selected authorities. Excludes the authority bodies with no email id
            recipient_list = queryset.values_list('authorities__email', flat=True).exclude(authorities__email=None)

            # Composes the email to be sent to the authorities and sends it to the recipients
            send_mail(subject, message, sender_id, recipient_list)

            item.email_status = True
            item.save()

    class Meta:
        model = Complaints


admin.site.register(Complaints, ComplaintModelAdmin)
admin.site.register(Comment, CommentModelAdmin)
admin.site.register(TagUris)
admin.site.register(ComplaintMedia, ComplaintMediaModelAdmin)
admin.site.register(Authorities, AuthoritiesModelAdmin)
