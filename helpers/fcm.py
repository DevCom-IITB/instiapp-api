"""Helpers for FCM notifications."""
from bs4 import BeautifulSoup
from django.conf import settings
from placements.models import BlogEntry
from events.models import Event
from news.models import NewsEntry
from venter.models import ComplaintComment
from querybot.models import UnresolvedQuery
from other.views import get_notif_queryset

try:
    from firebase_admin import messaging
except ImportError:
    messaging = None


def _stringify_data_message(data_message):
    """Convert FCM data payload values to strings as required by Firebase."""
    return {key: "" if value is None else str(value) for key, value in data_message.items()}


def _build_message_for_token(registration_id, data_message, notification, android_config):
    """Build a Firebase Admin Message object."""
    return messaging.Message(
        token=registration_id,
        data=data_message,
        notification=notification,
        android=android_config,
    )


def send_notification_fcm(push_service, device, data_message):
    """Attempt to send a single FCM notification using Firebase Admin SDK."""
    if messaging is None:
        return 0

    try:
        registration_id = device.fcm_id

        # Process the message for device specific things
        processed_message = device.process_rich(data_message)
        processed_message = _stringify_data_message(processed_message)

        # Build notification object
        notification = messaging.Notification(
            title=processed_message.get("title"),
            body=processed_message.get("verb"),
        )

        # Build Android config
        android_config = messaging.AndroidConfig(
            priority="high",
            notification=messaging.AndroidNotification(
                title=processed_message.get("title"),
                body=processed_message.get("verb"),
                sound="default",
            ),
        )

        # Build and send message
        msg = _build_message_for_token(
            registration_id, processed_message, notification, android_config
        )
        resp = messaging.send(msg)
        print(f"FCM send start: {device.user.name}")
        print(f"FCM send result: {{'result': '{resp}'}}")
        return 1 if resp else 0

    except Exception as ex:  # pylint: disable=W0703
        print(f"FCM send failed for {device.user.name}: {ex}")

    return 0


def get_news_image(news):
    if "yt:video" in news.guid:
        return settings.YOUTUBE_THUMB(news.guid.split("video:")[1])
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
            notification_image = actor.image_url if actor.image_url else None
            body = actor.bodies.first()
            if body:
                notification_large_icon = body.image_url

        # News/Blog Entry
        if isinstance(actor, (BlogEntry, NewsEntry)):
            title = actor.title
            notification_extra = actor.link

        # Rich field for news entry
        if isinstance(actor, NewsEntry):
            notification_large_icon = actor.body.image_url
            notification_large_content = BeautifulSoup(
                actor.content, features="html5lib"
            ).text
            notification_image = get_news_image(actor)

        # ComplaintComment
        if isinstance(actor, ComplaintComment):
            title = actor.complaint.description
            notification_large_content = actor.text
            notification_extra = str(actor.complaint.id)

        # UnresolvedQuery
        if isinstance(actor, UnresolvedQuery):
            title = actor.question

        notification_id = str(actor.id)

    # Construct the data message
    data_message = {
        "type": notification_type,
        "id": notification_id,
        "extra": notification_extra,
        "notification_id": str(notification.id),
        "title": truncated(title, 60),
        "verb": notification.verb,
        "total_count": get_notif_queryset(notification.recipient.notifications).count(),
    }

    # Set rich fields if present
    if notification_large_icon is not None:
        data_message["large_icon"] = settings.NOTIFICATION_LARGE_ICON_TRANSFORM(
            notification_large_icon
        )
    if notification_large_content is not None:
        data_message["large_content"] = truncated(notification_large_content, 250)
    if notification_image is not None:
        data_message["image_url"] = settings.NOTIFICATION_IMAGE_TRANSFORM(
            notification_image
        )

    return data_message


def truncated(val, max_len):
    if val and len(val) > max_len - 4:
        return val[:max_len] + " ..."
    return val
