"""Helpers for FCM notifications."""
from bs4 import BeautifulSoup
from django.conf import settings
from placements.models import BlogEntry
from events.models import Event
from news.models import NewsEntry
from venter.models import ComplaintComment
from helpers.device import fill_device_firebase
from other.views import get_notif_queryset

def send_fcm_data_message(push_service, registration_id, data_message):
    """Send a data FCM message."""
    push_service.notify_single_device(
        registration_id=registration_id, data_message=data_message)

def send_fcm_notification_message(push_service, registration_id, data_message):
    """Send a notification FCM message."""
    push_service.notify_single_device(
        registration_id=registration_id, message_title=data_message['title'],
        message_body=data_message['verb'], data_message=data_message,
        click_action=data_message.get('click_action', None), sound='default')

def send_notification_fcm(push_service, device, data_message):
    """Attempt to send a single FCM notification."""

    try:
        registration_id = device.fcm_id

        # Fill/check for invalid device
        if device.needs_refresh() and not fill_device_firebase(push_service, device):
            device.delete()
            return 0

        # Process the message for device specific things
        data_message = device.process_rich(data_message)

        # Check if the user supports rich notifications
        push_method = None
        if device.supports_rich():
            push_method = send_fcm_data_message
        else:
            push_method = send_fcm_notification_message

        # Push the notification
        push_method(push_service, registration_id, data_message)
        return 1

    except Exception as ex:  # pylint: disable=W0703
        print(device.user.name, ex)

    return 0

def get_news_image(news):
    if 'yt:video' in news.guid:
        return settings.YOUTUBE_THUMB(news.guid.split('video:')[1])
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
            notification_large_content = BeautifulSoup(actor.content, features='html5lib').text
            notification_image = get_news_image(actor)

        # ComplaintComment
        if isinstance(actor, ComplaintComment):
            title = actor.complaint.description
            notification_large_content = actor.text
            notification_extra = str(actor.complaint.id)

        notification_id = str(actor.id)

    # Construct the data message
    data_message = {
        "type": notification_type,
        "id": notification_id,
        "extra": notification_extra,
        "notification_id": str(notification.id),
        "title": truncated(title, 60),
        "verb": notification.verb,
        "total_count": get_notif_queryset(
            notification.recipient.notifications).count()
    }

    # Set rich fields if present
    if notification_large_icon is not None:
        data_message['large_icon'] = settings.NOTIFICATION_LARGE_ICON_TRANSFORM(notification_large_icon)
    if notification_large_content is not None:
        data_message['large_content'] = truncated(notification_large_content, 250)
    if notification_image is not None:
        data_message['image_url'] = settings.NOTIFICATION_IMAGE_TRANSFORM(notification_image)

    return data_message

def truncated(val, max_len):
    if val and len(val) > max_len - 4:
        return val[:max_len] + ' ...'
    return val
