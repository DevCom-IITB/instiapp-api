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

def get_news_image(news):
    if 'yt:video' in news.guid:
        return 'https://img.youtube.com/vi/' + news.guid.split('video:')[1] + '/maxresdefault.jpg'
    return None

class Command(BaseCommand):
    help = 'Sends push notifications'

    def handle(self, *args, **options):
        """Send Push notifications."""

        sent = 0
        failed = 0
        fcm = 0
        badfcm = 0
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

            # Get title
            title = "InstiApp"

            # Default values
            notification_type = None
            notification_id = None
            notification_extra = None

            # Rich fields
            is_rich = False
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
                        notification_large_icon = bodies[0].image_url

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
                is_rich = True
                data_message['large_icon'] = notification_large_icon
            if notification_large_content is not None:
                is_rich = True
                data_message['large_content'] = notification_large_content
            if notification_image is not None:
                is_rich = True
                data_message['image_url'] = notification_image

            # Send FCM push notification
            try:
                registration_id = profile.fcm_id
                message_title = title
                message_body = notification.verb

                # Check if the user supports rich notifications
                if is_rich and profile.android_version >= 17:
                    push_service.notify_single_device(
                        registration_id=registration_id, data_message=data_message)
                else:
                    push_service.notify_single_device(
                        registration_id=registration_id, message_title=message_title,
                        message_body=message_body, data_message=data_message, sound='default')

                fcm += 1
            except Exception as ex:
                print(profile.name, ex)
                badfcm += 1

            # For each web push subscription
            for subscription in profile.web_push_subscriptions.all():

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
                        "title": title,
                        "body": notification.verb,
                        "icon": "assets/logo-sq-sm.png",
                        "vibrate": [100, 50, 100],
                        "data": data_message
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

        print("WebPush:", sent, "WebPush FAIL:", failed, "FCM", fcm, "FCM FAIL:", badfcm)
        self.stdout.write(self.style.SUCCESS('Push notification chore completed successfully'))
