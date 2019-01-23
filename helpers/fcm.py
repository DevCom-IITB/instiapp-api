"""Helpers for FCM notifications."""
from bs4 import BeautifulSoup
from placements.models import BlogEntry
from events.models import Event
from news.models import NewsEntry
from venter.models import Comment
from helpers.device import fill_device_firebase

def send_fcm_data_message(push_service, registration_id, data_message):
    """Send a data FCM message."""
    push_service.notify_single_device(
        registration_id=registration_id, data_message=data_message)

def send_fcm_notification_message(push_service, registration_id, data_message):
    """Send a notification FCM message."""
    push_service.notify_single_device(
        registration_id=registration_id, message_title=data_message['title'],
        message_body=data_message['verb'], data_message=data_message, sound='default')

def send_notification_fcm(push_service, device, data_message):
    """Attempt to send a single FCM notification."""

    try:
        registration_id = device.fcm_id

        # Fill/check for invalid device
        if not fill_device_firebase(push_service, device):
            device.delete()
            return 0

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

        # Comment
        if isinstance(actor, Comment):
            title = actor.complaint.description
            notification_extra = actor.complaint.id

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
