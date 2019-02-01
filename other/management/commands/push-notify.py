"""Chore to send push notifications."""
from django.core.management.base import BaseCommand
from django.conf import settings
from pyfcm import FCMNotification
from notifications.models import Notification

from helpers.fcm import send_notification_fcm
from helpers.fcm import send_fcm_notification_message
from helpers.fcm import get_rich_notification
from helpers.webpush import send_notification_webpush

class Command(BaseCommand):
    help = 'Sends push notifications'

    def handle(self, *args, **options):  # noqa: C901
        """Send Push notifications."""

        webpush_sent = 0
        webpush_total = 0
        fcm_sent = 0

        push_service = FCMNotification(api_key=settings.FCM_SERVER_KEY)

        # Iterate all unsent notifications
        for notification in Notification.objects.filter(emailed=False)[:1000]:

            # Check invalid subscriptions
            if not notification or not notification.actor:
                continue

            # Get the user's profile
            profile = notification.recipient.profile

            # Check bad users
            if not profile:
                continue

            # Stop the spam!
            notification.emailed = True
            notification.save()

            # Get rich notification
            data_message = get_rich_notification(notification)

            # Retro method for transition
            if profile.fcm_id and profile.fcm_id != '':
                send_fcm_notification_message(push_service, profile.fcm_id, data_message)

            # Send FCM push notification
            for device in profile.devices.all():
                fcm_sent += send_notification_fcm(push_service, device, data_message)

            # For each web push subscription
            for subscription in profile.web_push_subscriptions.all():
                webpush_total += 1
                webpush_sent += send_notification_webpush(subscription, data_message)

        print(
            "WebPush:", webpush_sent,
            "WebPush FAIL:", webpush_total - webpush_sent,
            "FCM:", fcm_sent
        )
        self.stdout.write(self.style.SUCCESS('Push notification chore completed successfully'))
