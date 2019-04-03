"""Extra models for notifications."""
from uuid import uuid4
from dateutil.parser import parse
from django.db import models
from django.contrib.sessions.models import Session
from django.utils import timezone

class Device(models.Model):
    """A device to which a user is logged in.
    To be used chiefly for sending notifications."""

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    time_of_creation = models.DateTimeField(auto_now_add=True)
    last_ping = models.DateTimeField()
    last_refresh = models.DateTimeField(default=parse('1970-01-01T00:00:00Z'))

    user = models.ForeignKey('users.UserProfile', on_delete=models.CASCADE, related_name='devices')
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='devices')

    fcm_id = models.CharField(max_length=200, null=True, blank=True)

    application = models.CharField(max_length=50, blank=True)
    app_version = models.CharField(max_length=50, blank=True)
    platform = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.user.name

    def supports_rich(self):
        """Check if this device supports data messages."""

        # Check for flutter and iOS
        if self.application == 'app.insti.flutter':
            return False
        if self.application == 'app.insti.ios':
            return False

        # Try parsing the app version
        try:
            return int(self.app_version) >= 17
        except ValueError:
            return False

    def process_rich(self, data_message):
        """Add device specific fields to the data message."""

        # Add click_action for flutter
        if self.application == 'app.insti.flutter':
            data_message['click_action'] = 'FLUTTER_NOTIFICATION_CLICK'

        return data_message

    def needs_refresh(self):
        """Returns if information from Firebase is stale."""

        # Check if last refresh was older than 12 hours
        return (timezone.now() - self.last_refresh).total_seconds() > 43200
