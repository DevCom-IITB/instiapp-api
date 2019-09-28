"""Admin models for venter."""
from django.contrib import admin
from django.core.mail import send_mail
from django.conf import settings
from venter.models import Complaint
from venter.models import ComplaintComment
from venter.models import ComplaintTag
from venter.models import ComplaintImage
from venter.models import ComplaintAuthority

class ComplaintCommentTabularInline(admin.TabularInline):
    model = ComplaintComment
    readonly_fields = ('text', 'time', 'commented_by',)

class TagTabularInline(admin.TabularInline):
    model = Complaint.tags.through
    verbose_name = 'Tag'
    verbose_name_plural = 'Tags'

class UserLikedTabularInline(admin.TabularInline):
    model = Complaint.users_up_voted.through
    readonly_fields = ('userprofile',)
    verbose_name = 'User up Voted'
    verbose_name_plural = 'Users up voted'

class UserSubscribedTabularInline(admin.TabularInline):
    model = Complaint.subscriptions.through
    readonly_fields = ('userprofile',)
    verbose_name = 'Subscribed User'
    verbose_name_plural = 'Subscribed Users'

class ComplaintImageTabularInline(admin.TabularInline):
    model = ComplaintImage
    readonly_fields = ('image_url',)

class ComplaintImageModelAdmin(admin.ModelAdmin):
    list_display = ['image_url', 'complaint']
    raw_id_fields = ('complaint',)
    model = ComplaintImage

class ComplaintCommentModelAdmin(admin.ModelAdmin):
    list_display = ['text', 'complaint', 'time']
    readonly_fields = ('commented_by', 'complaint')
    model = ComplaintComment

class ComplaintAuthorityModelAdmin(admin.ModelAdmin):
    list_display = ['name', 'email']
    model = ComplaintAuthority

class ComplaintModelAdmin(admin.ModelAdmin):
    readonly_fields = ['created_by']
    list_display = ['report_date', 'status', 'email_list', 'email_sent_to']
    list_editable = ['status']
    list_filter = ['status']
    filter_horizontal = ('authorities',)
    inlines = [
        ComplaintCommentTabularInline,
        TagTabularInline,
        UserLikedTabularInline,
        ComplaintImageTabularInline,
        UserSubscribedTabularInline
    ]
    exclude = ('tags', 'users_up_voted', 'media', 'subscriptions')
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

        The email messages are sent using the send_mail() method, and use the four parameters listed above
        """

        for item in queryset:
            # Check if the complaint has a valid authority set. If none exists, remove the complaint from the queryset
            if not item.authorities.all().exists():
                continue

            input_list = list(ComplaintImage.objects.filter(complaint=item.id).values('image_url'))
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
            authority = item.authorities.values_list('name', flat=True)
            authorities_sent = ', '.join(authority)

            # Composes the email to be sent to the authorities and sends it to the recipients
            send_mail(subject, message, sender_id, recipient_list)

            # check if email_sent_to list is empty or not, if empty assign auth value else append auth value
            if item.email_sent_to:
                item.email_sent_to += ', ' + authorities_sent
            else:
                item.email_sent_to = authorities_sent

            item.authorities.clear()
            item.status = 'In Progress'
            item.email_status = True
            item.save()

    class Meta:
        model = Complaint


admin.site.register(Complaint, ComplaintModelAdmin)
admin.site.register(ComplaintComment, ComplaintCommentModelAdmin)
admin.site.register(ComplaintTag)
admin.site.register(ComplaintImage, ComplaintImageModelAdmin)
admin.site.register(ComplaintAuthority, ComplaintAuthorityModelAdmin)
