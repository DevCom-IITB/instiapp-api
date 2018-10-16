"""Chore to send push notifications."""
import json
from django.core.management.base import BaseCommand
from django.conf import settings
from bs4 import BeautifulSoup
from pywebpush import webpush, WebPushException
from pyfcm import FCMNotification
from notifications.models import Notification
from placements.models import BlogEntry
from events.models import Event
from news.models import NewsEntry

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
            "icon": "assets/logo-sq-sm.png",
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

def send_notification_fcm(push_service, profile, data_message):
    """Attempt to send a single FCM notification."""

    try:
        registration_id = profile.fcm_id

        # Check if the user supports rich notifications
        if profile.android_version >= 17:
            push_service.notify_single_device(
                registration_id=registration_id, data_message=data_message)
        else:
            push_service.notify_single_device(
                registration_id=registration_id, message_title=data_message['title'],
                message_body=data_message['verb'], data_message=data_message, sound='default')

        return 1

    except Exception as ex:  # pylint: disable=W0703
        print(profile.name, ex)

    return 0

def get_news_image(news):
    if 'yt:video' in news.guid:
        return 'https://img.youtube.com/vi/' + news.guid.split('video:')[1] + '/maxresdefault.jpg'
    return None

def get_rich_notification(notification):
    # Get title
    title = "InstiApp"

    # Default values
    notification_type = None
    notification_id = None
    notification_extra = None

    # Rich fields
    notification_large_icon = None
    notification_large_content = None
    notification_image = None

    # Get information about actor
    actor = notification.actor
    if actor is not None:
        # Infer notification type from actor class
        notification_type = actor.__class__.__name__.lower()

        # Event
        if isinstance(actor, Event):
            title = actor.name
            # Rich notifications
            bodies = actor.bodies.all()
            if bodies.exists():
                notification_large_icon = bodies.first().image_url

        # News/Blog Entry
        if isinstance(actor, (BlogEntry, NewsEntry)):
            title = actor.title
            notification_extra = actor.link

        # Rich field for news entry
        if isinstance(actor, NewsEntry):
            notification_large_icon = actor.body.image_url
            notification_large_content = BeautifulSoup(actor.content, features='html5lib').text
            if len(notification_large_content) > 250:
                notification_large_content = notification_large_content[:250] + ' ...'
            notification_image = get_news_image(actor)

        notification_id = str(actor.id)

    # Construct the data message
    data_message = {
        "type": notification_type,
        "id": notification_id,
        "extra": notification_extra,
        "notification_id": str(notification.id),
        "title": title,
        "verb": notification.verb
    }

    # Set rich fields if present
    if notification_large_icon is not None:
        data_message['large_icon'] = notification_large_icon
    if notification_large_content is not None:
        data_message['large_content'] = notification_large_content
    if notification_image is not None:
        data_message['image_url'] = notification_image

    return data_message


class Command(BaseCommand):
    help = 'Sends push notifications'

    def handle(self, *args, **options):  # noqa: C901
        """Send Push notifications."""

        webpush_sent = 0
        webpush_total = 0
        fcm_sent = 0

        push_service = FCMNotification(api_key=settings.FCM_SERVER_KEY)

        # Iterate all unsent notifications
        for notification in Notification.objects.prefetch_related(
                'recipient', 'recipient__profile').filter(emailed=False):

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

            # Send FCM push notification
            fcm_sent += send_notification_fcm(push_service, profile, data_message)

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
