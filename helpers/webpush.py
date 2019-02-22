"""Helpers for web push notifications."""
import json
from pywebpush import webpush, WebPushException
from django.conf import settings

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

def send_notification_webpush(subscription, data_message):
    """Attempt to send a data_message to a subscription."""
    # Get a dict in the format we want
    dict_sub = {
        "endpoint": subscription.endpoint,
        "keys": {
            "p256dh": subscription.p256dh,
            "auth": subscription.auth
        }
    }

    # Make the payload
    payload = {
        "notification": {
            "title": data_message['title'],
            "body": data_message['verb'],
            "icon": data_message.get('large_icon', settings.NOTIFICATION_LARGE_ICON_DEFAULT),
            "image": data_message.get('image_url', None),
            "badge": settings.NOTIFICATION_LARGE_ICON_DEFAULT,
            "vibrate": [100, 50, 100],
            "data": data_message
        }
    }

    try:
        # Try to send
        send_push(dict_sub, payload)
        return 1
    except WebPushException:
        # Remove subscription
        subscription.delete()

    return 0
