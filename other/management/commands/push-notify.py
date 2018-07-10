"""Chore to send push notifications."""
import json
from django.core.management.base import BaseCommand
from django.conf import settings
from pywebpush import webpush, WebPushException
from users.models import UserProfile

def send_push(subscription, payload):
    """Send a single push notification."""
    webpush(
        subscription_info=subscription,
        data=json.dumps(payload),
        ttl=30,
        vapid_private_key=settings.VAPID_PRIV_KEY,
        vapid_claims={
            "sub": "mailto:support@radialapps.com",
        }
    )

class Command(BaseCommand):
    help = 'Sends push notifications'

    def handle(self, *args, **options):
        """Send Push notifications."""

        sent = 0
        failed = 0

        # Iterate all users
        for profile in UserProfile.objects.prefetch_related(
                'web_push_subscriptions', 'user').all():

            # Check bad users
            if not profile or not profile.user:
                continue

            # For each notification
            for notification in profile.user.notifications.filter(unread=True, emailed=False):

                # Check invalid subscriptions
                if not notification or not notification.actor:
                    continue

                # For each subscription
                for subscription in profile.web_push_subscriptions.all():

                    # Stop the spam!
                    notification.emailed = True
                    notification.save()

                    # Get a dict in the format we want
                    dict_sub = {
                        "endpoint": subscription.endpoint,
                        "keys":{
                            "p256dh": subscription.p256dh,
                            "auth": subscription.auth
                        }
                    }

                    # Make the payload
                    payload = {
                        "notification": {
                            "title": notification.actor.name,
                            "body": notification.verb,
                            "icon": "assets/logo-sq-sm.png",
                            "vibrate": [100, 50, 100],
                            "data": {
                                "primaryKey": 1
                            }
                        }
                    }

                    try:
                        # Try to send
                        send_push(dict_sub, payload)
                        sent += 1
                    except WebPushException:
                        # Remove subscription
                        failed += 1
                        subscription.delete()

        print("Sent:", sent, "Failed:", failed)
